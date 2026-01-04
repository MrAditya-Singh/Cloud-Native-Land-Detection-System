"""Main data ingestion manager orchestrating all components."""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .config import Config
from .providers.sentinel2 import Sentinel2Provider
from .providers.landsat import LandsatProvider
from .providers.commercial import create_commercial_provider
from .storage.s3_storage import S3Storage
from .schedulers.cron_scheduler import CronScheduler
from .schedulers.eventbridge_scheduler import EventBridgeScheduler

logger = logging.getLogger(__name__)


class IngestionManager:
    """
    Main manager for satellite data ingestion.
    
    Coordinates data providers, storage, and scheduling for automated
    satellite data downloads.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ingestion manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = Config(config_path)
        
        # Initialize providers
        self.providers = {}
        self._init_phase1_providers()
        self._init_phase2_providers()
        
        # Initialize storage
        self.storage = None
        if self.config.get('aws.s3.enabled'):
            self._init_storage()
        
        # Initialize scheduler
        self.scheduler = None
        
        logger.info("Ingestion manager initialized")
    
    def _init_phase1_providers(self):
        """Initialize Phase 1 (free) data providers."""
        phase1_config = self.config.phase1_config
        
        # Sentinel-2
        if phase1_config.get('sentinel2', {}).get('enabled'):
            sentinel_username = self.config.get_env('SENTINEL_USERNAME')
            sentinel_password = self.config.get_env('SENTINEL_PASSWORD')
            
            self.providers['sentinel2'] = Sentinel2Provider(
                phase1_config['sentinel2'],
                username=sentinel_username if sentinel_username else None,
                password=sentinel_password if sentinel_password else None
            )
            logger.info("Sentinel-2 provider initialized")
        
        # Landsat
        if phase1_config.get('landsat', {}).get('enabled'):
            landsat_username = self.config.get_env('LANDSAT_USERNAME')
            landsat_password = self.config.get_env('LANDSAT_PASSWORD')
            
            self.providers['landsat'] = LandsatProvider(
                phase1_config['landsat'],
                username=landsat_username if landsat_username else None,
                password=landsat_password if landsat_password else None
            )
            logger.info("Landsat provider initialized")
    
    def _init_phase2_providers(self):
        """Initialize Phase 2 (commercial) data providers."""
        phase2_config = self.config.phase2_config
        
        if not phase2_config.get('commercial_providers', {}).get('enabled'):
            return
        
        for provider_config in phase2_config['commercial_providers'].get('providers', []):
            if not provider_config.get('enabled'):
                continue
            
            provider_name = provider_config['name']
            api_key_env = provider_config.get('api_key_env')
            api_key = self.config.get_env(api_key_env) if api_key_env else None
            
            provider = create_commercial_provider(
                provider_name,
                provider_config,
                api_key
            )
            
            self.providers[provider_name] = provider
            logger.info(f"Commercial provider '{provider_name}' initialized")
    
    def _init_storage(self):
        """Initialize S3 storage."""
        s3_config = self.config.s3_config
        
        self.storage = S3Storage(
            bucket_name=s3_config.get('bucket_name', 'land-detection-satellite-data'),
            region=s3_config.get('region', 'us-east-1'),
            aws_access_key_id=self.config.get_env('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=self.config.get_env('AWS_SECRET_ACCESS_KEY')
        )
        
        # Ensure bucket exists
        self.storage.ensure_bucket_exists()
        logger.info("S3 storage initialized")
    
    def search_and_download(
        self,
        aoi: Dict[str, Any],
        start_date: datetime,
        end_date: datetime,
        sources: Optional[List[str]] = None,
        max_cloud_coverage: float = 20,
        aoi_id: str = "default",
        upload_to_s3: bool = True
    ) -> Dict[str, List[str]]:
        """
        Search and download satellite data from configured sources.
        
        Args:
            aoi: Area of Interest as GeoJSON geometry
            start_date: Start date for search
            end_date: End date for search
            sources: List of data sources to use (None = all enabled)
            max_cloud_coverage: Maximum cloud coverage percentage
            aoi_id: Area of Interest identifier for storage organization
            upload_to_s3: Whether to upload downloaded files to S3
            
        Returns:
            Dictionary mapping source names to lists of downloaded file paths
        """
        if sources is None:
            sources = list(self.providers.keys())
        
        results = {}
        
        for source in sources:
            if source not in self.providers:
                logger.warning(f"Provider '{source}' not available")
                continue
            
            provider = self.providers[source]
            logger.info(f"Searching {source} data...")
            
            try:
                # Search for products
                products = provider.search(
                    aoi=aoi,
                    start_date=start_date,
                    end_date=end_date,
                    max_cloud_coverage=max_cloud_coverage
                )
                
                logger.info(f"Found {len(products)} products from {source}")
                
                # Download products
                downloaded_files = []
                download_path = self.config.get(
                    f'data_ingestion.phase1.{source}.download_path',
                    f'data/{source}'
                )
                
                for product in products[:5]:  # Limit to 5 products for demo
                    try:
                        file_path = provider.download(
                            product,
                            download_path
                        )
                        downloaded_files.append(file_path)
                        
                        # Upload to S3 if enabled
                        if upload_to_s3 and self.storage:
                            self.storage.upload_file(
                                local_path=file_path,
                                aoi_id=aoi_id,
                                source=source,
                                acquisition_date=product.acquisition_date,
                                metadata={
                                    'product_id': product.product_id,
                                    'cloud_coverage': str(product.cloud_coverage)
                                }
                            )
                    
                    except Exception as e:
                        logger.error(f"Error downloading product {product.product_id}: {e}")
                        continue
                
                results[source] = downloaded_files
                
            except Exception as e:
                logger.error(f"Error processing {source}: {e}")
                results[source] = []
        
        return results
    
    def setup_automated_ingestion(
        self,
        aoi: Dict[str, Any],
        aoi_id: str,
        method: str = "cron",
        schedule: str = "0 2 * * *"
    ):
        """
        Set up automated data ingestion.
        
        Args:
            aoi: Area of Interest as GeoJSON geometry
            aoi_id: Area of Interest identifier
            method: Scheduling method ("cron" or "eventbridge")
            schedule: Schedule expression (cron format or EventBridge expression)
        """
        if method == "cron":
            self.scheduler = CronScheduler()
            
            # Define ingestion task
            def ingestion_task():
                from datetime import timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
                
                self.search_and_download(
                    aoi=aoi,
                    start_date=start_date,
                    end_date=end_date,
                    aoi_id=aoi_id
                )
            
            # Schedule the task
            self.scheduler.schedule_from_cron(
                task=ingestion_task,
                cron_expr=schedule,
                task_name=f"ingestion_{aoi_id}"
            )
            
            logger.info(f"Automated ingestion configured with cron: {schedule}")
            
        elif method == "eventbridge":
            self.scheduler = EventBridgeScheduler(
                region=self.config.get('aws.region', 'us-east-1')
            )
            
            rule_name = f"land-detection-ingestion-{aoi_id}"
            
            # Create EventBridge rule
            self.scheduler.create_schedule_rule(
                rule_name=rule_name,
                schedule_expression=schedule,
                description=f"Automated ingestion for AOI {aoi_id}"
            )
            
            logger.info(f"EventBridge rule created: {rule_name}")
            
        else:
            raise ValueError(f"Unknown scheduling method: {method}")
    
    def get_storage_stats(self, aoi_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Args:
            aoi_id: Optional AOI ID to filter statistics
            
        Returns:
            Storage statistics
        """
        if not self.storage:
            return {"error": "S3 storage not initialized"}
        
        return self.storage.get_storage_stats(aoi_id)

"""Landsat-8/9 data provider implementation."""

import logging
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer

from .base import DataProvider, SatelliteProduct

logger = logging.getLogger(__name__)


class LandsatProvider(DataProvider):
    """Provider for Landsat-8 and Landsat-9 historical data."""
    
    DATASETS = {
        'landsat-8': 'landsat_ot_c2_l2',
        'landsat-9': 'landsat_ot_c2_l2'
    }
    
    def __init__(self, config: Dict[str, Any], username: str = None, password: str = None):
        """
        Initialize Landsat provider.
        
        Args:
            config: Provider configuration
            username: USGS EarthExplorer username (or set LANDSAT_USERNAME env var)
            password: USGS EarthExplorer password (or set LANDSAT_PASSWORD env var)
        """
        super().__init__(config)
        self.username = username
        self.password = password
        self.api = None
        self.ee = None
        
        if username and password:
            self._init_api()
    
    def _init_api(self):
        """Initialize Landsat API connection."""
        try:
            self.api = API(self.username, self.password)
            self.ee = EarthExplorer(self.username, self.password)
            logger.info("Landsat API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Landsat API: {e}")
            raise
    
    def search(
        self,
        aoi: Dict[str, Any],
        start_date: datetime,
        end_date: datetime,
        max_cloud_coverage: float = 20,
        **kwargs
    ) -> List[SatelliteProduct]:
        """
        Search for Landsat products.
        
        Args:
            aoi: Area of Interest as GeoJSON geometry
            start_date: Start date for search
            end_date: End date for search
            max_cloud_coverage: Maximum cloud coverage percentage
            **kwargs: Additional parameters (dataset, missions, etc.)
            
        Returns:
            List of Landsat products
        """
        if not self.api:
            logger.warning("Landsat API not initialized. Call with credentials first.")
            return []
        
        if not self.validate_aoi(aoi):
            raise ValueError("Invalid AOI geometry")
        
        # Get bounding box from AOI
        bbox = self._get_bbox(aoi)
        
        # Get missions to search
        missions = kwargs.get('missions', self.config.get('missions', ['landsat-8', 'landsat-9']))
        
        satellite_products = []
        
        for mission in missions:
            dataset = self.DATASETS.get(mission, 'landsat_ot_c2_l2')
            
            try:
                # Search for scenes
                scenes = self.api.search(
                    dataset=dataset,
                    latitude=bbox['center_lat'],
                    longitude=bbox['center_lon'],
                    bbox=bbox['bbox'],
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    max_cloud_cover=max_cloud_coverage,
                    max_results=kwargs.get('max_results', 100)
                )
                
                # Convert to SatelliteProduct objects
                for scene in scenes:
                    satellite_products.append(
                        SatelliteProduct(
                            product_id=scene['entity_id'],
                            source=f'Landsat-{mission.split("-")[1]}',
                            acquisition_date=datetime.strptime(
                                scene['acquisition_date'], '%Y-%m-%d'
                            ),
                            cloud_coverage=scene.get('cloud_cover', 0),
                            geometry=aoi,
                            metadata=scene,
                            download_url=scene.get('download_url')
                        )
                    )
                
                logger.info(f"Found {len(scenes)} {mission} products")
                
            except Exception as e:
                logger.error(f"Error searching {mission} products: {e}")
                continue
        
        return satellite_products
    
    def download(
        self,
        product: SatelliteProduct,
        output_path: str,
        **kwargs
    ) -> str:
        """
        Download a Landsat product.
        
        Args:
            product: Satellite product to download
            output_path: Local directory to save the product
            **kwargs: Additional download parameters
            
        Returns:
            Path to downloaded file
        """
        if not self.ee:
            raise RuntimeError("Landsat EarthExplorer not initialized")
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Download the product
            file_path = self.ee.download(
                product.product_id,
                output_dir=str(output_dir),
                timeout=kwargs.get('timeout', 300)
            )
            
            logger.info(f"Downloaded Landsat product: {product.product_id}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading Landsat product {product.product_id}: {e}")
            raise
    
    def _get_bbox(self, geojson: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get bounding box from GeoJSON geometry.
        
        Args:
            geojson: GeoJSON geometry
            
        Returns:
            Dictionary with bbox coordinates and center point
        """
        from shapely.geometry import shape
        
        geometry = shape(geojson)
        bounds = geometry.bounds  # (minx, miny, maxx, maxy)
        
        return {
            'bbox': bounds,
            'center_lat': (bounds[1] + bounds[3]) / 2,
            'center_lon': (bounds[0] + bounds[2]) / 2
        }
    
    def __del__(self):
        """Cleanup API connections."""
        if self.api:
            try:
                self.api.logout()
            except:
                pass
        if self.ee:
            try:
                self.ee.logout()
            except:
                pass

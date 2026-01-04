"""Sentinel-2 data provider implementation."""

import logging
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

from sentinelsat import SentinelAPI, geojson_to_wkt, read_geojson

from .base import DataProvider, SatelliteProduct

logger = logging.getLogger(__name__)


class Sentinel2Provider(DataProvider):
    """Provider for Sentinel-2 satellite data (10m multispectral)."""
    
    def __init__(self, config: Dict[str, Any], username: str = None, password: str = None):
        """
        Initialize Sentinel-2 provider.
        
        Args:
            config: Provider configuration
            username: Copernicus Hub username (or set SENTINEL_USERNAME env var)
            password: Copernicus Hub password (or set SENTINEL_PASSWORD env var)
        """
        super().__init__(config)
        self.username = username
        self.password = password
        self.api = None
        
        if username and password:
            self._init_api()
    
    def _init_api(self):
        """Initialize Sentinel API connection."""
        try:
            self.api = SentinelAPI(
                self.username,
                self.password,
                'https://apihub.copernicus.eu/apihub'
            )
            logger.info("Sentinel-2 API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Sentinel-2 API: {e}")
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
        Search for Sentinel-2 products.
        
        Args:
            aoi: Area of Interest as GeoJSON geometry
            start_date: Start date for search
            end_date: End date for search
            max_cloud_coverage: Maximum cloud coverage percentage
            **kwargs: Additional parameters (platformname, producttype, etc.)
            
        Returns:
            List of Sentinel-2 products
        """
        if not self.api:
            logger.warning("Sentinel-2 API not initialized. Call with credentials first.")
            return []
        
        if not self.validate_aoi(aoi):
            raise ValueError("Invalid AOI geometry")
        
        # Convert GeoJSON to WKT
        footprint = self._geojson_to_wkt(aoi)
        
        # Search parameters
        search_params = {
            'platformname': kwargs.get('platformname', 'Sentinel-2'),
            'producttype': kwargs.get('producttype', 'S2MSI2A'),
            'cloudcoverpercentage': (0, max_cloud_coverage),
            'date': (start_date, end_date)
        }
        
        try:
            # Query Sentinel Hub
            products = self.api.query(footprint, **search_params)
            
            # Convert to SatelliteProduct objects
            satellite_products = []
            for product_id, product_info in products.items():
                satellite_products.append(
                    SatelliteProduct(
                        product_id=product_id,
                        source='Sentinel-2',
                        acquisition_date=product_info['beginposition'],
                        cloud_coverage=product_info.get('cloudcoverpercentage', 0),
                        geometry=aoi,
                        metadata=product_info,
                        file_size_mb=product_info.get('size', 0)
                    )
                )
            
            logger.info(f"Found {len(satellite_products)} Sentinel-2 products")
            return satellite_products
            
        except Exception as e:
            logger.error(f"Error searching Sentinel-2 products: {e}")
            return []
    
    def download(
        self,
        product: SatelliteProduct,
        output_path: str,
        **kwargs
    ) -> str:
        """
        Download a Sentinel-2 product.
        
        Args:
            product: Satellite product to download
            output_path: Local directory to save the product
            **kwargs: Additional download parameters
            
        Returns:
            Path to downloaded file
        """
        if not self.api:
            raise RuntimeError("Sentinel-2 API not initialized")
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Download the product
            download_info = self.api.download(
                product.product_id,
                directory_path=str(output_dir),
                checksum=kwargs.get('checksum', True)
            )
            
            logger.info(f"Downloaded Sentinel-2 product: {product.product_id}")
            return download_info['path']
            
        except Exception as e:
            logger.error(f"Error downloading Sentinel-2 product {product.product_id}: {e}")
            raise
    
    def _geojson_to_wkt(self, geojson: Dict[str, Any]) -> str:
        """
        Convert GeoJSON geometry to WKT format.
        
        Args:
            geojson: GeoJSON geometry
            
        Returns:
            WKT string
        """
        from shapely.geometry import shape
        geometry = shape(geojson)
        return geometry.wkt

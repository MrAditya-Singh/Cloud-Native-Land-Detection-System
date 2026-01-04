"""Base provider interface for satellite data sources."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SatelliteProduct:
    """Represents a satellite data product."""
    
    product_id: str
    source: str
    acquisition_date: datetime
    cloud_coverage: float
    geometry: Dict[str, Any]  # GeoJSON geometry
    metadata: Dict[str, Any]
    download_url: Optional[str] = None
    file_size_mb: Optional[float] = None


class DataProvider(ABC):
    """Abstract base class for satellite data providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize data provider.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def search(
        self,
        aoi: Dict[str, Any],
        start_date: datetime,
        end_date: datetime,
        max_cloud_coverage: float = 20,
        **kwargs
    ) -> List[SatelliteProduct]:
        """
        Search for satellite products.
        
        Args:
            aoi: Area of Interest as GeoJSON geometry
            start_date: Start date for search
            end_date: End date for search
            max_cloud_coverage: Maximum cloud coverage percentage
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of satellite products
        """
        pass
    
    @abstractmethod
    def download(
        self,
        product: SatelliteProduct,
        output_path: str,
        **kwargs
    ) -> str:
        """
        Download a satellite product.
        
        Args:
            product: Satellite product to download
            output_path: Local path to save the product
            **kwargs: Additional download parameters
            
        Returns:
            Path to downloaded file
        """
        pass
    
    def validate_aoi(self, aoi: Dict[str, Any]) -> bool:
        """
        Validate Area of Interest geometry.
        
        Args:
            aoi: GeoJSON geometry
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ['type', 'coordinates']
        return all(key in aoi for key in required_keys)

"""Tests for base provider functionality."""

import pytest
from datetime import datetime

from data_ingestion.providers.base import DataProvider, SatelliteProduct


class MockProvider(DataProvider):
    """Mock provider for testing."""
    
    def search(self, aoi, start_date, end_date, max_cloud_coverage=20, **kwargs):
        return []
    
    def download(self, product, output_path, **kwargs):
        return output_path


def test_satellite_product_creation():
    """Test SatelliteProduct dataclass."""
    product = SatelliteProduct(
        product_id='TEST-001',
        source='test-source',
        acquisition_date=datetime(2024, 1, 1),
        cloud_coverage=15.5,
        geometry={'type': 'Polygon', 'coordinates': []},
        metadata={'key': 'value'}
    )
    
    assert product.product_id == 'TEST-001'
    assert product.source == 'test-source'
    assert product.cloud_coverage == 15.5


def test_provider_initialization():
    """Test provider initialization."""
    config = {'test': 'config'}
    provider = MockProvider(config)
    
    assert provider.config == config
    assert provider.name == 'MockProvider'


def test_validate_aoi():
    """Test AOI validation."""
    provider = MockProvider({})
    
    # Valid AOI
    valid_aoi = {
        'type': 'Polygon',
        'coordinates': [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
    }
    assert provider.validate_aoi(valid_aoi) is True
    
    # Invalid AOI (missing required keys)
    invalid_aoi = {'coordinates': []}
    assert provider.validate_aoi(invalid_aoi) is False

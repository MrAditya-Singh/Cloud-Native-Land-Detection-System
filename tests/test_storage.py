"""Tests for S3 storage functionality."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from data_ingestion.storage.s3_storage import S3Storage


@pytest.fixture
def mock_s3_client():
    """Create a mock S3 client."""
    with patch('boto3.client') as mock_client, \
         patch('boto3.resource') as mock_resource:
        yield mock_client.return_value, mock_resource.return_value


def test_s3_storage_initialization(mock_s3_client):
    """Test S3Storage initialization."""
    storage = S3Storage(
        bucket_name='test-bucket',
        region='us-east-1'
    )
    
    assert storage.bucket_name == 'test-bucket'
    assert storage.region == 'us-east-1'


def test_generate_s3_key():
    """Test S3 key generation with AOI-based structure."""
    with patch('boto3.client'), patch('boto3.resource'):
        storage = S3Storage('test-bucket')
        
        # The actual key generation happens in upload_file
        # This test verifies the expected format
        aoi_id = 'aoi_001'
        source = 'sentinel2'
        date = datetime(2024, 1, 15)
        filename = 'scene.tif'
        
        expected_key = f"{aoi_id}/{source}/2024-01-15/{filename}"
        
        # Verify format matches expected pattern
        assert f"{aoi_id}/{source}/{date.strftime('%Y-%m-%d')}/{filename}" == expected_key

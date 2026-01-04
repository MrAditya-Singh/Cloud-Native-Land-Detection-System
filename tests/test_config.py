"""Tests for configuration management."""

import pytest
import tempfile
from pathlib import Path
import yaml

from data_ingestion.config import Config


def test_config_loading():
    """Test configuration file loading."""
    # Create a temporary config file
    config_data = {
        'aws': {
            's3': {
                'bucket_name': 'test-bucket',
                'region': 'us-west-2'
            }
        },
        'data_ingestion': {
            'phase1': {
                'sentinel2': {
                    'enabled': True,
                    'resolution': '10m'
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        config = Config(config_path)
        
        # Test dot notation access
        assert config.get('aws.s3.bucket_name') == 'test-bucket'
        assert config.get('aws.s3.region') == 'us-west-2'
        assert config.get('data_ingestion.phase1.sentinel2.enabled') is True
        
        # Test default values
        assert config.get('nonexistent.key', 'default') == 'default'
        
        # Test property methods
        assert config.s3_config['bucket_name'] == 'test-bucket'
        
    finally:
        Path(config_path).unlink()


def test_config_properties():
    """Test configuration property accessors."""
    config_data = {
        'aws': {
            's3': {'bucket_name': 'test'},
            'region': 'us-east-1'
        },
        'data_ingestion': {
            'phase1': {'sentinel2': {'enabled': True}},
            'phase2': {'commercial_providers': {'enabled': False}}
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        config = Config(config_path)
        
        assert 's3' in config.aws_config
        assert config.s3_config['bucket_name'] == 'test'
        assert config.phase1_config['sentinel2']['enabled'] is True
        assert config.phase2_config['commercial_providers']['enabled'] is False
        
    finally:
        Path(config_path).unlink()

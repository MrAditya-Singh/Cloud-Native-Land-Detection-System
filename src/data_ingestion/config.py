"""Configuration management for data ingestion system."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """Configuration loader and manager."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration YAML file
        """
        # Load environment variables
        load_dotenv()
        
        # Set default config path if not provided
        if config_path is None:
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "data_ingestion.yaml"
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to config value (e.g., 'aws.s3.bucket_name')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_env(self, key: str, default: str = "") -> str:
        """
        Get environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)
    
    @property
    def aws_config(self) -> Dict[str, Any]:
        """Get AWS configuration."""
        return self.get('aws', {})
    
    @property
    def s3_config(self) -> Dict[str, Any]:
        """Get S3 configuration."""
        return self.get('aws.s3', {})
    
    @property
    def phase1_config(self) -> Dict[str, Any]:
        """Get Phase 1 data source configuration."""
        return self.get('data_ingestion.phase1', {})
    
    @property
    def phase2_config(self) -> Dict[str, Any]:
        """Get Phase 2 data source configuration."""
        return self.get('data_ingestion.phase2', {})

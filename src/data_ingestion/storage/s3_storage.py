"""Amazon S3 storage module for AOI-based satellite data storage."""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class S3Storage:
    """
    Amazon S3 storage manager with AOI-based organization.
    
    Storage structure: s3://{bucket}/{aoi_id}/{source}/{date}/
    Example: s3://land-detection-data/aoi_001/sentinel2/2024-01-01/scene.tif
    """
    
    def __init__(
        self,
        bucket_name: str,
        region: str = 'us-east-1',
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        """
        Initialize S3 storage.
        
        Args:
            bucket_name: S3 bucket name
            region: AWS region
            aws_access_key_id: AWS access key (optional, uses env/IAM if not provided)
            aws_secret_access_key: AWS secret key (optional, uses env/IAM if not provided)
        """
        self.bucket_name = bucket_name
        self.region = region
        
        # Initialize S3 client
        session_kwargs = {'region_name': region}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs.update({
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key
            })
        
        self.s3_client = boto3.client('s3', **session_kwargs)
        self.s3_resource = boto3.resource('s3', **session_kwargs)
        
        logger.info(f"S3 storage initialized for bucket: {bucket_name}")
    
    def upload_file(
        self,
        local_path: str,
        aoi_id: str,
        source: str,
        acquisition_date: datetime,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a file to S3 with AOI-based organization.
        
        Args:
            local_path: Path to local file
            aoi_id: Area of Interest identifier
            source: Data source (sentinel2, landsat, etc.)
            acquisition_date: Date of data acquisition
            metadata: Optional metadata to attach to the object
            
        Returns:
            S3 URI of the uploaded file
        """
        local_file = Path(local_path)
        if not local_file.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")
        
        # Generate S3 key using AOI-based structure
        date_str = acquisition_date.strftime('%Y-%m-%d')
        s3_key = f"{aoi_id}/{source}/{date_str}/{local_file.name}"
        
        try:
            # Prepare upload arguments
            upload_args = {}
            if metadata:
                upload_args['Metadata'] = {
                    k: str(v) for k, v in metadata.items()
                }
            
            # Upload file
            self.s3_client.upload_file(
                str(local_file),
                self.bucket_name,
                s3_key,
                ExtraArgs=upload_args
            )
            
            s3_uri = f"s3://{self.bucket_name}/{s3_key}"
            logger.info(f"Uploaded file to S3: {s3_uri}")
            return s3_uri
            
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
    
    def download_file(
        self,
        s3_key: str,
        local_path: str
    ) -> str:
        """
        Download a file from S3.
        
        Args:
            s3_key: S3 object key
            local_path: Local path to save the file
            
        Returns:
            Path to downloaded file
        """
        local_file = Path(local_path)
        local_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            self.s3_client.download_file(
                self.bucket_name,
                s3_key,
                str(local_file)
            )
            
            logger.info(f"Downloaded file from S3: {s3_key}")
            return str(local_file)
            
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            raise
    
    def list_files(
        self,
        aoi_id: Optional[str] = None,
        source: Optional[str] = None,
        prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in S3 bucket.
        
        Args:
            aoi_id: Filter by Area of Interest ID
            source: Filter by data source
            prefix: Custom prefix to filter by
            
        Returns:
            List of file information dictionaries
        """
        # Build prefix
        if prefix:
            search_prefix = prefix
        elif aoi_id and source:
            search_prefix = f"{aoi_id}/{source}/"
        elif aoi_id:
            search_prefix = f"{aoi_id}/"
        else:
            search_prefix = ""
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=search_prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'uri': f"s3://{self.bucket_name}/{obj['Key']}"
                    })
            
            logger.info(f"Found {len(files)} files with prefix: {search_prefix}")
            return files
            
        except ClientError as e:
            logger.error(f"Error listing S3 objects: {e}")
            raise
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Deleted file from S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False
    
    def ensure_bucket_exists(self) -> bool:
        """
        Ensure S3 bucket exists, create if it doesn't.
        
        Returns:
            True if bucket exists or was created successfully
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} exists")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    logger.info(f"Created bucket: {self.bucket_name}")
                    return True
                except ClientError as create_error:
                    logger.error(f"Error creating bucket: {create_error}")
                    return False
            else:
                logger.error(f"Error checking bucket: {e}")
                return False
    
    def get_storage_stats(self, aoi_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Args:
            aoi_id: Optional AOI ID to filter statistics
            
        Returns:
            Dictionary with storage statistics
        """
        files = self.list_files(aoi_id=aoi_id)
        
        total_size = sum(f['size'] for f in files)
        total_files = len(files)
        
        # Group by source
        by_source = {}
        for f in files:
            parts = f['key'].split('/')
            if len(parts) >= 2:
                source = parts[1]
                if source not in by_source:
                    by_source[source] = {'count': 0, 'size': 0}
                by_source[source]['count'] += 1
                by_source[source]['size'] += f['size']
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_gb': total_size / (1024 ** 3),
            'by_source': by_source,
            'aoi_id': aoi_id or 'all'
        }

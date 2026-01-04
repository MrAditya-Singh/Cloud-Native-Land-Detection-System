"""
AWS service utilities for S3, SageMaker, and other AWS services
"""
import boto3
from typing import Optional, BinaryIO
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class AWSService:
    """AWS service wrapper for cloud operations"""
    
    def __init__(self):
        """Initialize AWS clients"""
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        self.sagemaker_client = boto3.client(
            'sagemaker',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        self.sagemaker_runtime = boto3.client(
            'sagemaker-runtime',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    
    def upload_to_s3(self, file_obj: BinaryIO, bucket: str, key: str) -> bool:
        """Upload a file to S3"""
        try:
            self.s3_client.upload_fileobj(file_obj, bucket, key)
            logger.info(f"Successfully uploaded {key} to {bucket}")
            return True
        except Exception as e:
            logger.error(f"Error uploading to S3: {e}")
            return False
    
    def download_from_s3(self, bucket: str, key: str, local_path: str) -> bool:
        """Download a file from S3"""
        try:
            self.s3_client.download_file(bucket, key, local_path)
            logger.info(f"Successfully downloaded {key} from {bucket}")
            return True
        except Exception as e:
            logger.error(f"Error downloading from S3: {e}")
            return False
    
    def get_s3_object(self, bucket: str, key: str) -> Optional[bytes]:
        """Get an object from S3"""
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Error getting S3 object: {e}")
            return None
    
    def list_s3_objects(self, bucket: str, prefix: str = "") -> list:
        """List objects in an S3 bucket"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            logger.error(f"Error listing S3 objects: {e}")
            return []
    
    def invoke_sagemaker_endpoint(self, endpoint_name: str, payload: bytes) -> Optional[dict]:
        """Invoke a SageMaker endpoint for inference"""
        try:
            response = self.sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='application/json',
                Body=payload
            )
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Error invoking SageMaker endpoint: {e}")
            return None


# Singleton instance
aws_service = AWSService()

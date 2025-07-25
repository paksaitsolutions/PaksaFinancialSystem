"""
CDN integration for static asset delivery.
"""
import boto3
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.logging import logger

class CDNManager:
    """CDN manager for static asset delivery."""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.cloudfront_client = boto3.client(
            'cloudfront',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.CDN_BUCKET_NAME
        self.distribution_id = settings.CLOUDFRONT_DISTRIBUTION_ID
    
    async def upload_asset(self, file_path: str, content: bytes, content_type: str) -> str:
        """Upload asset to CDN."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=content,
                ContentType=content_type,
                CacheControl='public, max-age=31536000'  # 1 year
            )
            
            cdn_url = f"https://{settings.CDN_DOMAIN}/{file_path}"
            logger.info(f"Uploaded asset to CDN: {cdn_url}")
            return cdn_url
            
        except Exception as e:
            logger.error(f"CDN upload failed: {str(e)}")
            raise
    
    async def invalidate_cache(self, paths: list) -> bool:
        """Invalidate CDN cache for specific paths."""
        try:
            response = self.cloudfront_client.create_invalidation(
                DistributionId=self.distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': str(datetime.utcnow().timestamp())
                }
            )
            
            logger.info(f"CDN cache invalidated for paths: {paths}")
            return True
            
        except Exception as e:
            logger.error(f"CDN invalidation failed: {str(e)}")
            return False
    
    def get_signed_url(self, file_path: str, expiration: int = 3600) -> str:
        """Generate signed URL for private assets."""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_path},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Signed URL generation failed: {str(e)}")
            return ""

cdn_manager = CDNManager()
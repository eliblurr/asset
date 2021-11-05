from botocore.exceptions import ClientError
from config import settings, UPLOAD_ROOT
import boto3, logging, os

logger = logging.getLogger("eAsset.main")

def s3():
    return boto3.client(
        service_name='s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

s3_client = s3()

def s3_upload(file, bucket=settings.AWS_STORAGE_BUCKET_NAME, object_name=None, **kwargs):
    if object_name is None:
        object_name = os.path.basename(file.filename)
    
    try:        
        response = s3_client.upload_fileobj(
            file.file, 
            bucket, 
            object_name,
            ExtraArgs={
                'ACL': settings.AWS_DEFAULT_ACL,
                "CacheControl": settings.AWS_S3_OBJECT_CACHE_CONTROL,
                'ContentType': file.content_type.split('/')[0]
            }
        )
    except ClientError as e:
        logger.error(e)
        return False
    return f'https://{bucket}.s3.amazonaws.com/{object_name}'

def s3_delete(object_name, bucket=settings.AWS_STORAGE_BUCKET_NAME):
    try:
        s3_client.delete_object(Bucket=bucket, Key=object_name)
    except ClientError as e:
        logger.error(e)
        return False
    return True
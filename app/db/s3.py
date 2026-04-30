import boto3
from botocore.config import Config

from app.config import settings

boto_config = Config(retries={"max_attempts": 3, "mode": "adaptive"})

s3_client = boto3.client(
    "s3",
    region_name=settings.AWS_REGION,
    config=boto_config,
)


def generate_presigned_upload_url(object_key: str, expires_in: int = 300) -> str:
    url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.S3_BUCKET_NAME,
            "Key": object_key,
        },
        ExpiresIn=expires_in,
    )
    return url


def generate_presigned_download_url(object_key: str, expires_in: int = 3600) -> str:
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.S3_BUCKET_NAME,
            "Key": object_key,
        },
        ExpiresIn=expires_in,
    )
    return url

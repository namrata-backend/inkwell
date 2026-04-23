from datetime import datetime, timezone

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.config import settings

boto_config = Config(retries={"max_attempts": 3, "mode": "adaptive"})

dynamodb = boto3.resource(
    "dynamodb", region_name=settings.AWS_REGION, config=boto_config
)
table = dynamodb.Table(settings.DYNAMODB_USERS_TABLE)


def create_user(user_id: str, username: str) -> dict:
    item = {
        "user_id": user_id,
        "username": username,
        "bio": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    table.put_item(Item=item)
    return item


def get_user(user_id: str) -> dict | None:
    try:
        response = table.get_item(Key={"user_id": user_id})
        return response.get("Item")
    except ClientError as e:
        raise e

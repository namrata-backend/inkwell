from datetime import datetime, timezone

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.config import settings

boto_config = Config(retries={"max_attempts": 3, "mode": "adaptive"})

dynamodb = boto3.resource(
    "dynamodb", region_name=settings.AWS_REGION, config=boto_config
)
table = dynamodb.Table(settings.DYNAMODB_REACTIONS_TABLE)


def put_reaction(
    target_id: str,
    user_id: str,
    target_type: str,
    reaction: str,
) -> dict:
    item = {
        "target_id": target_id,
        "user_id": user_id,
        "target_type": target_type,
        "reaction": reaction,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        table.put_item(Item=item)
        return item
    except ClientError as e:
        raise e


def get_reaction(target_id: str, user_id: str) -> dict | None:
    try:
        response = table.get_item(Key={"target_id": target_id, "user_id": user_id})
        return response.get("Item")
    except ClientError as e:
        raise e


def delete_reaction(target_id: str, user_id: str) -> None:
    try:
        table.delete_item(Key={"target_id": target_id, "user_id": user_id})
    except ClientError as e:
        raise e

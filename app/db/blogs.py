import uuid
from datetime import datetime, timezone

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.config import settings

boto_config = Config(retries={"max_attempts": 3, "mode": "adaptive"})

dynamodb = boto3.resource(
    "dynamodb", region_name=settings.AWS_REGION, config=boto_config
)
table = dynamodb.Table(settings.DYNAMODB_BLOGS_TABLE)


def create_blog(
    author_id: str, title: str, content: str, image_key: str | None
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "blog_id": str(uuid.uuid4()),
        "author_id": author_id,
        "title": title,
        "content": content,
        "image_key": image_key,
        "created_at": now,
        "updated_at": now,
    }
    table.put_item(Item=item)
    return item


def get_blog(blog_id: str) -> dict | None:
    try:
        response = table.get_item(Key={"blog_id": blog_id})
        return response.get("Item")
    except ClientError as e:
        raise e


def list_blogs(limit: int = 20, last_evaluated_key: dict | None = None) -> dict:
    kwargs: dict = {"Limit": limit}
    if last_evaluated_key:
        kwargs["ExclusiveStartKey"] = last_evaluated_key
    try:
        response = table.scan(**kwargs)
        return {
            "items": response.get("Items", []),
            "count": response.get("Count", 0),
            "last_evaluated_key": response.get("LastEvaluatedKey"),
        }
    except ClientError as e:
        raise e


def list_blogs_by_author(
    author_id: str, limit: int = 20, last_evaluated_key: dict | None = None
) -> dict:
    kwargs: dict = {
        "IndexName": "author_id-index",
        "KeyConditionExpression": "author_id = :aid",
        "ExpressionAttributeValues": {":aid": author_id},
        "Limit": limit,
    }
    if last_evaluated_key:
        kwargs["ExclusiveStartKey"] = last_evaluated_key
    try:
        response = table.query(**kwargs)
        return {
            "items": response.get("Items", []),
            "count": response.get("Count", 0),
            "last_evaluated_key": response.get("LastEvaluatedKey"),
        }
    except ClientError as e:
        raise e


def update_blog(blog_id: str, updates: dict) -> dict | None:
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_expr = "SET " + ", ".join(f"#{k} = :{k}" for k in updates)
    expr_names = {f"#{k}": k for k in updates}
    expr_values = {f":{k}": v for k, v in updates.items()}
    try:
        response = table.update_item(
            Key={"blog_id": blog_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ReturnValues="ALL_NEW",
        )
        return response.get("Attributes")
    except ClientError as e:
        raise e


def delete_blog(blog_id: str) -> None:
    try:
        table.delete_item(Key={"blog_id": blog_id})
    except ClientError as e:
        raise e

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
table = dynamodb.Table(settings.DYNAMODB_COMMENTS_TABLE)


def create_comment(
    blog_id: str,
    user_id: str,
    text: str,
    parent_comment_id: str | None = None,
) -> dict:
    item = {
        "comment_id": str(uuid.uuid4()),
        "blog_id": blog_id,
        "user_id": user_id,
        "parent_comment_id": parent_comment_id,
        "text": text,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    table.put_item(Item=item)
    return item


def get_comment(comment_id: str) -> dict | None:
    try:
        response = table.get_item(Key={"comment_id": comment_id})
        return response.get("Item")
    except ClientError as e:
        raise e


def get_comments_for_blog(blog_id: str) -> list:
    try:
        response = table.query(
            IndexName="blog_id-index",
            KeyConditionExpression="blog_id = :bid",
            ExpressionAttributeValues={":bid": blog_id},
        )
        return response.get("Items", [])
    except ClientError as e:
        raise e


def delete_comment(comment_id: str) -> None:
    try:
        table.delete_item(Key={"comment_id": comment_id})
    except ClientError as e:
        raise e


def build_comment_tree(comments: list) -> list:
    comment_map: dict = {}
    roots: list = []

    for comment in comments:
        comment["replies"] = []
        comment_map[comment["comment_id"]] = comment

    for comment in comments:
        parent_id = comment.get("parent_comment_id")
        if parent_id and parent_id in comment_map:
            comment_map[parent_id]["replies"].append(comment)
        else:
            roots.append(comment)

    return roots

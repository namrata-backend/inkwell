import base64
import json
import logging
import uuid

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.jwt import get_current_user_id
from app.db.blogs import (
    create_blog,
    delete_blog,
    get_blog,
    list_blogs,
    list_blogs_by_author,
    update_blog,
)
from app.db.s3 import generate_presigned_download_url, generate_presigned_upload_url
from app.models.blogs import CreateBlogRequest, UpdateBlogRequest

router = APIRouter(prefix="/api/v1/blogs", tags=["Blogs"])

logger = logging.getLogger("inkwell")


def _encode_key(key: dict) -> str:
    return base64.b64encode(json.dumps(key).encode()).decode()


def _decode_key(encoded: str) -> dict:
    return json.loads(base64.b64decode(encoded.encode()).decode())


@router.post("", status_code=status.HTTP_201_CREATED)
async def create(
    body: CreateBlogRequest,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    try:
        blog = create_blog(
            author_id=user_id,
            title=body.title,
            content=body.content,
            image_key=body.image_key,
        )
        return {"success": True, "data": blog}
    except ClientError as e:
        logger.error({"event": "create_blog_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.get("", status_code=status.HTTP_200_OK)
async def list_all(
    limit: int = Query(default=20, ge=1, le=100),
    last_evaluated_key: str = Query(default=None),
) -> dict:
    try:
        lek = _decode_key(last_evaluated_key) if last_evaluated_key else None
        result = list_blogs(limit=limit, last_evaluated_key=lek)
        encoded_lek = (
            _encode_key(result["last_evaluated_key"])
            if result["last_evaluated_key"]
            else None
        )
        return {
            "success": True,
            "data": {
                "items": result["items"],
                "count": result["count"],
                "last_evaluated_key": encoded_lek,
            },
        }
    except ClientError as e:
        logger.error({"event": "list_blogs_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.get("/mine", status_code=status.HTTP_200_OK)
async def list_mine(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(default=20, ge=1, le=100),
    last_evaluated_key: str = Query(default=None),
) -> dict:
    try:
        lek = _decode_key(last_evaluated_key) if last_evaluated_key else None
        result = list_blogs_by_author(
            author_id=user_id, limit=limit, last_evaluated_key=lek
        )
        encoded_lek = (
            _encode_key(result["last_evaluated_key"])
            if result["last_evaluated_key"]
            else None
        )
        return {
            "success": True,
            "data": {
                "items": result["items"],
                "count": result["count"],
                "last_evaluated_key": encoded_lek,
            },
        }
    except ClientError as e:
        logger.error({"event": "list_mine_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.get("/upload-url", status_code=status.HTTP_200_OK)
async def get_upload_url(
    user_id: str = Depends(get_current_user_id),
) -> dict:
    object_key = f"blog-images/{user_id}/{uuid.uuid4()}"
    url = generate_presigned_upload_url(object_key)
    return {"success": True, "data": {"upload_url": url, "object_key": object_key}}


@router.get("/{blog_id}", status_code=status.HTTP_200_OK)
async def get_one(blog_id: str) -> dict:
    try:
        blog = get_blog(blog_id)
        if blog is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "BLOG_NOT_FOUND",
                    "message": "Blog with this ID does not exist",
                },
            )
        if blog.get("image_key"):
            blog["image_url"] = generate_presigned_download_url(blog["image_key"])
        return {"success": True, "data": blog}
    except ClientError as e:
        logger.error({"event": "get_blog_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.put("/{blog_id}", status_code=status.HTTP_200_OK)
async def update(
    blog_id: str,
    body: UpdateBlogRequest,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    try:
        blog = get_blog(blog_id)
        if blog is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "BLOG_NOT_FOUND",
                    "message": "Blog with this ID does not exist",
                },
            )
        if blog["author_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "You do not have permission to update this blog",
                },
            )
        updates = body.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "NO_FIELDS", "message": "No fields provided to update"},
            )
        updated = update_blog(blog_id=blog_id, updates=updates)
        return {"success": True, "data": updated}
    except ClientError as e:
        logger.error({"event": "update_blog_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.delete("/{blog_id}", status_code=status.HTTP_200_OK)
async def delete(
    blog_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    try:
        blog = get_blog(blog_id)
        if blog is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "BLOG_NOT_FOUND",
                    "message": "Blog with this ID does not exist",
                },
            )
        if blog["author_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "You do not have permission to delete this blog",
                },
            )
        delete_blog(blog_id)
        return {"success": True, "data": {"message": "Blog deleted successfully"}}
    except ClientError as e:
        logger.error({"event": "delete_blog_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )

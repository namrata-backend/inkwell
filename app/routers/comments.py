import logging

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.jwt import get_current_user_id
from app.db.blogs import get_blog
from app.db.comments import (
    build_comment_tree,
    create_comment,
    delete_comment,
    get_comment,
    get_comments_for_blog,
)
from app.models.comments import CreateCommentRequest, CreateReplyRequest

router = APIRouter(prefix="/api/v1", tags=["Comments"])

logger = logging.getLogger("inkwell")


@router.post("/comments", status_code=status.HTTP_201_CREATED)
async def create(
    body: CreateCommentRequest,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    try:
        blog = get_blog(body.blog_id)
        if blog is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "BLOG_NOT_FOUND",
                    "message": "Blog with this ID does not exist",
                },
            )
        comment = create_comment(
            blog_id=body.blog_id,
            user_id=user_id,
            text=body.text,
        )
        return {"success": True, "data": comment}
    except ClientError as e:
        logger.error({"event": "create_comment_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.post("/comments/{comment_id}/reply", status_code=status.HTTP_201_CREATED)
async def reply(
    comment_id: str,
    body: CreateReplyRequest,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    try:
        parent = get_comment(comment_id)
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "COMMENT_NOT_FOUND",
                    "message": "Comment with this ID does not exist",
                },
            )
        comment = create_comment(
            blog_id=parent["blog_id"],
            user_id=user_id,
            text=body.text,
            parent_comment_id=comment_id,
        )
        return {"success": True, "data": comment}
    except ClientError as e:
        logger.error({"event": "reply_comment_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.get("/blogs/{blog_id}/comments", status_code=status.HTTP_200_OK)
async def get_for_blog(blog_id: str) -> dict:
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
        comments = get_comments_for_blog(blog_id)
        tree = build_comment_tree(comments)
        return {"success": True, "data": {"items": tree, "count": len(tree)}}
    except ClientError as e:
        logger.error({"event": "get_comments_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK)
async def delete(
    comment_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    try:
        comment = get_comment(comment_id)
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "COMMENT_NOT_FOUND",
                    "message": "Comment with this ID does not exist",
                },
            )
        if comment["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "You do not have permission to delete this comment",
                },
            )
        delete_comment(comment_id)
        return {"success": True, "data": {"message": "Comment deleted successfully"}}
    except ClientError as e:
        logger.error({"event": "delete_comment_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )

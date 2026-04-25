from typing import Optional

from pydantic import BaseModel


class CreateCommentRequest(BaseModel):
    blog_id: str
    text: str


class CreateReplyRequest(BaseModel):
    text: str


class CommentResponse(BaseModel):
    comment_id: str
    blog_id: str
    user_id: str
    parent_comment_id: Optional[str] = None
    text: str
    created_at: str
    replies: list = []

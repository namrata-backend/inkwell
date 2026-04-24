from typing import Optional

from pydantic import BaseModel


class CreateBlogRequest(BaseModel):
    title: str
    content: str
    image_key: Optional[str] = None


class UpdateBlogRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_key: Optional[str] = None


class BlogResponse(BaseModel):
    blog_id: str
    author_id: str
    title: str
    content: str
    image_key: Optional[str] = None
    created_at: str
    updated_at: str

from typing import Literal

from pydantic import BaseModel


class CreateReactionRequest(BaseModel):
    target_id: str
    target_type: Literal["blog", "comment"]
    reaction: Literal["like", "dislike"]


class DeleteReactionRequest(BaseModel):
    target_id: str

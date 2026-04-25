import logging

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.jwt import get_current_user_id
from app.db.reactions import delete_reaction, get_reaction, put_reaction
from app.models.reactions import CreateReactionRequest, DeleteReactionRequest

router = APIRouter(prefix="/api/v1/reactions", tags=["Reactions"])

logger = logging.getLogger("inkwell")


@router.post("", status_code=status.HTTP_200_OK)
async def react(
    body: CreateReactionRequest,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    try:
        existing = get_reaction(target_id=body.target_id, user_id=user_id)
        if existing and existing["reaction"] == body.reaction:
            delete_reaction(target_id=body.target_id, user_id=user_id)
            return {"success": True, "data": {"message": "Reaction removed"}}
        reaction = put_reaction(
            target_id=body.target_id,
            user_id=user_id,
            target_type=body.target_type,
            reaction=body.reaction,
        )
        return {"success": True, "data": reaction}
    except ClientError as e:
        logger.error({"event": "react_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.delete("", status_code=status.HTTP_200_OK)
async def remove_reaction(
    body: DeleteReactionRequest,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    try:
        existing = get_reaction(target_id=body.target_id, user_id=user_id)
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "REACTION_NOT_FOUND",
                    "message": "No reaction found to remove",
                },
            )
        delete_reaction(target_id=body.target_id, user_id=user_id)
        return {"success": True, "data": {"message": "Reaction removed successfully"}}
    except ClientError as e:
        logger.error({"event": "remove_reaction_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )

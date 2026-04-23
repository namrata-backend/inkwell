import logging

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.cognito import (
    confirm_sign_up,
    forgot_password,
    login,
    refresh_token,
    reset_password,
    sign_up,
)
from app.auth.jwt import get_current_user_id
from app.db.users import create_user, get_user
from app.models.auth import (
    ConfirmRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RefreshTokenResponse,
    ResetPasswordRequest,
    SignUpRequest,
    TokenResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

logger = logging.getLogger("inkwell")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(body: SignUpRequest) -> dict:
    try:
        result = sign_up(body.email, body.password, body.username)
        return {
            "success": True,
            "data": {
                "message": "Check your email for the confirmation code",
                "user_sub": result["user_sub"],
            },
        }
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "UsernameExistsException":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "USER_ALREADY_EXISTS",
                    "message": "An account with this email already exists",
                },
            )
        if code == "InvalidPasswordException":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_PASSWORD",
                    "message": "Password does not meet requirements",
                },
            )
        logger.error({"event": "signup_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm(body: ConfirmRequest) -> dict:
    try:
        confirm_sign_up(body.email, body.code)
        create_user(user_id=body.user_sub, username=body.username)
        return {"success": True, "data": {"message": "Account confirmed successfully"}}
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "CodeMismatchException":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_CODE",
                    "message": "The confirmation code is incorrect",
                },
            )
        if code == "ExpiredCodeException":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "EXPIRED_CODE",
                    "message": "The confirmation code has expired",
                },
            )
        logger.error({"event": "confirm_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(body: LoginRequest) -> dict:
    try:
        result = login(body.email, body.password)
        return {
            "success": True,
            "data": TokenResponse(
                access_token=result["AccessToken"],
                id_token=result["IdToken"],
                refresh_token=result["RefreshToken"],
                token_type=result["TokenType"],
                expires_in=result["ExpiresIn"],
            ),
        }
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "NotAuthorizedException":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Incorrect email or password",
                },
            )
        if code == "UserNotConfirmedException":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "USER_NOT_CONFIRMED",
                    "message": "Please confirm your account first",
                },
            )
        logger.error({"event": "login_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(body: RefreshRequest) -> dict:
    try:
        result = refresh_token(body.refresh_token)
        return {
            "success": True,
            "data": RefreshTokenResponse(
                access_token=result["AccessToken"],
                id_token=result["IdToken"],
                token_type=result["TokenType"],
                expires_in=result["ExpiresIn"],
            ),
        }
    except ClientError as e:
        logger.error({"event": "refresh_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_REFRESH_TOKEN",
                "message": "Refresh token is invalid or expired",
            },
        )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password_endpoint(body: ForgotPasswordRequest) -> dict:
    try:
        forgot_password(body.email)
        return {
            "success": True,
            "data": {
                "message": "If an account exists, a reset code was sent to your email"
            },
        }
    except ClientError as e:
        logger.error({"event": "forgot_password_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_endpoint(body: ResetPasswordRequest) -> dict:
    try:
        reset_password(body.email, body.code, body.new_password)
        return {"success": True, "data": {"message": "Password reset successfully"}}
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "CodeMismatchException":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_CODE",
                    "message": "The reset code is incorrect",
                },
            )
        if code == "ExpiredCodeException":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "EXPIRED_CODE",
                    "message": "The reset code has expired",
                },
            )
        logger.error({"event": "reset_password_error", "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(user_id: str = Depends(get_current_user_id)) -> dict:
    user = get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User profile not found"},
        )
    return {"success": True, "data": user}

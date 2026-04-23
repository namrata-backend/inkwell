import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.config import settings

boto_config = Config(retries={"max_attempts": 3, "mode": "adaptive"})

cognito_client = boto3.client(
    "cognito-idp",
    region_name=settings.AWS_REGION,
    config=boto_config,
)


def sign_up(email: str, password: str, username: str) -> dict:
    try:
        response = cognito_client.sign_up(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "preferred_username", "Value": username},
            ],
        )
        return {"user_sub": response["UserSub"]}
    except ClientError as e:
        raise e


def confirm_sign_up(email: str, code: str) -> None:
    try:
        cognito_client.confirm_sign_up(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            Username=email,
            ConfirmationCode=code,
        )
    except ClientError as e:
        raise e


def login(email: str, password: str) -> dict:
    try:
        response = cognito_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": email, "PASSWORD": password},
            ClientId=settings.COGNITO_APP_CLIENT_ID,
        )
        return response["AuthenticationResult"]
    except ClientError as e:
        raise e


def refresh_token(token: str) -> dict:
    try:
        response = cognito_client.initiate_auth(
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": token},
            ClientId=settings.COGNITO_APP_CLIENT_ID,
        )
        return response["AuthenticationResult"]
    except ClientError as e:
        raise e


def forgot_password(email: str) -> None:
    try:
        cognito_client.forgot_password(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            Username=email,
        )
    except ClientError as e:
        raise e


def reset_password(email: str, code: str, new_password: str) -> None:
    try:
        cognito_client.confirm_forgot_password(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            Username=email,
            ConfirmationCode=code,
            Password=new_password,
        )
    except ClientError as e:
        raise e

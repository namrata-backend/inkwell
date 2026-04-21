from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AWS
    AWS_REGION: str

    # Cognito
    COGNITO_USER_POOL_ID: str
    COGNITO_APP_CLIENT_ID: str

    # DynamoDB
    DYNAMODB_USERS_TABLE: str
    DYNAMODB_BLOGS_TABLE: str
    DYNAMODB_COMMENTS_TABLE: str
    DYNAMODB_REACTIONS_TABLE: str

    # S3
    S3_BUCKET_NAME: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

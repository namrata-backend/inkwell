# Inkwell API

A serverless blog API built with FastAPI and AWS. Supports user authentication, blog CRUD, comments, reactions, and image uploads.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (Python) |
| Auth | AWS Cognito (email OTP, JWT) |
| Compute | AWS Lambda (via Mangum) |
| API | AWS API Gateway (HTTP API) |
| Database | AWS DynamoDB (4 tables) |
| Storage | AWS S3 (blog images, pre-signed URLs) |
| Logging | AWS CloudWatch (structured JSON) |
| Access Control | AWS IAM (scoped execution role) |
| CI/CD | GitHub Actions |

## Local Setup

### Prerequisites
- Python 3.12+
- AWS account
- Git

### Steps

1. Clone the repo
```bash
git clone https://github.com/namrata-backend/inkwell.git
cd inkwell
```

2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

3. Install dependencies
```bash
pip install -r requirements-dev.txt
```

4. Set up environment variables
```bash
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
```
Fill in your AWS values in `.env`.

5. Run locally
```bash
uvicorn app.main:app --reload
```

6. Open Swagger UI
```
http://127.0.0.1:8000/docs
```

## Environment Variables

See [.env.example](.env.example) for all required variables.

| Variable | Description |
|----------|-------------|
| `AWS_REGION` | AWS region (e.g. ap-south-1) |
| `COGNITO_USER_POOL_ID` | Cognito User Pool ID |
| `COGNITO_APP_CLIENT_ID` | Cognito App Client ID |
| `DYNAMODB_USERS_TABLE` | DynamoDB Users table name |
| `DYNAMODB_BLOGS_TABLE` | DynamoDB Blogs table name |
| `DYNAMODB_COMMENTS_TABLE` | DynamoDB Comments table name |
| `DYNAMODB_REACTIONS_TABLE` | DynamoDB Reactions table name |
| `S3_BUCKET_NAME` | S3 bucket name for blog images |

## API Endpoints

All endpoints prefixed with `/api/v1/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /health | Public | Health check |
| POST | /auth/signup | Public | Register |
| POST | /auth/confirm | Public | Confirm OTP |
| POST | /auth/login | Public | Login |
| POST | /auth/refresh | Public | Refresh token |
| POST | /auth/forgot-password | Public | Forgot password |
| POST | /auth/reset-password | Public | Reset password |
| GET | /auth/me | Protected | Get profile |
| GET | /blogs | Public | List all blogs |
| POST | /blogs | Protected | Create blog |
| GET | /blogs/mine | Protected | List my blogs |
| GET | /blogs/upload-url | Protected | Get S3 upload URL |
| GET | /blogs/{id} | Public | Get one blog |
| PUT | /blogs/{id} | Protected | Update blog |
| DELETE | /blogs/{id} | Protected | Delete blog |
| GET | /blogs/{id}/comments | Public | Get comments |
| POST | /comments | Protected | Create comment |
| POST | /comments/{id}/reply | Protected | Reply to comment |
| DELETE | /comments/{id} | Protected | Delete comment |
| POST | /reactions | Protected | React |
| DELETE | /reactions | Protected | Remove reaction |

## Architecture

See [Document/ARCHITECTURE.md](Document/ARCHITECTURE.md) for full system design.

## Project Progress

See [Document/DEVELOPMENT_TRACKER.md](Document/DEVELOPMENT_TRACKER.md) for phase-by-phase progress.

## Running Tests

```bash
pytest --cov=app --cov-report=term-missing
```

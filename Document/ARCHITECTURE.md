# Inkwell — System Architecture

This document describes the complete system design for the Inkwell Serverless Blog API.
It is written before code starts and updated as the system evolves.

---

## System Overview

Inkwell is a serverless REST API for a blogging platform. There are no managed servers.
Code runs only when a request arrives (Lambda), data is stored in managed cloud services (DynamoDB, S3, Cognito),
and the entire infrastructure scales automatically.

---

## High-Level Architecture

```
                          ┌─────────────────────────────────────────────────────┐
                          │                    AWS Cloud                         │
                          │                                                      │
  Client (Browser/App)    │   ┌──────────────┐     ┌─────────────────────────┐  │
  ──────────────────── ───┼──▶│ API Gateway  │────▶│   AWS Lambda            │  │
                          │   │ (HTTP API)   │     │   (FastAPI + Mangum)    │  │
                          │   │              │     │                         │  │
                          │   │  Cognito JWT │     │  app/                   │  │
                          │   │  Authorizer  │     │  ├── routers/           │  │
                          │   └──────────────┘     │  │   ├── auth.py        │  │
                          │                        │  │   ├── blogs.py       │  │
                          │   ┌──────────────┐     │  │   ├── comments.py    │  │
                          │   │ AWS Cognito  │◀────│  │   └── reactions.py   │  │
                          │   │ User Pool    │     │  ├── db/                 │  │
                          │   │              │     │  ├── auth/               │  │
                          │   │ - Signup     │     │  └── models/             │  │
                          │   │ - OTP verify │     └──────────┬──────────────┘  │
                          │   │ - JWT issue  │                │                  │
                          │   └──────────────┘                │                  │
                          │                                   │                  │
                          │              ┌────────────────────┼──────────────┐   │
                          │              │                    │              │   │
                          │              ▼                    ▼              ▼   │
                          │   ┌──────────────────┐  ┌──────────────┐  ┌──────┐  │
                          │   │   AWS DynamoDB   │  │   AWS S3     │  │ CW   │  │
                          │   │                  │  │              │  │ Logs │  │
                          │   │  - Users         │  │  Blog images │  │      │  │
                          │   │  - Blogs         │  │  Pre-signed  │  │      │  │
                          │   │  - Comments      │  │  URLs        │  │      │  │
                          │   │  - Reactions     │  │              │  │      │  │
                          │   └──────────────────┘  └──────────────┘  └──────┘  │
                          │                                                      │
                          │   ┌──────────────────────────────────────────────┐   │
                          │   │  AWS IAM — Execution Role (least privilege)  │   │
                          │   └──────────────────────────────────────────────┘   │
                          └─────────────────────────────────────────────────────┘
```

---

## AWS Services and Their Roles

| Service | Role in Inkwell |
|---------|----------------|
| **API Gateway** | The single public entry point. Routes all HTTP requests to Lambda. Validates Cognito JWTs on protected routes before Lambda even runs. |
| **AWS Lambda** | Runs the FastAPI application code. Triggered by API Gateway. Stateless — no memory between requests. Scales to zero when idle. |
| **AWS Cognito** | Handles all authentication. Stores user credentials (email, password). Issues JWT tokens (ID, access, refresh). Sends OTP emails for signup and password reset. |
| **AWS DynamoDB** | The primary database. Four tables store all application data. Serverless, scales automatically, billed per request. |
| **AWS S3** | Stores blog images. Never served directly — always via pre-signed URLs with expiry. Clients upload directly to S3 (Lambda is not in the upload path). |
| **AWS CloudWatch** | Receives all structured JSON logs from Lambda automatically. Used for debugging, monitoring, and alerts. |
| **AWS IAM** | The Lambda execution role. Grants the Lambda function the minimum permissions needed to talk to DynamoDB, S3, Cognito, and CloudWatch — nothing more. |

---

## Request Lifecycle (Happy Path)

### Public Request (e.g. GET /api/v1/blogs)
```
1. Client sends HTTP request to API Gateway invoke URL
2. API Gateway receives request — no authorizer on public routes
3. API Gateway triggers Lambda with the request as an event
4. Mangum adapter converts the Lambda event to a FastAPI request
5. FastAPI router handles the request → queries DynamoDB
6. Response flows back: FastAPI → Mangum → Lambda → API Gateway → Client
7. CloudWatch receives structured log lines from the Lambda execution
```

### Protected Request (e.g. POST /api/v1/blogs)
```
1. Client sends HTTP request with Authorization: Bearer <JWT> header
2. API Gateway Cognito authorizer intercepts the request
3. Authorizer validates the JWT against Cognito's public JWKS endpoint
4. If invalid → 401 returned immediately, Lambda never runs
5. If valid → API Gateway passes request to Lambda with user claims
6. FastAPI JWT middleware extracts user_id (sub claim) from token
7. Router handles the request with the verified user_id
8. DynamoDB write occurs with author_id = current user
```

### Image Upload Flow
```
1. Client calls GET /api/v1/blogs/upload-url
2. Lambda generates a pre-signed S3 PUT URL (valid 5 minutes)
3. URL returned to client
4. Client uploads image DIRECTLY to S3 using the pre-signed URL
   (Lambda is completely out of this path — faster, no Lambda cost)
5. Client sends blog create request with the S3 object key
6. Lambda saves blog with image_key to DynamoDB
7. When blog is fetched, Lambda generates a pre-signed GET URL (valid 1 hour)
8. Client uses that URL to display the image
```

---

## Database Schema

### Table 1: Users
```
PK: user_id (String) = Cognito sub (UUID)

Fields:
  user_id       String    Cognito sub — primary key
  username      String    Public display name (from Cognito preferred_username)
  bio           String    Optional profile bio
  created_at    String    ISO 8601 timestamp

Note: Cognito holds email, password, and verification status.
      This table holds app-specific profile data only.
```

### Table 2: Blogs
```
PK: blog_id (String) = UUID generated on create

Fields:
  blog_id       String    UUID
  author_id     String    FK → Users.user_id
  title         String
  content       String    Full blog body
  image_key     String    S3 object key (optional)
  created_at    String    ISO 8601 timestamp
  updated_at    String    ISO 8601 timestamp

GSI 1: author_id-index
  PK: author_id
  Use: list all blogs by a specific user (GET /api/v1/blogs/mine)

GSI 2: created_at-index  (optional)
  PK: created_at (or a partition shard)
  Use: latest blogs feed
```

### Table 3: Comments
```
PK: comment_id (String) = UUID generated on create

Fields:
  comment_id          String    UUID
  blog_id             String    FK → Blogs.blog_id
  user_id             String    FK → Users.user_id
  parent_comment_id   String    NULL for top-level, comment_id for replies
  text                String    Comment body
  created_at          String    ISO 8601 timestamp

GSI 1: blog_id-index
  PK: blog_id
  Use: fetch all comments for a blog (GET /api/v1/blogs/{id}/comments)
  Note: tree (nesting) is built in application code after querying this GSI
```

### Table 4: Reactions
```
PK: target_id (String) = blog_id or comment_id
SK: user_id   (String) = Cognito sub

Composite PK + SK enforces one reaction per user per target at the DB level.

Fields:
  target_id     String    blog_id or comment_id
  user_id       String    FK → Users.user_id
  target_type   String    "blog" or "comment"
  reaction      String    "like" or "dislike"
  created_at    String    ISO 8601 timestamp
```

---

## Authentication Flow

```
SIGNUP
  Client ──▶ POST /api/v1/auth/signup (email, password, username)
         ──▶ Lambda calls Cognito SignUp
         ──▶ Cognito sends 6-digit OTP to email
         ◀── 200: "check your email"

CONFIRM OTP
  Client ──▶ POST /api/v1/auth/confirm (email, otp_code)
         ──▶ Lambda calls Cognito ConfirmSignUp
         ──▶ On success: Lambda creates row in DynamoDB Users table
         ◀── 200: "account confirmed"

LOGIN
  Client ──▶ POST /api/v1/auth/login (email, password)
         ──▶ Lambda calls Cognito InitiateAuth (USER_PASSWORD_AUTH)
         ◀── 200: { id_token, access_token, refresh_token }

TOKEN REFRESH
  Client ──▶ POST /api/v1/auth/refresh (refresh_token)
         ──▶ Lambda calls Cognito InitiateAuth (REFRESH_TOKEN_AUTH)
         ◀── 200: { id_token, access_token }

PROTECTED REQUESTS
  Client ──▶ Any protected endpoint with Authorization: Bearer <id_token>
         ──▶ API Gateway Cognito authorizer validates token
         ──▶ Lambda FastAPI dependency extracts sub (user_id) from claims
         ──▶ Handler receives verified user_id
```

---

## Folder Structure

```
Inkwell/
├── CLAUDE.md                        ← Claude's behaviour rules
├── .env                             ← Local secrets (gitignored)
├── .env.example                     ← Template committed to git
├── .gitignore
├── .pre-commit-config.yaml          ← black, flake8, isort hooks
├── requirements.txt                 ← Production dependencies
├── requirements-dev.txt             ← Dev/test dependencies
├── README.md
│
├── Document/
│   ├── Serverless_Blog_API_Roadmap.docx
│   ├── DEVELOPMENT_TRACKER.md       ← Phase & step progress
│   └── ARCHITECTURE.md              ← This file
│
├── app/
│   ├── main.py                      ← FastAPI app init, Mangum handler, router registration
│   ├── config.py                    ← Env var loading and validation
│   ├── exceptions.py                ← Custom exception classes + handlers
│   ├── logging_config.py            ← Structured JSON logger setup
│   │
│   ├── routers/
│   │   ├── auth.py                  ← /api/v1/auth/* endpoints
│   │   ├── blogs.py                 ← /api/v1/blogs/* endpoints
│   │   ├── comments.py              ← /api/v1/comments/* endpoints
│   │   └── reactions.py             ← /api/v1/reactions/* endpoints
│   │
│   ├── db/
│   │   ├── client.py                ← boto3 DynamoDB client singleton
│   │   ├── users.py                 ← Users table queries
│   │   ├── blogs.py                 ← Blogs table queries
│   │   ├── comments.py              ← Comments table queries
│   │   └── reactions.py             ← Reactions table queries
│   │
│   ├── auth/
│   │   ├── cognito.py               ← boto3 Cognito calls (signup, login, etc.)
│   │   └── jwt.py                   ← JWT verification dependency (FastAPI Depends)
│   │
│   └── models/
│       ├── auth.py                  ← Pydantic request/response models for auth
│       ├── blogs.py                 ← Pydantic models for blogs
│       ├── comments.py              ← Pydantic models for comments
│       └── reactions.py             ← Pydantic models for reactions
│
└── tests/
    ├── conftest.py                  ← Shared fixtures (test client, mock tokens)
    ├── test_auth.py
    ├── test_blogs.py
    ├── test_comments.py
    └── test_reactions.py
```

---

## API Endpoint Reference

All endpoints prefixed with `/api/v1/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /health | Public | Health check |
| POST | /auth/signup | Public | Register with email + password |
| POST | /auth/confirm | Public | Confirm account with OTP |
| POST | /auth/login | Public | Login, receive JWT tokens |
| POST | /auth/refresh | Public | Refresh access token |
| POST | /auth/forgot-password | Public | Send password reset OTP |
| POST | /auth/reset-password | Public | Reset password with OTP |
| GET | /auth/me | Protected | Get current user info |
| GET | /blogs | Public | List all blogs (paginated) |
| POST | /blogs | Protected | Create a blog |
| GET | /blogs/mine | Protected | List own blogs |
| GET | /blogs/upload-url | Protected | Get pre-signed S3 upload URL |
| GET | /blogs/{blog_id} | Public | Get one blog |
| PUT | /blogs/{blog_id} | Protected | Update own blog |
| DELETE | /blogs/{blog_id} | Protected | Delete own blog |
| GET | /blogs/{blog_id}/comments | Public | Get comments for a blog (tree) |
| POST | /comments | Protected | Create a comment on a blog |
| POST | /comments/{comment_id}/reply | Protected | Reply to a comment |
| DELETE | /comments/{comment_id} | Protected | Delete own comment |
| POST | /reactions | Protected | React to blog or comment |
| DELETE | /reactions | Protected | Remove reaction |

---

## Authorization Matrix

| Action | Owner | Any logged-in user | Public (no login) |
|--------|-------|--------------------|-------------------|
| Read blogs | Yes | Yes | Yes |
| Create blog | Yes | Yes | No |
| Update blog | Yes | No | No |
| Delete blog | Yes | No | No |
| Read comments | Yes | Yes | Yes |
| Create comment | Yes | Yes | No |
| Reply to comment | Yes | Yes | No |
| Delete comment | Yes (own) | No | No |
| React to blog/comment | Yes | Yes | No |
| Remove own reaction | Yes | No | No |
| Upload image | Yes | Yes | No |

---

## Environment Variables

All loaded from `.env` locally, and set as Lambda environment variables in AWS.

```
AWS_REGION                   AWS region (e.g. ap-south-1)
COGNITO_USER_POOL_ID         Cognito User Pool ID
COGNITO_APP_CLIENT_ID        Cognito App Client ID
DYNAMODB_USERS_TABLE         DynamoDB Users table name
DYNAMODB_BLOGS_TABLE         DynamoDB Blogs table name
DYNAMODB_COMMENTS_TABLE      DynamoDB Comments table name
DYNAMODB_REACTIONS_TABLE     DynamoDB Reactions table name
S3_BUCKET_NAME               S3 bucket name for blog images
```

---

## Security Decisions

| Decision | Reason |
|----------|--------|
| Cognito public client (no app secret) | Simpler for learning; appropriate for a client-side app |
| Block public S3 access | Images served only via time-limited pre-signed URLs — no permanent public URLs |
| JWT validated at API Gateway | Saves Lambda cost — invalid tokens never reach Lambda |
| IAM least-privilege role | Lambda can only access its own tables and bucket — no overpermission |
| Pydantic validation on all inputs | Invalid data rejected before it reaches DB layer |
| No stack traces in error responses | Internal errors never leak implementation details to clients |
| Structured JSON logging | Logs are queryable by field in CloudWatch — faster debugging |

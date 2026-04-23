# Inkwell — Development Tracker

Track every phase and every step as you build.
Update status after each step is verified. Never mark something Done until the "Done when" checkpoint is truly met.

**Status legend:**
- `[ ]` Not started
- `[~]` In progress
- `[x]` Done & verified

---

## Phase 1 — Design on Paper
**Branch:** `feature/phase-1-design`
**Goal:** Complete system design before touching any code

| Step | Task | Status |
|------|------|--------|
| 1.1 | Define all entities and their fields (User, Blog, Comment, Reaction) | `[x]` |
| 1.2 | Write the full endpoint list (~15 endpoints) | `[x]` |
| 1.3 | Write the authorization matrix (who can do what) | `[x]` |
| 1.4 | Walk through 3 user stories on paper | `[x]` |

**Done when:** Every user story traces through endpoints without gaps.

---

## Phase 2 — DynamoDB Schema
**Branch:** `feature/phase-2-dynamodb-schema`
**Goal:** Plan all tables and indexes before any code or AWS setup

| Step | Task | Status |
|------|------|--------|
| 2.1 | Design Users table (PK, fields) | `[x]` |
| 2.2 | Design Blogs table (PK, GSIs) | `[x]` |
| 2.3 | Design Comments table (PK, GSIs, parent_comment_id logic) | `[x]` |
| 2.4 | Design Reactions table (PK + SK composite key) | `[x]` |
| 2.5 | Verify every read endpoint has an indexed query path | `[x]` |

**Done when:** No endpoint requires a full table scan.

---

## Phase 3 — Local Project Setup
**Branch:** `feature/phase-3-project-setup`
**Goal:** Clean, running FastAPI project pushed to GitHub

| Step | Task | Status |
|------|------|--------|
| 3.1 | Create project folder, git init, create GitHub repo | `[x]` |
| 3.2 | Create Python virtual environment | `[x]` |
| 3.3 | Install dependencies, create requirements.txt and requirements-dev.txt | `[x]` |
| 3.4 | Create folder structure (app/, routers/, db/, auth/, models/, tests/) | `[x]` |
| 3.5 | Create .env and .env.example | `[x]` |
| 3.6 | Create .gitignore | `[x]` |
| 3.7 | Set up pre-commit hooks (black, flake8, isort) | `[x]` |
| 3.8 | Write GET /api/v1/health endpoint | `[x]` |
| 3.9 | Run uvicorn locally, verify Swagger loads at /docs | `[x]` |
| 3.10 | Create README.md (initial version) | `[x]` |
| 3.11 | Push to GitHub, set branch protection on main and develop | `[x]` |

**Done when:** FastAPI runs locally, /docs loads, repo is on GitHub with .env excluded.

---

## Phase 4 — Cognito Setup (AWS Console)
**Branch:** `feature/phase-4-cognito-setup`
**Goal:** Working Cognito User Pool before writing auth code

| Step | Task | Status |
|------|------|--------|
| 4.1 | Create Cognito User Pool with email sign-in | `[X]` |
| 4.2 | Create App Client (public, no secret) | `[X]` |
| 4.3 | Save User Pool ID, App Client ID, Region to .env | `[X]` |
| 4.4 | Manual test: create user in console, receive email | `[X]` |
| 4.5 | Test full signup + confirm + login via AWS CLI or console | `[X]` |
| 4.6 | Verify JWT claims at jwt.io (sub, email, preferred_username) | `[X]` |

**Done when:** Full signup/confirm/login cycle works without any FastAPI code.

---

## Phase 5 — AWS Resources Setup (Console)
**Branch:** `feature/phase-5-aws-resources`
**Goal:** DynamoDB tables and S3 bucket ready for use

| Step | Task | Status |
|------|------|--------|
| 5.1 | Create Users DynamoDB table | `[X]` |
| 5.2 | Create Blogs DynamoDB table with GSIs | `[X]` |
| 5.3 | Create Comments DynamoDB table with GSIs | `[X]` |
| 5.4 | Create Reactions DynamoDB table (composite PK+SK) | `[X]` |
| 5.5 | Manual test: insert and query item in each table | `[X]` |
| 5.6 | Create S3 bucket (block public access ON) | `[X]` |
| 5.7 | Configure CORS on S3 bucket | `[X]` |
| 5.8 | Manual test: upload and download file via console | `[X]` |

**Done when:** Every table and bucket responds to manual operations in the console.

---

## Phase 6 — Auth Layer (FastAPI)
**Branch:** `feature/phase-6-auth`
**Goal:** All 6 auth endpoints working with token middleware

| Step | Task | Status |
|------|------|--------|
| 6.1 | Build POST /api/v1/auth/signup | `[X]` |
| 6.2 | Build POST /api/v1/auth/confirm | `[X]` |
| 6.3 | Build POST /api/v1/auth/login | `[X]` |
| 6.4 | Build POST /api/v1/auth/refresh | `[X]` |
| 6.5 | Build POST /api/v1/auth/forgot-password | `[X]` |
| 6.6 | Build POST /api/v1/auth/reset-password | `[X]` |
| 6.7 | Build JWT verification middleware (FastAPI dependency) | `[X]` |
| 6.8 | Build GET /api/v1/auth/me (protected, returns user_id) | `[X]` |
| 6.9 | Test all auth flows in Swagger | `[X]` |
| 6.10 | Test middleware: no token → 401, bad token → 401, valid → 200 | `[X]` |

**Done when:** All 6 auth flows work, middleware rejects bad tokens, DynamoDB Users row created on confirm.

---

## Phase 7 — Blog CRUD
**Branch:** `feature/phase-7-blogs`
**Goal:** Full blog CRUD with ownership enforcement

| Step | Task | Status |
|------|------|--------|
| 7.1 | Build POST /api/v1/blogs (create) | `[ ]` |
| 7.2 | Build GET /api/v1/blogs (list all, paginated) | `[ ]` |
| 7.3 | Build GET /api/v1/blogs/mine (list own) | `[ ]` |
| 7.4 | Build GET /api/v1/blogs/{blog_id} (get one) | `[ ]` |
| 7.5 | Build PUT /api/v1/blogs/{blog_id} (update, owner only) | `[ ]` |
| 7.6 | Build DELETE /api/v1/blogs/{blog_id} (delete, owner only) | `[ ]` |
| 7.7 | Test ownership: user B cannot update/delete user A's blog → 403 | `[ ]` |

**Done when:** Ownership rules enforced, tested with two different users.

---

## Phase 8 — Comments and Reactions
**Branch:** `feature/phase-8-comments-reactions`
**Goal:** Comment tree and reaction toggle working correctly

| Step | Task | Status |
|------|------|--------|
| 8.1 | Build POST /api/v1/comments (create comment) | `[ ]` |
| 8.2 | Build POST /api/v1/comments/{comment_id}/reply | `[ ]` |
| 8.3 | Build GET /api/v1/blogs/{blog_id}/comments (tree structure) | `[ ]` |
| 8.4 | Build DELETE /api/v1/comments/{comment_id} (owner only) | `[ ]` |
| 8.5 | Build POST /api/v1/reactions (like/dislike blog or comment) | `[ ]` |
| 8.6 | Build DELETE /api/v1/reactions (remove reaction) | `[ ]` |
| 8.7 | Test comment tree renders correctly (parents with nested replies) | `[ ]` |
| 8.8 | Test reaction toggle: like → like again → removed. Like → dislike → flipped | `[ ]` |

**Done when:** Comment tree correct, reaction toggle works, no duplicate reactions possible.

---

## Phase 9 — S3 Image Uploads
**Branch:** `feature/phase-9-image-uploads`
**Goal:** Full upload → store → retrieve → display cycle

| Step | Task | Status |
|------|------|--------|
| 9.1 | Build GET /api/v1/blogs/upload-url (returns pre-signed PUT URL) | `[ ]` |
| 9.2 | Test: PUT image file directly to S3 using the URL | `[ ]` |
| 9.3 | Update blog create to accept image_key | `[ ]` |
| 9.4 | Update blog get to return pre-signed GET URL for image | `[ ]` |
| 9.5 | Test full cycle: get URL → upload → create blog → fetch → image displays | `[ ]` |
| 9.6 | Test URL expiry (set short TTL, confirm it stops working after) | `[ ]` |

**Done when:** Full upload → store → retrieve → display cycle works end to end.

---

## Phase 10 — IAM Role for Lambda
**Branch:** `feature/phase-10-iam-role`
**Goal:** Least-privilege IAM execution role, verified with simulator

| Step | Task | Status |
|------|------|--------|
| 10.1 | Create Lambda execution role | `[ ]` |
| 10.2 | Attach AWSLambdaBasicExecutionRole (CloudWatch Logs) | `[ ]` |
| 10.3 | Add scoped DynamoDB permissions (4 tables + GSIs) | `[ ]` |
| 10.4 | Add scoped S3 permissions (your bucket only) | `[ ]` |
| 10.5 | Add scoped Cognito permissions (only actions used) | `[ ]` |
| 10.6 | Verify with IAM policy simulator — allowed actions pass, others deny | `[ ]` |

**Done when:** Simulator confirms least-privilege access for every service.

---

## Phase 11 — Mangum (Lambda Wrapper)
**Branch:** `feature/phase-11-mangum`
**Goal:** FastAPI wrapped for Lambda, local dev unchanged

| Step | Task | Status |
|------|------|--------|
| 11.1 | Add Mangum handler to main.py | `[ ]` |
| 11.2 | Verify uvicorn still works locally after adding Mangum | `[ ]` |
| 11.3 | Verify /docs, /health, one protected endpoint still work | `[ ]` |

**Done when:** Mangum added, nothing broke locally.

---

## Phase 12 — First Manual Deployment
**Branch:** `feature/phase-12-lambda-deploy`
**Goal:** Lambda runs and returns real 200 response

| Step | Task | Status |
|------|------|--------|
| 12.1 | Zip app/ folder + dependencies | `[ ]` |
| 12.2 | Create Lambda function, upload zip, attach IAM role | `[ ]` |
| 12.3 | Set all environment variables on Lambda | `[ ]` |
| 12.4 | Set handler to app.main.handler | `[ ]` |
| 12.5 | Test invocation in Lambda console → 200 response | `[ ]` |
| 12.6 | Check CloudWatch Logs — log lines visible | `[ ]` |

**Done when:** Lambda test invocation returns real 200 response.

---

## Phase 13 — API Gateway
**Branch:** `feature/phase-13-api-gateway`
**Goal:** Every endpoint accessible via public internet URL

| Step | Task | Status |
|------|------|--------|
| 13.1 | Create HTTP API in API Gateway | `[ ]` |
| 13.2 | Add ANY /{proxy+} route → Lambda integration | `[ ]` |
| 13.3 | Set up Cognito JWT authorizer on protected routes | `[ ]` |
| 13.4 | Configure CORS for frontend origin | `[ ]` |
| 13.5 | Deploy to prod stage, copy invoke URL | `[ ]` |
| 13.6 | Test /health from Postman → 200 | `[ ]` |
| 13.7 | Test protected route without token → 401 | `[ ]` |
| 13.8 | Run full test suite against deployed URL | `[ ]` |

**Done when:** Every endpoint that worked locally now works through API Gateway URL.

---

## Phase 14 — CloudWatch Logging
**Branch:** `feature/phase-14-cloudwatch`
**Goal:** Logs queryable, alarms firing correctly

| Step | Task | Status |
|------|------|--------|
| 14.1 | Verify logs appear automatically from Lambda | `[ ]` |
| 14.2 | Add structured JSON log calls at info/warning/error levels | `[ ]` |
| 14.3 | Create Lambda error rate alarm | `[ ]` |
| 14.4 | Create Lambda throttle alarm | `[ ]` |
| 14.5 | Trigger known error, find log lines in CloudWatch | `[ ]` |
| 14.6 | Run Logs Insights query — results appear | `[ ]` |

**Done when:** Any endpoint can be debugged by reading CloudWatch, alarms fire as expected.

---

## Phase 15 — GitHub Actions CI/CD
**Branch:** `feature/phase-15-cicd`
**Goal:** Push-to-deploy working, broken builds don't deploy

| Step | Task | Status |
|------|------|--------|
| 15.1 | Create .github/workflows/deploy.yml | `[ ]` |
| 15.2 | Add AWS credentials to GitHub Secrets | `[ ]` |
| 15.3 | Workflow: checkout → install deps → run tests → zip → update Lambda | `[ ]` |
| 15.4 | Push trivial change to main → watch Action run → Lambda updated | `[ ]` |
| 15.5 | Push broken code → Action fails → Lambda NOT updated | `[ ]` |

**Done when:** Push-to-deploy works and failing builds do not deploy broken code.

---

## Phase 16 — Polish and Hardening
**Branch:** `feature/phase-16-polish`
**Goal:** Production-grade reliability and documentation

| Step | Task | Status |
|------|------|--------|
| 16.1 | Add pagination to blog list (limit + last_evaluated_key) | `[ ]` |
| 16.2 | Add rate limiting on auth endpoints | `[ ]` |
| 16.3 | Audit all error responses — consistent JSON shape everywhere | `[ ]` |
| 16.4 | Finalise README with architecture diagram and endpoint list | `[ ]` |
| 16.5 | Test pagination with 30+ blogs — no duplicates, no gaps | `[ ]` |
| 16.6 | Hammer /login with wrong passwords — rate limiter kicks in | `[ ]` |

**Done when:** App handles scale, abuse, and errors gracefully.

---

## Phase 17 — Optional Frontend
**Branch:** `feature/phase-17-frontend`
**Goal:** Real user can use the app end-to-end in a browser

| Step | Task | Status |
|------|------|--------|
| 17.1 | Set up React app (or plain HTML/JS) | `[ ]` |
| 17.2 | Implement full auth flow (signup → OTP → login) | `[ ]` |
| 17.3 | Implement blog create with image upload | `[ ]` |
| 17.4 | Implement blog feed, comments, reactions | `[ ]` |
| 17.5 | Host on S3 + CloudFront or Vercel | `[ ]` |
| 17.6 | Test full user journey in browser (including mobile) | `[ ]` |

**Done when:** A real user can use the app end-to-end without reading any docs.

---

## Overall Progress

| Phase | Name | Status |
|-------|------|--------|
| 1 | Design on Paper | `[x]` |
| 2 | DynamoDB Schema | `[x]` |
| 3 | Local Project Setup | `[x]` |
| 4 | Cognito Setup | `[ ]` |
| 5 | AWS Resources Setup | `[ ]` |
| 6 | Auth Layer | `[ ]` |
| 7 | Blog CRUD | `[ ]` |
| 8 | Comments and Reactions | `[ ]` |
| 9 | S3 Image Uploads | `[ ]` |
| 10 | IAM Role | `[ ]` |
| 11 | Mangum Wrapper | `[ ]` |
| 12 | First Manual Deployment | `[ ]` |
| 13 | API Gateway | `[ ]` |
| 14 | CloudWatch | `[ ]` |
| 15 | GitHub Actions CI/CD | `[ ]` |
| 16 | Polish and Hardening | `[ ]` |
| 17 | Optional Frontend | `[ ]` |

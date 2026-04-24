import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from mangum import Mangum

from app.exceptions import register_exception_handlers
from app.logging_config import logger
from app.routers.auth import router as auth_router
from app.routers.blogs import router as blogs_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Inkwell API starting up")
    yield
    logger.info("Inkwell API shutting down")


app = FastAPI(
    title="Inkwell API",
    description="Serverless Blog API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(blogs_router)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next: any) -> Response:
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/api/v1/health", tags=["Health"])
async def health_check() -> dict:
    return {"success": True, "data": {"status": "ok"}}


handler = Mangum(app, lifespan="on")

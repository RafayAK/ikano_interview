from contextlib import asynccontextmanager
from pathlib import Path

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.applications import router as applications_router
from app.api.resume import router as resume_router
from app.config import settings
from app.db import models  # noqa: F401  ensures models are registered on Base.metadata
from app.db.base import Base
from app.db.session import engine
from app.logging_config import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Ikano Onboarding", lifespan=lifespan)

app.include_router(applications_router, prefix="/api/v1")
app.include_router(resume_router, prefix="/api/v1")

# Reuses an AWS ALB's X-Amzn-Trace-Id when present (see load balancer request tracing
# docs); generates a fresh one otherwise. Echoed back on the response for support tracing.
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Amzn-Trace-Id",
    update_request_header=True,
    transformer=None,
    validator=None,
)

# Added last so it wraps outermost, per Starlette's middleware ordering.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type", "Authorization", "X-Amzn-Trace-Id"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Mount compiled Astro frontend if present (e.g. in unified production Docker container or after npm run build)
_dist_path = (
    Path(settings.frontend_dist_dir)
    if settings.frontend_dist_dir
    else Path("/app/frontend_dist")
)
if not _dist_path.is_dir():
    _local_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if _local_dist.is_dir():
        _dist_path = _local_dist

if _dist_path.is_dir():
    app.mount("/", StaticFiles(directory=str(_dist_path), html=True), name="frontend")



from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analytics, auth, health, history, scans, users
from app.core.config import settings
from app.db.session import Base, engine
from app.models import password_reset, password_reset_otp, scan, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create missing database tables
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="PhishGuard phishing URL risk analysis API",
    version="1.0.0",
    lifespan=lifespan,
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


# API routes
app.include_router(health.router)
app.include_router(auth.router, prefix="/api")
app.include_router(scans.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "PhishGuard API is running",
        "docs": "/docs",
        "health": "/health",
    }

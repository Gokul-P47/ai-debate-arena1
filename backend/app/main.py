"""FastAPI application entry point."""

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.routes import debate, health

load_dotenv()

APP_TITLE = "AI Debate Arena API"
APP_VERSION = "1.0.0"
API_V1_PREFIX = "/api/v1"

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

app.include_router(health.router, prefix=API_V1_PREFIX)
app.include_router(debate.router, prefix=API_V1_PREFIX)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning basic API information.

    Returns:
        Dictionary with welcome message, title, and version.
    """
    return {
        "message": "Welcome to AI Debate Arena API",
        "title": APP_TITLE,
        "version": APP_VERSION,
    }

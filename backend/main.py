from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.browser_manager import browser_manager


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Manage application-wide startup and shutdown tasks."""
    await browser_manager.start()
    yield
    await browser_manager.stop()


app = FastAPI(
    title="SEO Checker API",
    version="0.1.0",
    description="Backend API for the SEO Audit Tool.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health", summary="Health check")
async def health_check():
    return {"status": "ok"}

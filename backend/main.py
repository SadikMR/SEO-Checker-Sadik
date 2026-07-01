from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SEO Checker API",
    version="0.1.0",
    description="Backend API for the SEO Audit Tool.",
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

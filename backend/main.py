from fastapi import FastAPI

app = FastAPI(
    title="SEO Checker API",
    version="0.1.0",
    description="Backend API for the SEO Audit Tool.",
)


@app.get("/health", summary="Health check")
async def health_check():
    return {"status": "ok"}

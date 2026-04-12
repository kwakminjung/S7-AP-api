import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

APP_MODE = os.getenv("APP_MODE", "aplist")

if APP_MODE == "aplist":
    from app.api.aplist_api import router as api_router, aplist_lifespan as lifespan
elif APP_MODE == "template":
    from app.api.template_api import router as api_router, template_lifespan as lifespan

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "mode": APP_MODE}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content="", media_type="image/x-icon")
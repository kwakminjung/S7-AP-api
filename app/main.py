import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.api.aplist_api import router as aplist_api, aplist_lifespan
from app.api.template_api import router as template_api, template_lifespan

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "mode": os.getenv("APP_MODE", "unknown")}

APP_MODE = os.getenv("APP_MODE", "aplist")

if APP_MODE == "aplist":
    app = FastAPI(lifespan=aplist_lifespan)
    app.include_router(aplist_api)
elif APP_MODE == "template":
    app = FastAPI(lifespan=template_lifespan)
    app.include_router(template_api)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content="", media_type="image/x-icon")
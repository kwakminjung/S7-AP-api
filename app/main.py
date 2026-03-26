import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.aplist_api import app.api as aplist_api
from app.api.template_api import app.api as template_api

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "mode": os.getenv("APP_MODE", "unknown")}

APP_MODE = os.getenv("APP_MODE", "aplist")

if APP_MODE == "aplist":
    app.include_router(aplist_api)
elif APP_MODE == "template":
    app.include_router(aplist_api)
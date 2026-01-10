from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.config as config
from app.api.ingest import router as ingest_router
from app.api.delete import router as delete_router

# ==================================================
# App initialization
# ==================================================

app = FastAPI(
    title="ChattyDevs Core",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
config.validate_required()

# ==================================================
# Middleware
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================================================
# Routers
# ==================================================

app.include_router(
    ingest_router,
    prefix="/projects",
    tags=["Ingestion"],
)

app.include_router(
    delete_router,
    prefix="/projects",
    tags=["Deletion"],
)

# ==================================================
# Health check
# ==================================================

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "chattydevs-core",
        "environment": config.APP_ENV,
    }

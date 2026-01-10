from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field

from app.services.crawl import crawl_site
from app.services.chunk import chunk_text
from app.services.embed_and_upsert import upsert_chunks
import app.config as config
from fastapi import Depends
from app.security import verify_internal_token

router = APIRouter()


# ================== REQUEST SCHEMA ==================

class IngestRequest(BaseModel):
    project_id: str = Field(..., min_length=3)
    start_url: HttpUrl
    max_pages: int = Field(
        default=config.CRAWL_MAX_PAGES,
        ge=1,
        le=200,
    )
    chunk_token_size: int = Field(
        default=config.CHUNK_TOKEN_SIZE,
        ge=100,
        le=1000,
    )


# ================== RESPONSE SCHEMA ==================

class IngestResponse(BaseModel):
    project_id: str
    pages_crawled: int
    chunks_indexed: int


# ================== ROUTE ==================

@router.post(
    "/ingest",
    response_model=IngestResponse,
    tags=["Projects"],
)
def ingest_project(
    req: IngestRequest,
    _: None = Depends(verify_internal_token)
):
    """
    Crawl a website, chunk content, embed, and store in vector DB.
    """

    try:
        pages = crawl_site(
            start_url=str(req.start_url),
            max_pages=req.max_pages,
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal error during crawling"
        )


    total_chunks = 0

    for page in pages:
        text = page.get("text", "").strip()
        url = page.get("url")

        if not text:
            continue

        chunks = chunk_text(
            text=text,
            max_tokens=req.chunk_token_size,
        )

        if not chunks:
            continue

        inserted = upsert_chunks(
            project_id=req.project_id,
            url=url,
            chunks=chunks,
        )

        total_chunks += inserted

    return IngestResponse(
        project_id=req.project_id,
        pages_crawled=len(pages),
        chunks_indexed=total_chunks,
    )

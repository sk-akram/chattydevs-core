import uuid
import requests
from typing import List

import app.config as config


# ================== CONSTANTS ==================

QDRANT_HEADERS = {
    "Content-Type": "application/json",
    "api-key": config.QDRANT_API_KEY,
}

GEMINI_EMBED_ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"{config.GEMINI_EMBED_MODEL}:embedContent"
)

# ===============================================


import time

def embed_text(text: str) -> List[float]:
    for attempt in range(3):
        try:
            response = requests.post(
                GEMINI_EMBED_ENDPOINT,
                params={"key": config.GEMINI_API_KEY},
                headers={"Content-Type": "application/json"},
                json={
                    "content": {
                        "parts": [{"text": text}]
                    }
                },
                timeout=20,
            )

            response.raise_for_status()
            return response.json()["embedding"]["values"]

        except Exception:
            if attempt == 2:
                raise
            time.sleep(1.5)


def _build_points(
    project_id: str,
    url: str,
    chunks: List[str],
):
    """
    Generator that converts text chunks into Qdrant-ready points.
    """
    for chunk in chunks:
        embedding = embed_text(chunk)

        yield {
            "id": str(uuid.uuid4()),
            "vector": embedding,
            "payload": {
                "project_id": project_id,
                "url": url,
                "content": chunk,
            },
        }


def upsert_chunks(
    project_id: str,
    url: str,
    chunks: List[str],
) -> int:
    """
    Embed and upsert chunks into Qdrant.

    Returns:
        int: number of vectors inserted
    """

    if not project_id or not url or not chunks:
        raise ValueError("project_id, url and chunks are required")

    inserted = 0
    batch: List[dict] = []

    for point in _build_points(project_id, url, chunks):
        batch.append(point)

        if len(batch) >= config.QDRANT_UPSERT_BATCH_SIZE:
            _upsert_batch(batch)
            inserted += len(batch)
            batch.clear()

    if batch:
        _upsert_batch(batch)
        inserted += len(batch)

    return inserted


def _upsert_batch(points: List[dict]) -> None:
    """
    Perform a batch upsert to Qdrant.
    """

    response = requests.put(
        f"{config.QDRANT_URL}/collections/{config.QDRANT_COLLECTION_NAME}/points",
        headers=QDRANT_HEADERS,
        json={"points": points},
        timeout=30,
    )

    response.raise_for_status()

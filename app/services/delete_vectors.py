import requests
import time
from typing import List, Optional

import app.config as config


# ================== CONSTANTS ==================

QDRANT_HEADERS = {
    "Content-Type": "application/json",
    "api-key": config.QDRANT_API_KEY,
}

# ===============================================


def _post_with_retry(url, headers, json, timeout):
    for attempt in range(3):
        try:
            res = requests.post(url, headers=headers, json=json, timeout=timeout)
            res.raise_for_status()
            return res
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1.5)


def _scroll_project_points(project_id: str) -> List[str]:
    """
    Fetch all Qdrant point IDs for a given project_id using scroll API.
    Cloud-Qdrant safe.
    """

    point_ids: List[str] = []
    offset: Optional[str] = None

    while True:
        payload = {
            "limit": config.QDRANT_SCROLL_LIMIT,
            "with_payload": False,
            "filter": {
                "must": [
                    {
                        "key": "project_id",
                        "match": {"value": project_id},
                    }
                ]
            },
        }

        if offset:
            payload["offset"] = offset

        response = _post_with_retry(
            url=f"{config.QDRANT_URL}/collections/{config.QDRANT_COLLECTION_NAME}/points/scroll",
            headers=QDRANT_HEADERS,
            json=payload,
            timeout=15,
        )

        result = response.json().get("result", {})
        points = result.get("points", [])

        if not points:
            break

        for p in points:
            point_ids.append(p["id"])

        offset = result.get("next_page_offset")
        if not offset:
            break

    return point_ids


def delete_project_vectors(project_id: str) -> int:
    """
    Delete all vectors belonging to a project_id.

    Returns:
        int: number of deleted vectors
    """

    if not project_id:
        raise ValueError("project_id is required")

    point_ids = _scroll_project_points(project_id)

    if not point_ids:
        return 0

    _post_with_retry(
        url=f"{config.QDRANT_URL}/collections/{config.QDRANT_COLLECTION_NAME}/points/delete",
        headers=QDRANT_HEADERS,
        json={"points": point_ids},
        timeout=15,
    )

    return len(point_ids)

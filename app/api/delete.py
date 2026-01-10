from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.delete_vectors import delete_project_vectors


router = APIRouter()


# ================== REQUEST SCHEMA ==================

class DeleteRequest(BaseModel):
    project_id: str = Field(..., min_length=3)


# ================== RESPONSE SCHEMA ==================

class DeleteResponse(BaseModel):
    project_id: str
    vectors_deleted: int


# ================== ROUTE ==================

@router.post(
    "/delete",
    response_model=DeleteResponse,
    tags=["Projects"],
)
def delete_project(req: DeleteRequest):
    """
    Delete all vectors associated with a project_id.
    """

    try:
        deleted_count = delete_project_vectors(req.project_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vector deletion failed: {str(e)}",
        )

    if deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="No vectors found for this project_id",
        )

    return DeleteResponse(
        project_id=req.project_id,
        vectors_deleted=deleted_count,
    )

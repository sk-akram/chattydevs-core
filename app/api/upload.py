from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.chunk import chunk_text
from app.services.embed_and_upsert import upsert_chunks

import io
import csv
from PyPDF2 import PdfReader

router = APIRouter()

@router.post("/upload")
async def upload_file(
    project_id: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        content = await file.read()
        text = extract_text(file.filename, content)

        if not text.strip():
            raise HTTPException(400, "No readable text found")

        chunks = chunk_text(text)
        inserted = upsert_chunks(project_id, file.filename, chunks)

        return {
            "project_id": project_id,
            "filename": file.filename,
            "chunks_indexed": inserted,
        }

    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")


def extract_text(filename: str, content: bytes) -> str:
    ext = filename.lower().split(".")[-1]

    if ext == "txt":
        return content.decode("utf-8", errors="ignore")

    if ext == "csv":
        text = ""
        reader = csv.reader(io.StringIO(content.decode()))
        for row in reader:
            text += " ".join(row) + "\n"
        return text

    if ext == "pdf":
        text = ""
        reader = PdfReader(io.BytesIO(content))
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    raise ValueError("Unsupported file type")

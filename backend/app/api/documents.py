
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4

from app.services.document_service import process_document
from app.services.business_extractor import extract_business_fields
from app.services.document_storage_service import (
    save_document,
    get_all_documents,
    get_document_by_id
)

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".xlsx"}
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and XLSX files are supported"
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 10 MB"
        )

    saved_filename = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / saved_filename

    try:
        file_path.write_bytes(content)

        result = process_document(str(file_path))
        business_data = extract_business_fields(result["content"])

        saved_document = save_document(result, business_data)

        return {
            "message": "Document uploaded and saved successfully",
            "original_filename": file.filename,
            "document": result,
            "business_data": business_data,
            "saved_document": saved_document
        }

    except Exception:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail="Document processing or storage failed"
        )

    finally:
        await file.close()


@router.get("/documents")
def list_documents():
    return {
        "total_documents": len(get_all_documents()),
        "documents": get_all_documents()
    }


@router.get("/documents/{document_id}")
def retrieve_document(document_id: str):
    document = get_document_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document

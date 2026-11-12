
import json
from datetime import datetime
from uuid import uuid4

from app.db.database import get_connection


def save_document(document: dict, business_data: dict) -> dict:
    document_record = {
        "document_id": f"DOC-{uuid4().hex[:10].upper()}",
        "filename": document["filename"],
        "file_type": document["file_type"],
        "document_type": (
            "Purchase Order" if business_data.get("po_number")
            else "Invoice" if business_data.get("invoice_number")
            else "Unknown"
        ),
        "extracted_data": business_data,
        "upload_time": datetime.now().isoformat()
    }

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO documents
            (document_id, filename, file_type, document_type,
             extracted_data, upload_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                document_record["document_id"],
                document_record["filename"],
                document_record["file_type"],
                document_record["document_type"],
                json.dumps(business_data),
                document_record["upload_time"]
            )
        )
        connection.commit()
    finally:
        connection.close()

    return document_record


def get_all_documents() -> list:
    connection = get_connection()

    try:
        rows = connection.execute(
            "SELECT * FROM documents ORDER BY id DESC"
        ).fetchall()

        return [
            {
                "document_id": row["document_id"],
                "filename": row["filename"],
                "file_type": row["file_type"],
                "document_type": row["document_type"],
                "extracted_data": json.loads(row["extracted_data"]),
                "upload_time": row["upload_time"]
            }
            for row in rows
        ]
    finally:
        connection.close()


def get_document_by_id(document_id: str):
    connection = get_connection()

    try:
        row = connection.execute(
            "SELECT * FROM documents WHERE document_id = ?",
            (document_id,)
        ).fetchone()

        if row is None:
            return None

        return {
            "document_id": row["document_id"],
            "filename": row["filename"],
            "file_type": row["file_type"],
            "document_type": row["document_type"],
            "extracted_data": json.loads(row["extracted_data"]),
            "upload_time": row["upload_time"]
        }
    finally:
        connection.close()

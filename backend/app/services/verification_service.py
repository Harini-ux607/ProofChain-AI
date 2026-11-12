from datetime import datetime
from uuid import uuid4

from app.db.database import get_connection
from app.services.audit_service import create_audit_log


def verify_execution(execution_id: str) -> dict:
    connection = get_connection()

    try:
        execution = connection.execute(
            "SELECT * FROM executions WHERE execution_id = ?",
            (execution_id,)
        ).fetchone()

        if execution is None:
            return {
                "verification_status": "failed",
                "message": "Execution record not found."
            }

        if execution["execution_status"] != "executed":
            return {
                "verification_status": "failed",
                "message": "Execution was not completed."
            }

        existing = connection.execute(
            "SELECT * FROM verifications WHERE execution_id = ?",
            (execution_id,)
        ).fetchone()

        if existing is not None:
            return {
                "verification_id": existing["verification_id"],
                "execution_id": existing["execution_id"],
                "verification_status": existing["verification_status"],
                "message": existing["message"],
                "verified_at": existing["verified_at"]
            }

        verification = {
            "verification_id": f"VER-{uuid4().hex[:10].upper()}",
            "execution_id": execution_id,
            "verification_status": "verified",
            "message": "Execution record exists and has executed status.",
            "verified_at": datetime.now().isoformat()
        }

        connection.execute(
            """
            INSERT INTO verifications
            (verification_id, execution_id, verification_status,
             message, verified_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                verification["verification_id"],
                verification["execution_id"],
                verification["verification_status"],
                verification["message"],
                verification["verified_at"]
            )
        )

        connection.commit()

    finally:
        connection.close()

    create_audit_log("EXECUTION_VERIFIED", verification)

    return verification


def get_all_verifications() -> list:
    connection = get_connection()

    try:
        rows = connection.execute(
            "SELECT * FROM verifications ORDER BY id DESC"
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()
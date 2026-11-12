
import json
from datetime import datetime
from uuid import uuid4

from app.db.database import get_connection
from app.services.audit_service import create_audit_log


def create_approval_request(investigation: dict) -> dict:

    if investigation.get("investigation_status") != "review_required":
        return {
            "approval_status": "not_required",
            "message": "No approval is required."
        }

    approval = {
        "approval_id": f"APR-{uuid4().hex[:10].upper()}",
        "approval_status": "pending",
        "reason": investigation.get("explanation", ""),
        "evidence": investigation.get("evidence", []),
        "created_at": datetime.now().isoformat()
    }

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO approvals
            (approval_id, approval_status, reason, evidence, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                approval["approval_id"],
                approval["approval_status"],
                approval["reason"],
                json.dumps(approval["evidence"]),
                approval["created_at"]
            )
        )
        connection.commit()
    finally:
        connection.close()

    create_audit_log("APPROVAL_CREATED", approval)

    return approval


def review_approval(approval_id: str, decision: str) -> dict:

    decision = decision.lower()

    if decision not in ["approve", "reject"]:
        return {"status": "error", "message": "Decision must be approve or reject."}

    new_status = "approved" if decision == "approve" else "rejected"

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE approvals
            SET approval_status = ?
            WHERE approval_id = ? AND approval_status = 'pending'
            """,
            (new_status, approval_id)
        )

        connection.commit()

        if cursor.rowcount == 0:
            existing = connection.execute(
                "SELECT approval_status FROM approvals WHERE approval_id = ?",
                (approval_id,)
            ).fetchone()

            if existing is None:
                return {"status": "error", "message": "Approval request not found."}

            return {
                "status": "error",
                "message": "This approval has already been reviewed."
            }

    finally:
        connection.close()

    result = {
        "approval_id": approval_id,
        "approval_status": new_status,
        "message": f"Approval request {new_status} successfully."
    }

    create_audit_log("APPROVAL_REVIEWED", result)

    return result


def get_all_approvals() -> list:

    connection = get_connection()

    try:
        rows = connection.execute(
            "SELECT * FROM approvals ORDER BY id DESC"
        ).fetchall()

        return [
            {
                "approval_id": row["approval_id"],
                "approval_status": row["approval_status"],
                "reason": row["reason"],
                "evidence": json.loads(row["evidence"]),
                "created_at": row["created_at"]
            }
            for row in rows
        ]
    finally:
        connection.close()


def execute_approved_action(approval_id: str) -> dict:

    connection = get_connection()

    try:
        approval = connection.execute(
            "SELECT * FROM approvals WHERE approval_id = ?",
            (approval_id,)
        ).fetchone()

        if approval is None:
            return {"execution_status": "blocked", "message": "Approval not found."}

        if approval["approval_status"] != "approved":
            return {
                "execution_status": "blocked",
                "message": "Action cannot be executed without approval."
            }

        execution = {
            "execution_id": f"EXE-{uuid4().hex[:10].upper()}",
            "approval_id": approval_id,
            "execution_status": "executed",
            "action": "Hold invoice payment for verification",
            "executed_at": datetime.now().isoformat()
        }

        connection.execute(
            """
            INSERT INTO executions
            (execution_id, approval_id, execution_status, action, executed_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                execution["execution_id"],
                execution["approval_id"],
                execution["execution_status"],
                execution["action"],
                execution["executed_at"]
            )
        )

        connection.commit()

    except Exception as error:
        if "UNIQUE constraint failed" in str(error):
            return {
                "execution_status": "blocked",
                "message": "This approval has already been executed."
            }
        raise

    finally:
        connection.close()

    create_audit_log("ACTION_EXECUTED", execution)

    return execution


def get_all_executions() -> list:

    connection = get_connection()

    try:
        rows = connection.execute(
            "SELECT * FROM executions ORDER BY id DESC"
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        connection.close()

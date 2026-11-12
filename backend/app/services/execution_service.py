from uuid import uuid4


def execute_approved_action(approval_request: dict) -> dict:
    """Execute an action only after human approval."""

    if approval_request.get("approval_status") != "approved":
        return {
            "execution_status": "blocked",
            "message": "Action cannot be executed without approval."
        }

    execution_id = f"EXE-{uuid4().hex[:8].upper()}"

    return {
        "execution_id": execution_id,
        "execution_status": "executed",
        "action": "Hold invoice payment for verification",
        "message": "Approved action executed successfully."
    }
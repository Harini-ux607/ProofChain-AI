
def create_approval_request(investigation: dict) -> dict:
    """Create a human approval request."""

    if investigation["investigation_status"] != "review_required":
        return {
            "approval_status": "not_required",
            "message": "No approval is required."
        }

    return {
        "approval_id": "APR-1001",
        "approval_status": "pending",
        "proposed_action": "Hold invoice payment for verification",
        "reason": investigation["explanation"],
        "evidence": investigation["evidence"],
        "message": "Waiting for human approval."
    }


def review_approval(approval_request: dict, decision: str) -> dict:
    """Approve or reject a pending request."""

    if approval_request["approval_status"] != "pending":
        return {
            "status": "error",
            "message": "This request has already been reviewed."
        }

    decision = decision.lower()

    if decision == "approve":
        approval_request["approval_status"] = "approved"

    elif decision == "reject":
        approval_request["approval_status"] = "rejected"

    else:
        return {
            "status": "error",
            "message": "Decision must be approve or reject."
        }

    return {
        "approval_id": approval_request["approval_id"],
        "approval_status": approval_request["approval_status"],
        "message": f"Approval request {decision}d successfully."
    }

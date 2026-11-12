
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.document_storage_service import get_document_by_id
from app.services.comparison_service import compare_documents
from app.services.investigation_service import investigate_discrepancy

from app.services.workflow_service import (
    create_approval_request,
    review_approval,
    get_all_approvals,
    execute_approved_action,
    get_all_executions
)

from app.services.verification_service import (
    verify_execution,
    get_all_verifications
)

from app.services.audit_service import get_audit_logs

router = APIRouter()


class ApprovalReview(BaseModel):
    decision: str


class DocumentComparisonRequest(BaseModel):
    po_document_id: str
    invoice_document_id: str


@router.post("/approvals")
def create_approval(investigation: dict):
    return create_approval_request(investigation)


@router.get("/approvals")
def list_approvals():
    return {"approvals": get_all_approvals()}


@router.post("/approvals/{approval_id}/review")
def review_approval_api(approval_id: str, request: ApprovalReview):
    return review_approval(approval_id, request.decision)


@router.post("/executions/{approval_id}")
def execute_action(approval_id: str):
    return execute_approved_action(approval_id)


@router.get("/executions")
def list_executions():
    return {"executions": get_all_executions()}


@router.post("/verifications/{execution_id}")
def verify_action(execution_id: str):
    return verify_execution(execution_id)


@router.get("/verifications")
def list_verifications():
    return {"verifications": get_all_verifications()}


@router.get("/audit-logs")
def list_audit_logs():
    return {"audit_logs": get_audit_logs()}


@router.post("/compare")
def compare_uploaded_documents(request: DocumentComparisonRequest):

    po_document = get_document_by_id(request.po_document_id)
    invoice_document = get_document_by_id(request.invoice_document_id)

    if po_document is None or invoice_document is None:
        raise HTTPException(
            status_code=404,
            detail="Purchase Order or Invoice document not found."
        )

    po_data = po_document["extracted_data"]
    invoice_data = invoice_document["extracted_data"]

    if not po_data.get("po_number"):
        raise HTTPException(
            status_code=400,
            detail="The selected document does not appear to be a Purchase Order."
        )

    if not invoice_data.get("invoice_number"):
        raise HTTPException(
            status_code=400,
            detail="The selected document does not appear to be an Invoice."
        )

    comparison = compare_documents(po_data, invoice_data)

    investigation = investigate_discrepancy(
        po_data,
        invoice_data,
        comparison
    )

    approval = create_approval_request(investigation)

    return {
        "purchase_order": {
            "document_id": po_document["document_id"],
            "filename": po_document["filename"],
            "data": po_data
        },
        "invoice": {
            "document_id": invoice_document["document_id"],
            "filename": invoice_document["filename"],
            "data": invoice_data
        },
        "comparison": comparison,
        "investigation": investigation,
        "approval": approval
    }

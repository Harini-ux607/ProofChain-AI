
from app.services.approval_service import (
    create_approval_request,
    review_approval
)

investigation = {
    "investigation_status": "review_required",
    "explanation": "Invoice contains 20 more units than the Purchase Order.",
    "evidence": [
        {
            "source": "Purchase Order",
            "observation": "Ordered quantity: 100"
        },
        {
            "source": "Invoice",
            "observation": "Invoiced quantity: 120"
        }
    ]
}

# Create approval request
approval = create_approval_request(investigation)

print("Approval Request:")
print(approval)

# Human approves the request
result = review_approval(approval, "approve")

print("\nApproval Result:")
print(result)

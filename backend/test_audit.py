from app.db.database import initialize_database
from app.services.audit_service import (
    create_audit_log,
    get_audit_logs
)

initialize_database()

audit = create_audit_log(
    "INVOICE_APPROVED",
    {
        "approval_id": "APR-1001",
        "invoice_number": "INV-5001",
        "status": "approved"
    }
)

print("Saved Audit Record:")
print(audit)

print("\nAll Audit Records:")
print(get_audit_logs())
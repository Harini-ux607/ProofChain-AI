
from app.db.database import initialize_database
from app.services.document_storage_service import (
    save_document,
    get_all_documents
)

initialize_database()

document = {
    "filename": "sample_purchase_order.xlsx",
    "file_type": ".xlsx"
}

business_data = {
    "po_number": "PO-1001",
    "quantity": 100,
    "unit_price": "45000"
}

saved = save_document(document, business_data)

print("Saved Document:")
print(saved)

print("\nAll Stored Documents:")
print(get_all_documents())

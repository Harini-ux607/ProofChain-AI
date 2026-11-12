
from app.services.comparison_service import compare_documents

# Purchase Order details
po_data = {
    "quantity": 100,
    "unit_price": "45000"
}

# Invoice details
invoice_data = {
    "quantity": 120,
    "unit_price": "45000"
}

result = compare_documents(po_data, invoice_data)

print("Document Comparison Result:")
print(result)


from app.services.comparison_service import compare_documents
from app.services.investigation_service import investigate_discrepancy

po_data = {
    "quantity": 100,
    "unit_price": "45000"
}

invoice_data = {
    "quantity": 120,
    "unit_price": "45000"
}

comparison_result = compare_documents(po_data, invoice_data)

investigation = investigate_discrepancy(
    po_data,
    invoice_data,
    comparison_result
)

print("Investigation Report:")
print(investigation)

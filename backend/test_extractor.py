
from app.services.business_extractor import extract_business_fields

sample_text = """
Sheet: Purchase Order

PO Number  Product  Quantity  Unit Price
PO-1001    Laptop   100       45000
PO-1002    Keyboard 50        1200
"""

result = extract_business_fields(sample_text)

print("Extracted Business Information:")
print(result)

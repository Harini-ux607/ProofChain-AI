
import re
import logging

from app.services.ai_extraction_service import extract_with_ai

logger = logging.getLogger(__name__)


def clean_number(value):
    """Convert a numeric string into a clean number."""

    if value is None:
        return None

    value = str(value).strip()
    value = re.sub(r"[₹$,]", "", value)

    if not value:
        return None

    try:
        number = float(value)

        if number.is_integer():
            return int(number)

        return number

    except ValueError:
        return None


def get_field(row, *names):
    """Find a field using alternative column names."""

    normalized = {
        re.sub(r"[^a-z0-9]", "", key.lower()): value
        for key, value in row.items()
    }

    for name in names:
        key = re.sub(r"[^a-z0-9]", "", name.lower())

        if key in normalized:
            return normalized[key]

    return None


def extract_business_fields(text: str) -> dict:
    """
    Extract business document fields using AI.
    Use rule-based extraction when AI is unavailable.
    """

    try:
        result = extract_with_ai(text)

        if result.get("invoice_number"):
            result["document_type"] = "Invoice"

        elif result.get("po_number"):
            result["document_type"] = "Purchase Order"

        return result

    except Exception as error:
        logger.exception(
            "AI extraction failed. Using rule-based fallback."
        )

        fallback_data = extract_with_rules(text)
        fallback_data["extraction_method"] = "rule_based_fallback"
        fallback_data["ai_error"] = str(error)

        return fallback_data


def extract_with_rules(text: str) -> dict:
    """Extract document information using labelled text rows."""

    po_match = re.search(
        r"\bPO-\d+\b",
        text,
        re.IGNORECASE
    )

    invoice_match = re.search(
        r"\bINV-\d+\b",
        text,
        re.IGNORECASE
    )

    line_items = []

    # Extract every structured Excel row.
    for line in text.splitlines():

        if not line.strip().upper().startswith("ROW:"):
            continue

        row = {}

        # Example:
        # ROW: Product=Laptop | Quantity=100 | Unit Price=45000
        content = line.split(":", 1)[1]

        for part in content.split("|"):

            if "=" not in part:
                continue

            key, value = part.split("=", 1)
            row[key.strip()] = value.strip()

        description = get_field(
            row,
            "Product",
            "Description",
            "Item",
            "Product Name",
            "Item Description"
        )

        quantity = clean_number(
            get_field(row, "Quantity", "Qty")
        )

        unit_price = clean_number(
            get_field(row, "Unit Price", "Price", "Rate")
        )

        line_total = clean_number(
            get_field(
                row,
                "Line Total",
                "Amount",
                "Total",
                "Line Amount"
            )
        )

        # Ignore header or empty rows.
        if description is None and quantity is None:
            continue

        line_items.append({
            "description": description,
            "quantity": quantity,
            "unit_price": unit_price,
            "line_total": line_total
        })

    # Extract document type.
    if invoice_match:
        document_type = "Invoice"

    elif po_match:
        document_type = "Purchase Order"

    else:
        document_type = "Unknown"

    # Preserve compatibility with existing single-item fields.
    first_item = line_items[0] if line_items else {}

    quantity = first_item.get("quantity")
    unit_price = first_item.get("unit_price")

    # Extract only an explicitly labelled document total.
    total_match = re.search(
        r"(?:Grand\s+)?Total\s*Amount\s*[:=]?\s*"
        r"(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d{1,2})?)",
        text,
        re.IGNORECASE
    )

    total_amount = (
        clean_number(total_match.group(1))
        if total_match
        else None
    )

    # Find explicitly labelled document identifiers.
    if not po_match:
        po_match = re.search(
            r"PO\s*(?:Number|No\.?)\s*[:=]\s*(PO-\d+)",
            text,
            re.IGNORECASE
        )

    if not invoice_match:
        invoice_match = re.search(
            r"Invoice\s*(?:Number|No\.?)\s*[:=]\s*(INV-\d+)",
            text,
            re.IGNORECASE
        )

    missing_fields = []

    if document_type == "Invoice":
        if not invoice_match:
            missing_fields.append("invoice_number")

        if not po_match:
            missing_fields.append("po_number")

    if not line_items:
        missing_fields.append("line_items")

    if quantity is None:
        missing_fields.append("quantity")

    if unit_price is None:
        missing_fields.append("unit_price")

    if total_amount is None:
        missing_fields.append("total_amount")

    return {
        "document_type": document_type,
        "po_number": po_match.group(0) if po_match else None,
        "invoice_number": (
            invoice_match.group(0) if invoice_match else None
        ),
        "vendor_name": None,
        "customer_name": None,
        "currency": None,
        "quantity": quantity,
        "unit_price": unit_price,
        "total_amount": total_amount,
        "line_items": line_items,
        "confidence": 0.85 if line_items else 0.0,
        "missing_fields": missing_fields,
        "extraction_notes": [
            "Rule-based extraction was used.",
            f"Extracted {len(line_items)} line item(s)."
        ]
    }

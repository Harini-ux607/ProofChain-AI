
import re


def normalize_name(value):
    """Normalize product names for matching."""

    if value is None:
        return ""

    return re.sub(
        r"[^a-z0-9]",
        "",
        str(value).lower()
    )


def to_number(value):
    """Convert numeric values safely."""

    if value is None:
        return None

    try:
        cleaned = re.sub(
            r"[₹$, ]",
            "",
            str(value)
        )

        return float(cleaned)

    except (ValueError, TypeError):
        return None


def compare_documents(po_data: dict, invoice_data: dict) -> dict:
    """Compare Purchase Order and Invoice documents."""

    po_items = po_data.get("line_items") or []
    invoice_items = invoice_data.get("line_items") or []

    # Use multi-item comparison when both documents have line items.
    if po_items and invoice_items:
        return compare_line_items(
            po_data,
            invoice_data,
            po_items,
            invoice_items
        )

    # If only one document has line items, comparison is incomplete.
    if po_items or invoice_items:
        return {
            "status": "incomplete",
            "message": "Line items are missing from one of the documents.",
            "discrepancies": [],
            "line_items_checked": 0
        }

    # Backward-compatible comparison for older single-item documents.
    return compare_legacy_fields(po_data, invoice_data)


def compare_line_items(
    po_data,
    invoice_data,
    po_items,
    invoice_items
):
    discrepancies = []
    incomplete = False
    matched_items = 0

    # Group invoice items by normalized product description.
    invoice_lookup = {}

    for item in invoice_items:

        name = normalize_name(item.get("description"))

        if not name:
            incomplete = True
            continue

        invoice_lookup.setdefault(name, []).append(item)

    used_invoice_items = set()

    # Compare each PO item with its matching invoice item.
    for po_item in po_items:

        description = po_item.get("description")
        name = normalize_name(description)

        if not name:
            incomplete = True
            continue

        matching_items = invoice_lookup.get(name, [])

        invoice_item = None

        for candidate in matching_items:

            candidate_id = id(candidate)

            if candidate_id not in used_invoice_items:
                invoice_item = candidate
                used_invoice_items.add(candidate_id)
                break

        if invoice_item is None:

            discrepancies.append({
                "field": "missing_item_in_invoice",
                "item_description": description,
                "purchase_order": po_item,
                "invoice": None
            })

            continue

        matched_items += 1

        # Compare quantity.
        po_quantity = to_number(po_item.get("quantity"))
        invoice_quantity = to_number(
            invoice_item.get("quantity")
        )

        if po_quantity is None or invoice_quantity is None:
            incomplete = True

        elif po_quantity != invoice_quantity:

            discrepancies.append({
                "field": "quantity",
                "item_description": description,
                "purchase_order": po_quantity,
                "invoice": invoice_quantity,
                "difference": invoice_quantity - po_quantity
            })

        # Compare unit price.
        po_price = to_number(po_item.get("unit_price"))
        invoice_price = to_number(
            invoice_item.get("unit_price")
        )

        if po_price is None or invoice_price is None:
            incomplete = True

        elif po_price != invoice_price:

            discrepancies.append({
                "field": "unit_price",
                "item_description": description,
                "purchase_order": po_price,
                "invoice": invoice_price
            })

        # Compare line total only when both values are available.
        po_total = to_number(po_item.get("line_total"))
        invoice_total = to_number(
            invoice_item.get("line_total")
        )

        if po_total is not None and invoice_total is not None:

            if po_total != invoice_total:

                discrepancies.append({
                    "field": "line_total",
                    "item_description": description,
                    "purchase_order": po_total,
                    "invoice": invoice_total
                })

    # Detect additional invoice items.
    for name, items in invoice_lookup.items():

        for invoice_item in items:

            if id(invoice_item) not in used_invoice_items:

                discrepancies.append({
                    "field": "extra_item_in_invoice",
                    "item_description": invoice_item.get("description"),
                    "purchase_order": None,
                    "invoice": invoice_item
                })

    # Compare document totals if both are available.
    po_amount = to_number(po_data.get("total_amount"))
    invoice_amount = to_number(
        invoice_data.get("total_amount")
    )

    if po_amount is not None and invoice_amount is not None:

        if po_amount != invoice_amount:

            discrepancies.append({
                "field": "total_amount",
                "purchase_order": po_amount,
                "invoice": invoice_amount
            })

    if discrepancies:

        return {
            "status": "mismatch",
            "message": "Differences found between documents.",
            "discrepancies": discrepancies,
            "line_items_checked": matched_items
        }

    if incomplete:

        return {
            "status": "incomplete",
            "message": "Some line-item information is missing.",
            "discrepancies": [],
            "line_items_checked": matched_items
        }

    return {
        "status": "matched",
        "message": "All matched line items and available totals match successfully.",
        "discrepancies": [],
        "line_items_checked": matched_items
    }


def compare_legacy_fields(po_data, invoice_data):
    """Preserve the previous single-item comparison."""

    discrepancies = []

    po_quantity = to_number(po_data.get("quantity"))
    invoice_quantity = to_number(
        invoice_data.get("quantity")
    )

    if po_quantity is not None and invoice_quantity is not None:

        if po_quantity != invoice_quantity:

            discrepancies.append({
                "field": "quantity",
                "purchase_order": po_quantity,
                "invoice": invoice_quantity,
                "difference": invoice_quantity - po_quantity
            })

    po_price = to_number(po_data.get("unit_price"))
    invoice_price = to_number(
        invoice_data.get("unit_price")
    )

    if po_price is not None and invoice_price is not None:

        if po_price != invoice_price:

            discrepancies.append({
                "field": "unit_price",
                "purchase_order": po_price,
                "invoice": invoice_price
            })

    po_amount = to_number(po_data.get("total_amount"))
    invoice_amount = to_number(
        invoice_data.get("total_amount")
    )

    if po_amount is not None and invoice_amount is not None:

        if po_amount != invoice_amount:

            discrepancies.append({
                "field": "total_amount",
                "purchase_order": po_amount,
                "invoice": invoice_amount
            })

    if discrepancies:

        return {
            "status": "mismatch",
            "message": "Differences found between documents.",
            "discrepancies": discrepancies
        }

    if (
        po_quantity is None
        or invoice_quantity is None
        or po_price is None
        or invoice_price is None
    ):

        return {
            "status": "incomplete",
            "message": "Some required information is missing for comparison.",
            "discrepancies": []
        }

    return {
        "status": "matched",
        "message": "Compared fields match successfully.",
        "discrepancies": []
    }

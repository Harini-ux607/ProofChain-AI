
def investigate_discrepancy(po_data, invoice_data, comparison_result):

    status = comparison_result.get("status")

    if status == "incomplete":
        return {
            "investigation_status": "incomplete",
            "explanation": comparison_result["message"],
            "evidence": [],
            "recommendation": (
                "Review the documents and provide missing information."
            )
        }

    if status == "matched":
        return {
            "investigation_status": "no_issue",
            "explanation": (
                "No discrepancy was detected in the compared fields."
            ),
            "evidence": [],
            "recommendation": "Continue normal processing."
        }

    evidence = []

    for item in comparison_result.get("discrepancies", []):

        evidence_item = {
            "field": item.get("field"),
            "purchase_order_value": item.get("purchase_order"),
            "invoice_value": item.get("invoice")
        }

        # Preserve the product name for line-item discrepancies.
        if item.get("item_description"):
            evidence_item["item_description"] = (
                item["item_description"]
            )

        # Preserve quantity difference when available.
        if "difference" in item:
            evidence_item["difference"] = item["difference"]

        evidence.append(evidence_item)

    explanation = (
        f"{len(evidence)} discrepancy field(s) were detected "
        "between the Purchase Order and Invoice."
    )

    return {
        "investigation_status": "review_required",
        "explanation": explanation,
        "evidence": evidence,
        "recommendation": (
            "Hold invoice payment and ask the responsible team "
            "to verify the differences before approval."
        )
    }

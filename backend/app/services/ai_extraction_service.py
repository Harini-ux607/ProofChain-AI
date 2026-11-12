
import json
import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


def extract_with_ai(document_text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from backend/.env")

    if not document_text.strip():
        raise ValueError("Document contains no readable text.")

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are an expert business document data extraction assistant.

Extract information from this Purchase Order or Invoice.

Rules:
1. Never invent missing information.
2. Return null for unavailable values.
3. Identify whether this is a Purchase Order, Invoice, or Unknown.
4. Extract every available line item.
5. Quantity must be a number or null.
6. Prices and amounts must be numeric values or null.
7. Preserve document numbers exactly.
8. Do not calculate missing values.
9. Confidence must be a number between 0 and 1.
10. Return valid JSON only.

Required JSON structure:

{{
    "document_type": "Purchase Order, Invoice, or Unknown",
    "po_number": null,
    "invoice_number": null,
    "vendor_name": null,
    "customer_name": null,
    "currency": null,
    "quantity": null,
    "unit_price": null,
    "total_amount": null,
    "line_items": [
        {{
            "description": null,
            "quantity": null,
            "unit_price": null,
            "line_total": null
        }}
    ],
    "confidence": 0.0,
    "missing_fields": [],
    "extraction_notes": []
}}

Document text:

{document_text[:20000]}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Extract business document information accurately. Return JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0
    )

    response_text = response.choices[0].message.content

    if not response_text:
        raise ValueError("AI returned an empty response.")

    data = json.loads(response_text)

    # Keep the first line item compatible with our existing comparison service.
    line_items = data.get("line_items") or []

    if line_items:
        first_item = line_items[0]

        if data.get("quantity") is None:
            data["quantity"] = first_item.get("quantity")

        if data.get("unit_price") is None:
            data["unit_price"] = first_item.get("unit_price")

    data["extraction_method"] = "openai"

    return data

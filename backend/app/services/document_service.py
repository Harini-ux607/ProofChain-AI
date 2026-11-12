
import pymupdf
import pandas as pd
from pathlib import Path


def extract_pdf_text(file_path: str) -> str:
    """Extract text from a PDF document."""

    text = ""

    with pymupdf.open(file_path) as document:
        for page in document:
            text += page.get_text() + "\n"

    return text.strip()


def format_excel_value(value):
    """Convert Excel cell values into readable text."""

    if pd.isna(value):
        return None

    if isinstance(value, float) and value.is_integer():
        return str(int(value))

    return str(value).strip()


def extract_excel_data(file_path: str) -> str:
    """Extract Excel data as structured, labelled rows."""

    sheets = pd.read_excel(
        file_path,
        sheet_name=None
    )

    extracted_data = []

    for sheet_name, dataframe in sheets.items():

        extracted_data.append(f"Sheet: {sheet_name}")

        for _, row in dataframe.iterrows():

            row_values = []

            for column in dataframe.columns:

                value = format_excel_value(row[column])

                if value is not None and value != "":
                    row_values.append(
                        f"{str(column).strip()}={value}"
                    )

            if row_values:
                extracted_data.append(
                    "ROW: " + " | ".join(row_values)
                )

    return "\n".join(extracted_data)


def process_document(file_path: str) -> dict:
    """Identify the file type and extract its contents."""

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        content = extract_pdf_text(file_path)

    elif extension in [".xlsx", ".xls"]:
        content = extract_excel_data(file_path)

    else:
        raise ValueError("Unsupported file format")

    return {
        "filename": path.name,
        "file_type": extension,
        "content": content,
        "status": "processed"
    }

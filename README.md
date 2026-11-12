# ProofChain AI
### Business Document Intelligence & Workflow Automation

ProofChain AI is a full-stack application designed to simplify business document investigation and approval workflows. It helps users upload business documents, extract important information, identify discrepancies between Purchase Orders and Invoices, and manage approval and verification activities.

## Features

- **Document Upload:** Upload PDF and Excel (XLSX) documents.
- **Data Extraction:** Extract important business fields from uploaded documents.
- **Document Comparison:** Compare Purchase Orders and Invoices.
- **Discrepancy Detection:** Identify mismatched quantities, prices, and amounts.
- **Approval Workflow:** Approve or reject document-related requests.
- **Execution Control:** Prevent duplicate execution and restrict execution without approval.
- **Verification:** Verify completed workflow executions.
- **Audit Trail:** Maintain records of workflow activities.
- **Dashboard:** View documents, approvals, executions, and verification information.

## Technology Stack

**Frontend**
- React
- JavaScript
- Vite
- CSS

**Backend**
- Python
- FastAPI
- REST API

**Database**
- SQLite

**Document Processing**
- PyMuPDF
- OpenPyXL
- Rule-based extraction
- OpenAI API integration (optional)

## Application Architecture

React Frontend → FastAPI Backend → Document Processing & Extraction → SQLite Database → Comparison & Approval Workflow → Verification & Audit History

## Run Locally

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd PROOFCHAIN-AI
```

### 2. Start the Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend API: http://127.0.0.1:8000

API documentation: http://127.0.0.1:8000/docs

### 3. Start the Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your browser.

## Document Processing

The application uses AI-assisted extraction when the configured AI service is available. A rule-based fallback supports document processing when the AI service is unavailable.

Extraction results depend on the readability and structure of uploaded documents. Users should review extracted values before approving business operations.

## Project Objective

To demonstrate how document processing, discrepancy detection, approval controls, and audit tracking can be combined into a single business workflow automation application.

## Project Status

Core upload, comparison, approval, execution, verification, and audit-history workflows have been implemented and tested.
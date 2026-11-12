
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router
from app.api.workflow import router as workflow_router
from app.db.database import initialize_database


app = FastAPI(
    title="ProofChain AI",
    description="AI-powered business document investigation and automation system",
    version="1.0.0"
)


# Initialize SQLite database when the application starts
@app.on_event("startup")
def startup():
    initialize_database()


# Allow React frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(documents_router)
app.include_router(workflow_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to ProofChain AI!",
        "status": "Running",
        "project": "AI Business Automation"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "backend": "FastAPI",
        "application": "ProofChain AI"
    }

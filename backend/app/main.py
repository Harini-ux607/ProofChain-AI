
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router
from app.api.workflow import router as workflow_router
from app.db.database import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="ProofChain AI",
    description="AI-powered business document investigation and automation system",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://proofchain-frontend-84ma.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

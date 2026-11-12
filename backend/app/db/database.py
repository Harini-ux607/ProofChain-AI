import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parents[2] / "proofchain.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_id TEXT UNIQUE,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT UNIQUE,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            document_type TEXT,
            extracted_data TEXT,
            upload_time TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            approval_id TEXT UNIQUE,
            approval_status TEXT NOT NULL,
            reason TEXT,
            evidence TEXT,
            created_at TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_id TEXT UNIQUE,
            approval_id TEXT NOT NULL UNIQUE,
            execution_status TEXT NOT NULL,
            action TEXT NOT NULL,
            executed_at TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verification_id TEXT UNIQUE,
            execution_id TEXT NOT NULL UNIQUE,
            verification_status TEXT NOT NULL,
            message TEXT NOT NULL,
            verified_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

    print("ProofChain AI database initialized successfully!")
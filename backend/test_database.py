from app.db.database import initialize_database, DATABASE_PATH

initialize_database()

print("Database location:", DATABASE_PATH)
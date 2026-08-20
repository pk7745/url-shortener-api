import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "CRITICAL: DATABASE_URL is not configured in the environment or .env file. "
        "PostgreSQL connection string is required."
    )

if not DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://", "postgresql+asyncpg://")):
    raise RuntimeError(
        f"CRITICAL: Invalid DATABASE_URL configuration. Only PostgreSQL is supported, "
        f"got prefix: {DATABASE_URL.split('://')[0] if '://' in DATABASE_URL else DATABASE_URL}"
    )

# Create SQLAlchemy engine for PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Ensure connections are tested before use
    pool_size=10,
    max_overflow=20,
)

# Session factory for handling database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for models
Base = declarative_base()


def verify_database_connection():
    """Verify active connection to the PostgreSQL database on startup."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError as exc:
        raise RuntimeError(
            f"Failed to connect to PostgreSQL database at {DATABASE_URL}. "
            f"Ensure PostgreSQL is running and credentials in .env are correct. "
            f"Original error: {str(exc)}"
        ) from exc


def get_db():
    """Dependency for providing database sessions to FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

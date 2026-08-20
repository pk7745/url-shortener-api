import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db, verify_database_connection
from app.models import URL
from app.schemas import URLCreate, URLResponse
from app.utils import generate_short_code

# Load environment variables
load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("url_shortener")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan handler."""
    # Verify database connection and create tables if needed
    verify_database_connection()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Production-Quality URL Shortener API",
    description="A lightweight, robust backend service for shortening URLs and handling redirects, built with FastAPI and PostgreSQL.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.post(
    "/shorten",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Shorten a long URL",
    description="Accepts a valid HTTP/HTTPS URL, generates a compact unique short code, stores the mapping in PostgreSQL, and returns the short code along with the complete shortened URL.",
)
def shorten_url(payload: URLCreate, db: Session = Depends(get_db)):
    """Endpoint to shorten a provided long URL."""
    original_url = payload.url
    max_retries = 5

    for attempt in range(max_retries):
        short_code = generate_short_code()
        
        # Check if short code already exists in DB
        existing = db.query(URL).filter(URL.short_code == short_code).first()
        if existing:
            logger.info(f"Short code collision for '{short_code}', retrying generation...")
            continue

        url_record = URL(original_url=original_url, short_code=short_code)
        db.add(url_record)
        
        try:
            db.commit()
            db.refresh(url_record)
            
            full_short_url = f"{BASE_URL}/{short_code}"
            logger.info(f"Created short_code '{short_code}' for URL '{original_url}' (ID: {url_record.id})")
            return URLResponse(short_code=short_code, short_url=full_short_url)
        except IntegrityError:
            db.rollback()
            logger.warning(f"IntegrityError on short_code '{short_code}' (attempt {attempt + 1}), retrying...")
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate a unique short code after multiple attempts. Please try again.",
                )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate unique short code.",
    )


@app.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Redirect to original URL",
    description="Accepts a short code, looks up the original URL in PostgreSQL, and issues an HTTP redirect response. Returns HTTP 404 if the code is invalid or unknown.",
)
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    """Endpoint to redirect a short code to its original URL."""
    clean_code = short_code.strip()
    logger.info(f"Looking up short_code: '{clean_code}'")

    url_record = db.query(URL).filter(URL.short_code == clean_code).first()
    
    if not url_record:
        logger.warning(f"Short code '{clean_code}' not found in database.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )
    
    logger.info(f"Found record for '{clean_code}' -> Redirecting to '{url_record.original_url}'")
    return RedirectResponse(
        url=url_record.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )

# URL Shortener API

A production-quality backend REST API for shortening URLs and handling HTTP redirects, built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **Pydantic**. Created as an internship evaluation backend project.

---

## Overview

The **URL Shortener API** allows clients to convert long web URLs into compact, unique short codes and shortened URLs. When a user requests the shortened URL via its short code, the API queries PostgreSQL and issues an HTTP 307 temporary redirect to the original web address.

This application is designed following clean architecture principles, explicit database transaction handling, strict URL validation, robust error handling, automated unit testing, and OpenAPI documentation.

---

## Features

- **URL Shortening**: Accepts long HTTP/HTTPS URLs and generates compact Base62 short codes.
- **PostgreSQL Persistence**: Fully persistent data storage using PostgreSQL and SQLAlchemy ORM.
- **Unique Short-Code Generation**: Collision-resistant short code generation with database-level uniqueness enforcement and automatic retry logic.
- **HTTP Redirects**: Implements standard HTTP 307 redirects to seamlessly route short links to original target URLs.
- **Strict Validation**: Validates incoming URLs using Pydantic schema validation to ensure only valid HTTP/HTTPS web addresses are accepted.
- **Error Handling**: Friendly, structured HTTP error responses (e.g. 404 for unknown codes, 422 for invalid URLs, 500 for server errors).
- **Interactive Documentation**: Built-in Swagger UI documentation (`/docs`) for easy manual testing.
- **Automated Test Suite**: Full `pytest` integration covering end-to-end API behaviors.

---

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0+
- **Driver**: psycopg2-binary
- **Validation**: Pydantic v2
- **ASGI Server**: Uvicorn
- **Testing**: Pytest & HTTPX / TestClient
- **Environment**: python-dotenv

---

## Project Structure

```text
url-shortener-api/
│
├── app/
│   ├── __init__.py      # Package initializer
│   ├── main.py          # FastAPI application entrypoint, middleware, routes
│   ├── database.py      # PostgreSQL connection string, SQLAlchemy engine & session factory
│   ├── models.py        # SQLAlchemy database model for URLs table
│   ├── schemas.py       # Pydantic request and response schemas
│   └── utils.py         # URL-safe short code generator utility
│
├── tests/
│   ├── __init__.py      # Test package initializer
│   └── test_api.py      # End-to-end API test suite using pytest
│
├── .env.example         # Environment variable template
├── .gitignore            # Git ignore rules for virtual environments, secrets, and caches
├── requirements.txt     # Python dependency specifications
├── schema.sql           # PostgreSQL DDL script for database table creation
└── README.md            # Comprehensive project documentation
```

---

## Prerequisites

Before running the application, ensure you have installed:
1. **Python 3.11+** (or Python 3.10+)
2. **PostgreSQL** server running locally or remotely
3. **Git** (optional, for version control)

---

## PostgreSQL Setup

1. **Start PostgreSQL Service**: Ensure your PostgreSQL server instance is running.
2. **Create Database**:
   Open `psql` or your PostgreSQL management tool (e.g., pgAdmin) and execute:
   ```sql
   CREATE DATABASE url_shortener;
   ```
3. **Create Database Table**:
   Apply the provided `schema.sql` script to create the `urls` table:
   ```bash
   psql -U postgres -d url_shortener -f schema.sql
   ```
   *Note: SQLAlchemy will also automatically create the table on application startup if it does not already exist.*

---

## Environment Variables

The application requires environment configuration specified in a `.env` file at the root directory.

Create a `.env` file by copying `.env.example`:
```bash
cp .env.example .env
```

Configure your parameters in `.env`:
```env
# PostgreSQL connection string (Replace username, password, host, port, dbname)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/url_shortener

# Base URL for constructing complete shortened links returned by /shorten
BASE_URL=http://localhost:8000
```

> [!WARNING]
> Never commit your `.env` file or real database credentials to Git repositories.

---

## Installation

1. **Clone or Navigate to the Repository**:
   ```bash
   cd url-shortener-api
   ```

2. **Create a Python Virtual Environment**:
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the API

Start the API server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API server will start on `http://localhost:8000`.

---

## API Usage

### 1. Shorten a URL

- **Endpoint**: `POST /shorten`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "url": "https://example.com/a/very/long/url"
  }
  ```
- **Response**: HTTP 201 Created
  ```json
  {
    "short_code": "aB92xK",
    "short_url": "http://localhost:8000/aB92xK"
  }
  ```

### 2. Redirect to Original URL

- **Endpoint**: `GET /{short_code}`
- **Example**: `GET /aB92xK`
- **Response**: HTTP 307 Temporary Redirect
  - Redirects browser/client to `https://example.com/a/very/long/url`.

---

## Error Cases

| Scenario | HTTP Status Code | Response Body Example |
| :--- | :--- | :--- |
| **Invalid URL** | `422 Unprocessable Entity` | `{"detail": [{"loc": ["body", "url"], "msg": "Invalid HTTP/HTTPS URL provided...", "type": "value_error"}]}` |
| **Unknown Short Code** | `404 Not Found` | `{"detail": "Short URL not found"}` |
| **Database Failure** | `500 Internal Server Error` | `{"detail": "Failed to connect to PostgreSQL database..."}` |

---

## Swagger Documentation

FastAPI automatically generates interactive OpenAPI documentation.

After starting the server, open your web browser and navigate to:
```text
http://localhost:8000/docs
```

From the Swagger UI interface, you can test `POST /shorten` and `GET /{short_code}` directly.

---

## Testing

Run the automated pytest test suite:

```bash
pytest tests/
```

To view verbose output:
```bash
pytest -v tests/
```

---

## Example End-to-End Flow

```text
1. Client sends long URL:
   POST /shorten  -->  {"url": "https://python.org"}

2. Application:
   - Validates input URL format
   - Generates unique short code (e.g., "PyCode")
   - Persists mapping in PostgreSQL table "urls"

3. Response returned to Client:
   HTTP 201 Created --> {"short_code": "PyCode", "short_url": "http://localhost:8000/PyCode"}

4. Client requests shortened link:
   GET /PyCode

5. Application:
   - Queries PostgreSQL for "PyCode"
   - Issues HTTP 307 Redirect to "https://python.org"
```

---

## Design Decisions

- **PostgreSQL Persistence**: PostgreSQL provides enterprise-grade ACID transactions, indexing support, and robust concurrency control for link persistence.
- **Database-Level Uniqueness**: The `short_code` field contains a unique index in PostgreSQL, guaranteeing persistence-level uniqueness even across concurrent API workers.
- **HTTP 307 Redirect**: Using HTTP 307 Temporary Redirect preserves the HTTP method and signals to HTTP clients that link targets may change dynamically.
- **Pydantic Validation**: Input URLs are strictly validated at the API boundary before hitting database sessions.
- **Environment Isolation**: Database connection details are loaded exclusively from `.env` variables via `python-dotenv`, preventing hardcoded credentials.

---

## Limitations & Future Improvements

- **Cache Layer**: Adding Redis caching for high-frequency short link redirects.
- **Custom Alias Support**: Allowing users to specify custom short codes during shortening.
- **Rate Limiting**: Incorporating rate limiting to prevent API abuse.

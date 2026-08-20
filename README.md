# URL Shortener API

> A RESTful backend API for creating shortened URLs and redirecting short links to their original destinations, built with FastAPI and PostgreSQL. Developed as an internship evaluation project.

---

## Overview

The **URL Shortener API** is a lightweight, backend RESTful web service designed to convert long HTTP/HTTPS URLs into compact, unique short codes. When a client requests a generated short code, the API queries PostgreSQL for the target mapping and responds with an HTTP 307 redirect to the original URL.

This application is built with FastAPI, using SQLAlchemy for database operations and Pydantic for input validation. All URL mappings are stored persistently in a PostgreSQL database, ensuring data longevity across application restarts without relying on in-memory state or fallback databases.

---

## Features

- **URL Shortening**: Accepts long HTTP/HTTPS URLs and returns compact Base62 short codes.
- **Unique Short-Code Generation**: Generates collision-resistant short codes with database-level uniqueness constraints and retry handling.
- **PostgreSQL Persistence**: Stores all URL mappings in PostgreSQL with automatic creation timestamps.
- **HTTP 307 Redirects**: Issues HTTP 307 Temporary Redirect responses for valid short codes.
- **Strict Input Validation**: Validates incoming request payloads using Pydantic to ensure only valid HTTP/HTTPS URLs are processed.
- **404 Error Handling**: Returns an HTTP 404 Not Found response when a requested short code does not exist.
- **Database-Level Uniqueness**: Enforces unique constraints on short codes in PostgreSQL.
- **Automatic Interactive Documentation**: Exposes Swagger UI (`/docs`) and ReDoc (`/redoc`) endpoints provided by FastAPI.
- **Automated Test Suite**: Includes an end-to-end unit and integration test suite using `pytest`.

---

## Technology Stack

| Technology | Purpose |
| :--- | :--- |
| **Python** | Backend programming language |
| **FastAPI** | REST API web framework |
| **PostgreSQL** | Persistent relational database |
| **SQLAlchemy** | ORM and database interaction |
| **Pydantic** | Request/response validation and schemas |
| **Uvicorn** | ASGI web server |
| **Pytest** | Test runner and framework |
| **HTTPX / TestClient** | API endpoint integration testing |
| **python-dotenv** | Environment variable management |

---

## Project Structure

```text
url-shortener-api/
│
├── app/
│   ├── __init__.py      # Package initializer
│   ├── main.py          # FastAPI application entry point, lifecycle, and route handlers
│   ├── database.py      # PostgreSQL SQLAlchemy engine, session maker, and connection verification
│   ├── models.py        # SQLAlchemy model mapping for the "urls" table
│   ├── schemas.py       # Pydantic schemas for request validation and response formatting
│   └── utils.py         # URL-safe Base62 short code generator utility
│
├── tests/
│   ├── __init__.py      # Test package initializer
│   └── test_api.py      # Automated API test suite using Pytest and FastAPI TestClient
│
├── .env.example         # Template for environment variables
├── .gitignore            # Git ignore rules for virtual environments, secrets, and caches
├── requirements.txt     # Python dependency manifest
├── schema.sql           # PostgreSQL table DDL creation script
└── README.md            # Project documentation
```

---

## Prerequisites

Before setting up and running the application, ensure the following are installed on your system:

- **Python 3.11+** (or Python 3.10+)
- **PostgreSQL** database server (must be installed and running)
- **Git** (useful for cloning the repository)

> [!IMPORTANT]
> The application requires an active PostgreSQL database connection to operate. It does not use SQLite or in-memory database fallbacks.

---

## Setup Instructions

### Step 1 — Clone the Repository

```bash
git clone https://github.com/pk7745/url-shortener-api.git
cd url-shortener-api
```

---

### Step 2 — Create a Virtual Environment

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### Windows (Command Prompt)

```cmd
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## PostgreSQL Database Setup

### 1. Create the Database

Log in to your PostgreSQL instance using `psql` or a administration tool (such as pgAdmin) and create a database:

```sql
CREATE DATABASE url_shortener;
```

*(If you choose a different database name, update your `DATABASE_URL` in `.env` accordingly).*

### 2. Create the Table

Apply the provided `schema.sql` script to create the `urls` table and associated index:

```bash
psql -U postgres -d url_shortener -f schema.sql
```

*Note: The application also executes SQLAlchemy table creation on startup if the table does not already exist.*

---

## Environment Variables

Environment variables are managed using a `.env` file at the root of the project directory.

- `.env.example` is committed to GitHub as a safe configuration template.
- `.env` is created locally and contains environment-specific settings.
- `.env` is listed in `.gitignore` to prevent committing sensitive information.

### Create `.env` from Template

#### Linux / macOS / Git Bash

```bash
cp .env.example .env
```

#### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Configuration Parameters

Configure `.env` as follows:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/url_shortener
BASE_URL=http://localhost:8000
```

- **`DATABASE_URL`**: The PostgreSQL connection string used by SQLAlchemy (`postgresql://<user>:<password>@<host>:<port>/<dbname>`).
- **`BASE_URL`**: The base address used to construct complete shortened URLs returned by `POST /shorten`.

---

## Run the Application

Start the API server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

- `app.main` references `app/main.py`.
- `app` is the FastAPI application instance.
- `--reload` enables auto-reload on code changes during development.

The server will start listening at:
`http://localhost:8000`

---

## Verify the Application

Once the server is running, confirm it is active by accessing the automatically generated documentation in your browser:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Documentation

### POST `/shorten`

Accepts a long HTTP/HTTPS URL, validates its format, generates a unique short code, stores the record in PostgreSQL, and returns the shortened URL.

#### Request Body

- **Content-Type**: `application/json`

```json
{
  "url": "https://example.com/a/very/long/url"
}
```

#### Successful Response (`201 Created`)

```json
{
  "short_code": "aB92xK",
  "short_url": "http://localhost:8000/aB92xK"
}
```

---

### GET `/{short_code}`

Receives a short code, queries PostgreSQL for the matching original URL, and issues an HTTP redirect.

#### Example Request

```text
GET /aB92xK
```

#### Responses

- **HTTP `307 Temporary Redirect`**: Redirects client to the original URL.
- **HTTP `404 Not Found`**: Returned when the requested short code does not exist.
  ```json
  {
    "detail": "Short URL not found"
  }
  ```

---

## End-to-End Example

```text
1. Start PostgreSQL server.
2. Configure .env with valid DATABASE_URL and BASE_URL.
3. Start FastAPI using: uvicorn app.main:app --reload
4. Open http://localhost:8000/docs.
5. Execute POST /shorten with {"url": "https://example.com"}.
6. Receive response: {"short_code": "nnrOh3", "short_url": "http://localhost:8000/nnrOh3"}.
7. Open http://localhost:8000/nnrOh3 in a browser or API client.
8. The API queries PostgreSQL for "nnrOh3".
9. The API returns an HTTP 307 Temporary Redirect.
10. The client is redirected to https://example.com.
```

---

## Error Handling

| Scenario | HTTP Status Code | Response / Details |
| :--- | :---: | :--- |
| **Invalid HTTP/HTTPS URL** | `422` | Validation error detailing malformed or empty URL |
| **Unknown Short Code** | `404` | `{"detail": "Short URL not found"}` |
| **Database Failure / Missing Config** | `500` / `RuntimeError` | PostgreSQL operational error or connection refusal |

---

## Testing

The project includes an automated test suite using `pytest` and FastAPI `TestClient`.

### Run Tests

```bash
pytest tests/
```

To run with verbose output:

```bash
pytest -v tests/
```

### What the Test Suite Covers

- `test_shorten_url_success`: Verifies `POST /shorten` creates short code and full URL.
- `test_shorten_url_persisted_in_db`: Verifies records are saved to the PostgreSQL database.
- `test_redirect_to_original_url`: Verifies `GET /{short_code}` returns an HTTP 307 redirect to target URL.
- `test_redirect_unknown_short_code`: Verifies unknown short code requests return HTTP 404.
- `test_invalid_url_rejection`: Verifies non-HTTP/HTTPS and malformed URLs are rejected with HTTP 422.

---

## Architecture / Request Flow

```text
Client
   │
   ▼
FastAPI
   │
   ├── POST /shorten
   │       │
   │       ▼
   │   Validate URL (Pydantic)
   │       │
   │       ▼
   │   Generate Short Code (utils)
   │       │
   │       ▼
   │   PostgreSQL (Save mapping)
   │
   └── GET /{short_code}
           │
           ▼
       PostgreSQL Lookup
           │
           ▼
       HTTP 307 Redirect
           │
           ▼
       Original Destination URL
```

---

## Database Schema

The application uses PostgreSQL with SQLAlchemy ORM.

### Table: `urls`

| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Unique surrogate identifier |
| `original_url` | `TEXT` | NOT NULL | The original destination URL |
| `short_code` | `VARCHAR(20)` | NOT NULL, UNIQUE, Indexed | Unique Base62 short code string |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | NOT NULL, Default `NOW()` | Automatic record creation timestamp |

---

## Security & Configuration Notes

- Database credentials and connection parameters are loaded via environment variables using `python-dotenv`.
- `.env` is listed in `.gitignore` and excluded from Git tracking.
- `.env.example` is provided as a reference template without real credentials.
- SQL operations are handled through SQLAlchemy ORM parameterization to prevent SQL injection.

---

## Deployment Readiness

Deploying this application to a production environment requires:

- A Python 3.11+ runtime environment
- A managed or hosted PostgreSQL database instance
- Setting the `DATABASE_URL` environment variable to point to the production PostgreSQL cluster
- Setting the `BASE_URL` environment variable to match the production domain name
- An ASGI production server command (such as `uvicorn app.main:app --host 0.0.0.0 --port 8000` or Gunicorn with Uvicorn workers)

---

## Future Improvements

*The following features are NOT currently implemented in this assignment codebase and represent optional future enhancements:*

- **Redis Caching**: Adding Redis caching for fast lookup of high-frequency short code redirects.
- **Custom Short Code Aliases**: Allowing users to specify custom short code strings during shortening.
- **Rate Limiting**: Implementing rate limiting middleware to prevent API abuse.
- **Click Analytics**: Tracking redirect request counts and timestamp analytics per link.
- **User Authentication**: Adding user accounts and authentication for link management.

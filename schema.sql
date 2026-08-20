-- PostgreSQL Schema for URL Shortener API

CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    original_url TEXT NOT NULL,
    short_code VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Index on short_code for fast lookup during redirection
CREATE INDEX IF NOT EXISTS ix_urls_short_code ON urls (short_code);

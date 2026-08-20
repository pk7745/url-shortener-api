from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


class URLCreate(BaseModel):
    """Request schema for creating a shortened URL."""

    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure the input URL is a valid HTTP/HTTPS URL."""
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")

        # Use Pydantic's HttpUrl parser for strict validation
        try:
            parsed_url = HttpUrl(v)
            if parsed_url.scheme not in ("http", "https"):
                raise ValueError("URL scheme must be http or https")
            return str(parsed_url)
        except Exception as err:
            raise ValueError(f"Invalid HTTP/HTTPS URL provided: {v}") from err


class URLResponse(BaseModel):
    """Response schema for shortened URL metadata."""

    model_config = ConfigDict(from_attributes=True)

    short_code: str
    short_url: str


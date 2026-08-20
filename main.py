"""Root entry point forwarding ASGI app to app.main:app for deployment compatibility."""
from app.main import app

__all__ = ["app"]

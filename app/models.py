from sqlalchemy import Column, DateTime, Integer, String, Text, func
from app.database import Base


class URL(Base):
    """SQLAlchemy model representing shortened URLs in PostgreSQL."""

    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(20), unique=True, index=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

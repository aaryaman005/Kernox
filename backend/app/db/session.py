from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base

# Import models so metadata is populated
from app.models import endpoint, event  # noqa


# ─────────────────────────────────────────────
# Engine Configuration
# ─────────────────────────────────────────────
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # 🔥 REQUIRED for in-memory DB
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
    )


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# ─────────────────────────────────────────────
# Auto-create tables ONLY for SQLite
# ─────────────────────────────────────────────
if settings.DATABASE_URL.startswith("sqlite"):
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

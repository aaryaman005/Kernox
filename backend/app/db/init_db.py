from app.db.base import Base
from app.db.session import engine

# Import models so they register with metadata
from app.models import endpoint, event  # noqa


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    print("Creating tables...")
    init_db()
    print("Tables created.")

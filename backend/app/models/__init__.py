
from app.db.session import Base, engine
from app.models.scan import Scan
from app.models.user import User


def init_db():
    # Importing the models registers their tables with Base.
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("PhishGuard database initialized successfully.")

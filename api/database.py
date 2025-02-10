from contextlib import contextmanager
from sqlmodel import Session, create_engine
from config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


@contextmanager
def get_session():
    """Context manager to ensure the session is closed after use."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    # Tables should be created with migrations (Alembic)
    # The models should already be imported and registered from app.models
    from sqlmodel import SQLModel
    import models

    SQLModel.metadata.create_all(engine)

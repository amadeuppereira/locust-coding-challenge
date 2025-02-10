import random

from sqlmodel import Session, select

from models import User

# In-memory session storage (for demonstration purposes)
# Should use redis, memcached, KV, ... in production
SESSION_DB = {}


def create_session(user_id: int) -> int:
    # Fake session ID generation
    session_id = str(len(SESSION_DB) + random.randint(0, 1000000))
    SESSION_DB[session_id] = user_id
    return session_id


def delete_session(session_id: int) -> None:
    SESSION_DB.pop(session_id, None)


def get_user_from_session(session_id: str, db_session: Session) -> User | None:
    user_id = SESSION_DB.get(session_id)
    if user_id is None:
        return None

    return db_session.get(User, user_id)

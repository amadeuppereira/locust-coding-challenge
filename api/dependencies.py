from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from utils import get_user_from_session
from models import User
from database import engine


def get_db():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


DBSession = Annotated[Session, Depends(get_db)]


def get_session_id(request: Request) -> str:
    return request.cookies.get("session_id")


def get_current_user(
    db_session: DBSession, session_id: str = Depends(get_session_id)
) -> User:
    user = get_user_from_session(session_id, db_session)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

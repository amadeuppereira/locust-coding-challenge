from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import select

from dependencies import DBSession, get_current_user, get_session_id
from utils import create_session, delete_session
from models import CPUUsageCreate, TestRun, User, UserLogin, CPUUsage
from config import settings


api_router = APIRouter(prefix="/api")


@api_router.post("/auth/login")
async def login(db_session: DBSession, credentials: UserLogin):
    statement = select(User).where(User.username == credentials.username)
    user = db_session.exec(statement).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # We are using plain text password comparison for simplicity
    if not credentials.password == user.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    response = JSONResponse({"status": "User login"}, status_code=status.HTTP_200_OK)
    response.set_cookie(key=settings.SESSION_COOKIE_KEY, value=create_session(user.id))
    return response


@api_router.post("/auth/logout")
async def logout(session_id: str = Depends(get_session_id)):
    # We should validate if there is a valid session
    # This is just to test with the authentication is working fine
    # Currently we always invalidate the session and return a success
    delete_session(session_id)

    response = JSONResponse({"status": "User logout"}, status_code=status.HTTP_200_OK)
    response.delete_cookie(key=settings.SESSION_COOKIE_KEY)
    return response


@api_router.post(
    "/test_runs/",
    dependencies=[Depends(get_current_user)],
    response_model=TestRun,
    status_code=status.HTTP_201_CREATED,
)
async def create_test_run(db_session: DBSession):
    test_run = TestRun()
    db_session.add(test_run)
    db_session.commit()
    db_session.refresh(test_run)
    return test_run


@api_router.post(
    "/test_runs/{id}/cpu_usage",
    dependencies=[Depends(get_current_user)],
    response_model=CPUUsage,
    status_code=status.HTTP_201_CREATED,
)
async def create_cpu_usage(
    db_session: DBSession, id: uuid.UUID, cpu_usage_in: CPUUsageCreate
):
    test_run = db_session.get(TestRun, id)
    if not test_run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    cpu_usage = CPUUsage.model_validate(cpu_usage_in, update={"test_run_id": id})
    db_session.add(cpu_usage)
    db_session.commit()
    db_session.refresh(cpu_usage)
    return cpu_usage


@api_router.get(
    "/test_runs/{id}/cpu_usage",
    dependencies=[Depends(get_current_user)],
    response_model=List[CPUUsage],
    status_code=status.HTTP_200_OK,
)
async def get_cpu_usage(db_session: DBSession, id: uuid.UUID):
    test_run = db_session.get(TestRun, id)
    if not test_run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return test_run.cpu_usages

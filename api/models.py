from datetime import datetime, timezone
import uuid

from sqlmodel import Field, Relationship, SQLModel


class BaseUser(SQLModel):
    username: str = Field(unique=True, index=True)
    # This password should be hashed
    # For simplicity we are using plain text
    password: str


class UserLogin(BaseUser):
    pass


class User(BaseUser, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class BaseTestRun(SQLModel):
    name: str


class TestRunCreate(BaseTestRun):
    pass


class TestRun(BaseTestRun, table=True):
    __tablename__ = "test_run"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # A TestRun can have multiple CPU usage entries
    cpu_usages: list["CPUUsage"] = Relationship(
        back_populates="test_run",
        sa_relationship_kwargs={"order_by": "CPUUsage.timestamp"},
    )


class BaseCPUUsage(SQLModel):
    percentage: float


class CPUUsageCreate(BaseCPUUsage):
    pass


class CPUUsage(BaseCPUUsage, table=True):
    __tablename__ = "cpu_usage"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Foreign key to link to TestRun
    test_run_id: uuid.UUID = Field(foreign_key="test_run.id")
    test_run: TestRun = Relationship(back_populates="cpu_usages")

import logging
import uuid

from database import get_session
from models import User, TestRun, CPUUsage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_users():
    with get_session() as session:
        session.add(User(username="user1", password="password1"))
        session.add(User(username="user2", password="password2"))


def create_tests():
    with get_session() as session:
        test_1 = TestRun(id=uuid.UUID("7acf59e4db164cd3b04a13b6e4f1f5ca"))
        test_2 = TestRun(id=uuid.UUID("16f1e55b34c74034b57ab10559d16872"))
        session.add(test_1)
        session.add(test_2)
        session.commit()

        session.add(CPUUsage(percentage=10.0, test_run_id=test_1.id))
        session.add(CPUUsage(percentage=13.0, test_run_id=test_1.id))
        session.add(CPUUsage(percentage=12.0, test_run_id=test_1.id))
        session.add(CPUUsage(percentage=25.3, test_run_id=test_1.id))
        session.add(CPUUsage(percentage=20.0, test_run_id=test_1.id))
        session.add(CPUUsage(percentage=17.0, test_run_id=test_1.id))
        session.add(CPUUsage(percentage=7.0, test_run_id=test_1.id))

        session.add(CPUUsage(percentage=50.0, test_run_id=test_2.id))
        session.add(CPUUsage(percentage=53.0, test_run_id=test_2.id))
        session.add(CPUUsage(percentage=52.0, test_run_id=test_2.id))
        session.add(CPUUsage(percentage=65.3, test_run_id=test_2.id))
        session.add(CPUUsage(percentage=60.0, test_run_id=test_2.id))
        session.add(CPUUsage(percentage=57.0, test_run_id=test_2.id))
        session.add(CPUUsage(percentage=47.0, test_run_id=test_2.id))


def main() -> None:
    logger.info("Creating initial data")
    create_users()
    create_tests()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()

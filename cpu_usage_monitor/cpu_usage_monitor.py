import argparse
from datetime import datetime, timedelta
import signal
import time
import psutil
import requests
import logging
import asyncio


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestRun:
    # We should validate the api responses
    # We are making an optimistic assumption that the API is working as expected
    def __init__(self):
        self._api = "http://localhost:8000/api"

        # This credentials should no be hardcoded
        # Should come from a configuration file or environment variables
        self._login("user1", "password1")
        logger.info(f"Sucessful login in {self._api}")

        self._test_run_id = self._create_test_run()
        logger.info(f"Started test run {self._test_run_id}")

    def _login(self, username: str, password: str):
        self._session = requests.session()
        self._session.post(
            f"{self._api}/auth/login", json={"username": username, "password": password}
        )

    def _create_test_run(self):
        r = self._session.post(f"{self._api}/test_runs/")
        return r.json()["id"]

    def save_cpu_usage(self, cpu_usage: float):
        r = self._session.post(
            f"{self._api}/test_runs/{self._test_run_id}/cpu_usage",
            json={"percentage": cpu_usage},
        )

    def get_cpu_usage(self):
        r = self._session.get(f"{self._api}/test_runs/{self._test_run_id}/cpu_usage")
        return r.json()


class CPUUsageMonitor:
    def __init__(self, interval: float, threshold: float):
        self.interval: float = interval
        self.threshold: float = threshold
        self._is_above_threshold: bool = False

        self._print_current_usage_interval: int = 5

        self._test_run = TestRun()

        # We call here since we should ignore the
        # first time `psutil.cpu_percent()` is called
        # because it will return a 0.0 value
        self._get_current_cpu_percent()

    def _get_current_cpu_percent(self):
        cpu_percent: float = psutil.cpu_percent()

        # We use `self._is_above_threshold` to warn only once
        # when it exceeds the threshold the first time
        # and reset it when is goes down
        if not self._is_above_threshold and cpu_percent > self.threshold:
            logger.warning(f"CPU usage exceeds {self.threshold}%")
            self._is_above_threshold = True
        elif not cpu_percent > self.threshold:
            self._is_above_threshold = False

        return cpu_percent

    async def measure_cpu(self):
        try:
            while True:
                cpu_percent = self._get_current_cpu_percent()
                self._test_run.save_cpu_usage(cpu_percent)
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            return

    async def print_cpu(self):
        try:
            while True:
                cpu_percent = self._get_current_cpu_percent()
                logger.info(f"Current CPU Usage: {cpu_percent:.2f}%")
                await asyncio.sleep(self._print_current_usage_interval)
        except asyncio.CancelledError:
            return

    async def start(self):
        self._start_time = time.monotonic()

        tasks = []

        tasks.append(asyncio.create_task(self.measure_cpu()))
        tasks.append(asyncio.create_task(self.print_cpu()))

        def sigint_handler():
            logger.info("Received CTRL+C... stopping...")
            for task in tasks:
                task.cancel()

        # Register SIGINT handler
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, sigint_handler)

        # Wait for tasks to finish
        await asyncio.gather(*tasks)

        self._end_time = time.monotonic()

        self.report()

    def report(self):
        cpu_usages = self._test_run.get_cpu_usage()

        total_time_above_threshold: timedelta = timedelta(seconds=0)
        is_above_threshold_timestamp: datetime = None

        # We can iterate the cpu usages directly because
        # the values are returned from the api
        # order by the 'timestamp'
        for cpu_usage in cpu_usages:
            usage_percentage: float = cpu_usage["percentage"]
            timestamp: datetime = datetime.fromisoformat(cpu_usage["timestamp"])

            # Store first timestamp when usage is higher than threshold
            if (
                usage_percentage > self.threshold
                and is_above_threshold_timestamp is None
            ):
                is_above_threshold_timestamp = timestamp

            # If usage is within threshold and previously was higher
            # We calculate the difference and add to the total time
            elif (
                not usage_percentage > self.threshold
                and is_above_threshold_timestamp is not None
            ):
                total_time_above_threshold += timestamp - is_above_threshold_timestamp
                is_above_threshold_timestamp = None
        else:
            # Case to handle if usage is higher until the end of the run
            # We default to last timestamp
            if is_above_threshold_timestamp is not None:
                last_timestamp: datetime = datetime.fromisoformat(
                    cpu_usages[-1]["timestamp"]
                )

                total_time_above_threshold += (
                    last_timestamp - is_above_threshold_timestamp
                )

        logger.info("---------- REPORT ------------")
        logger.info(f"Total time of the test:     {self._end_time - self._start_time:.2f}s")
        logger.info(f"Total time above threshold: {total_time_above_threshold.total_seconds()}s")
        logger.info("------------------------------")


def main():
    parser = argparse.ArgumentParser(description="Monitor CPU usage.")
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1,
        help="Sampling interval in seconds (default: 1s)",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=10,
        help="CPU usage percentage threshold (default: 10)",
    )
    args = parser.parse_args()

    monitor = CPUUsageMonitor(interval=args.interval, threshold=args.threshold)
    asyncio.run(monitor.start())


if __name__ == "__main__":
    main()

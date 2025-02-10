# locust-coding-challenge

**Intro**

- Submit your answer as a link to a publicly available GitHub repo.
- You don't need to consider security beyond what is mentioned in the instructions, or build any abstraction layers. But do make a note of any corners you have cut, or things you would need to do differently to put this code into production.

**Part 1**

- [x] Create a Python API using Flask or FastAPI that connects to a database of your choice.
- [x] Implement a route that allows a user to authenticate with a username and password stored in the database and creates a cookie-based session.
- [x] Implement a route that allows authenticated users to write cpu usage data that relates to a specific "test run".
- [x] Implement this as a cpu_usage table and a test_runs table and link them.
- [x] Implement a route that allows authenticated users to read all the cpu usage data linked to a specified test run.

**Part 2**

- [x] Create an installable Python script that measures the current CPU usage (using for
example psutil) and writes it to the database, via the API, at regular configurable
intervals. The CPU usage should be measured until the user manually stops the script.
Measurements should be grouped into test runs, such that each run of the script is a
new testrun.
- [x] The script should print the current cpu usage every 5 seconds.
- [x] The script should notify the user if the cpu usage exceeds a certain configurable
threshold.
- [x] A report should be shown at the end of the testrun:
    - [x] The total time of the test
    - [x] The approximate total time cpu usage was above threshold

**Part 3 (optional)**

- [x] Use Docker to package the API

---

**Start API (with mysql db)**

`docker compose up`

```
- login
POST /api/auth/login
{
    "username": str
    "password": str
}

- logout
POST /api/auth/logout

- create a new test run
POST /api/test_runs

- write cpu usage to a test run
POST /api/test_runs/{test_run_id}/cpu_usage
{
    "percentage": float
}

- get cpu usage from a test run
GET /api/test_runs/{test_run_id}/cpu_usage
```

---

**Populate db with dummy data:**

`docker compose exec api python3 dummy_data.py`

```
Users:
    - user1 / password1
    - user2 / password2

Test Runs:
    - 7acf59e4db164cd3b04a13b6e4f1f5ca
    - 16f1e55b34c74034b57ab10559d16872
```

---

**CPU usage monitor**

- Install

`pip install cpu_usage_monitor`

- Run

`cpu-usage-monitor`

```
usage: cpu-usage-monitor [-h] [-i INTERVAL] [-t THRESHOLD]

Monitor CPU usage.

options:
  -h, --help            show this help message and exit
  -i, --interval INTERVAL
                        Sampling interval in seconds (default: 1s)
  -t, --threshold THRESHOLD
                        CPU usage percentage threshold (default: 10)
```
---


**Notes:**

- Separate models, routers per functionality (auth, test runs, ...)
- Use model mixins (p.e: TimestampMixin)
- Use migrations (Alembic) to update database
- Cascade model deletes (when a test run is deleted should we also delete cpu usage related to it?)
- Pagination when retrieving all cpu usages
- This is storing user sessions in memory, should use redis, memcached, KV, ... in production
- Do not store passwords in plain text

- API user credential should not be hardcoded in the cpu usage monitor script
- In cpu usage monitor we should validate API responses (we assume that everything is going to be successful)
- Add error handling
- Preetier logs :)

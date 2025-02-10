from fastapi import FastAPI

from database import init_db
from routes import api_router

app = FastAPI()

# This should be handled before the api is started
# We are doing it here for simplicity
init_db()

app.include_router(api_router)

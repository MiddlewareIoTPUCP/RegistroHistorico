import asyncio

from fastapi import FastAPI

from app import config, rabbit_events
from app.influx_connection import influx_connection
from app.routes import data

app = FastAPI()
settings = config.Settings()
config.configure_logger(settings)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(rabbit_events.start(settings))
    asyncio.create_task(influx_connection.configure_connection(settings))

# We add data routes
app.include_router(data.router)

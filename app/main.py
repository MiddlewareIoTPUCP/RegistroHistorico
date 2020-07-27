import asyncio

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from app import config, rabbit_events
from app.influx_connection import influx_connection
from app.routes import data
from utils.hydra_connection import AuthError

settings = config.get_settings()
app = FastAPI(root_path=settings.root_path)
config.configure_logger()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(rabbit_events.start(settings))
    asyncio.create_task(influx_connection.configure_connection(settings))


@app.exception_handler(AuthError)
def handle_auth_error(request: Request, ex: AuthError):
    return JSONResponse(status_code=ex.status_code, content=ex.error)


# We add data routes
app.include_router(data.router)

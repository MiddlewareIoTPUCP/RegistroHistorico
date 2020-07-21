import logging
import sys

from pydantic import BaseSettings
from loguru import logger


class Settings(BaseSettings):
    amqp_broker_url: str = "amqp://guest:guest@localhost:5672/"
    influx_db_host: str = "localhost"
    influx_db_port: int = 8086
    influx_db_user: str = "user"
    influx_db_password: str = "user"
    influx_db_database: str = "IoTMiddleware"
    log_level: str = "INFO"


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_logger(settings: Settings) -> None:
    intercept_handler = InterceptHandler()
    logging.root.setLevel(settings.log_level)

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn.access",
        "uvicorn.error"
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    # Uvicorn special case
    logging.getLogger("uvicorn").handlers = [logging.NullHandler()]
    logger.configure(handlers=[{"sink": sys.stdout}])

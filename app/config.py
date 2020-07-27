import logging
import sys
from functools import lru_cache

from pydantic import BaseSettings
from loguru import logger


class Settings(BaseSettings):
    # Root Path (for api gateway)
    root_path: str = ""
    # AMQP Settings
    amqp_broker_url: str = "amqp://guest:guest@localhost:5672/"
    # InfluxDB Settings
    influx_db_host: str = "localhost"
    influx_db_port: int = 8086
    influx_db_user: str = "user"
    influx_db_password: str = "user"
    influx_db_database: str = "IoTMiddleware"
    # Log Settings
    log_level: str = "INFO"
    # Hydra/OAuth2 Settings
    hydra_url: str = "http://localhost:9000"
    hydra_algorithms: str = "RS256"
    # User service URL
    user_service_url: str = "http://localhost:8080"
    # Register device service URL
    register_device_service_url: str = "http://localhost:8000"


@lru_cache()
def get_settings():
    return Settings()


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


def configure_logger() -> None:
    settings = get_settings()
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

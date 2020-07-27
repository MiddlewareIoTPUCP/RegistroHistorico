from functools import lru_cache

from aioinflux import InfluxDBClient
from loguru import logger

from app.config import Settings


class InfluxDBConnection:
    client: InfluxDBClient = None


influx = InfluxDBConnection()


async def configure_connection(settings: Settings):
    influx.client = InfluxDBClient(host=settings.influx_db_host,
                                   port=settings.influx_db_port,
                                   database=settings.influx_db_database,
                                   username=settings.influx_db_user,
                                   password=settings.influx_db_password)
    logger.info("Connection set up for InfluxDB")


@lru_cache()
def get_database() -> InfluxDBClient:
    return influx.client

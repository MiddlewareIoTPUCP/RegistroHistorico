import aio_pika

from loguru import logger

from app.config import Settings
from app.rabbit_events.data_management import save_new_data


# Start of RabbitMQ connection
async def start(settings: Settings):
    connection = await aio_pika.connect_robust(settings.amqp_broker_url)
    logger.info("Connected to RabbitMQ")
    await save_new_data(connection)

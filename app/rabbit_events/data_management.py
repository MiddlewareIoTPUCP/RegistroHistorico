import datetime

from aio_pika import Connection, IncomingMessage, ExchangeType
from loguru import logger
from pydantic import ValidationError

from app.data_types import Readings
from app.web_requests import register_device_service
from app.influx_connection import influx_data_management


async def save_data(message: IncomingMessage):
    with message.process():
        try:
            readings = Readings.parse_raw(message.body.decode(), content_type="application/json")

            # Querying the virtual model from Register service
            deviceVirtualModel = await register_device_service.query_virtual_model(readings.objID, readings.ownerToken)
            if deviceVirtualModel is not None:
                # Save it to influex
                await influx_data_management.save_new_reading(readings, deviceVirtualModel)
            else:
                logger.error("Device not found {}".format(readings.objID))

        except ValidationError as e:
            logger.error("Validation error for message")
            logger.error(str(e))


async def save_new_data(connection: Connection):
    async with connection:
        # Create a channel for our connection
        channel = await connection.channel()

        # Create a new exchange of type fanout
        await channel.declare_exchange(name="new_data", type=ExchangeType.FANOUT, durable=True)

        # Create an anonymous exclusive queue to listen for messages
        queue = await channel.declare_queue(name="", exclusive=True)
        await queue.bind(exchange="new_data", routing_key="")

        # Start consuming from that queue
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await save_data(message)

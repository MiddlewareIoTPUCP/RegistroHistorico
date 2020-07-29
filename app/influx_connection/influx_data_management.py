import datetime

from loguru import logger
from aioinflux import InfluxDBClient

from app.data_types import Readings, DeviceVirtualModel, VirtualModelAction
from app.influx_connection import influx_connection


async def save_new_reading(readings: Readings, deviceVirtualModel: DeviceVirtualModel) -> None:
    # Create map for writing data to influx
    influx_write_map = dict()
    influx_write_map["time"] = datetime.datetime.utcnow()
    influx_write_map["measurement"] = deviceVirtualModel.ownerToken

    # Tags
    tags_map = dict()
    tags_map["obj_id"] = deviceVirtualModel.objId
    tags_map["device_id"] = deviceVirtualModel.deviceID
    influx_write_map["tags"] = tags_map

    # Fields
    # Field name is the virtual model readingType, index is used to find it
    fields_map = dict()
    for readingObj in readings.readings:
        if readingObj.index > len(deviceVirtualModel.virtualModel):
            logger.error("Virtual model for reading {} of object {} not found".format(
                readingObj.index, readings.objID
            ))
            continue
        virtualModel = deviceVirtualModel.virtualModel[readingObj.index]
        if isinstance(virtualModel, VirtualModelAction):
            logger.error("Virtual model for reading {} of object {} is for an action".format(
                readingObj.index, readings.objID
            ))
            continue
        fields_map[virtualModel.readingType] = readingObj.reading

    influx_write_map["fields"] = fields_map

    # Write it to influxDB
    influxClient = influx_connection.get_database()
    await influxClient.write(influx_write_map)

from datetime import datetime, timezone
from typing import Union, List, Optional
from pydantic import BaseModel, validator, Extra, Field


# Readings from Broker
class Reading(BaseModel):
    index: int
    reading: Union[float, int]

    @validator('reading')
    def if_int_convert(cls, number):
        if float(number).is_integer():
            return int(number)
        return number


class Readings(BaseModel):
    objID: str
    ownerToken: str
    readings: List[Reading]


# Virtual model from Register service
class VirtualModelReading(BaseModel):
    type: str
    readingType: str
    units: str
    dataType: str

    class Config:
        extra = Extra.forbid


class VirtualModelAction(BaseModel):
    type: str


class DeviceVirtualModel(BaseModel):
    objId: str = Field(alias="_id")
    ownerToken: str
    deviceID: str
    virtualModel: List[Union[VirtualModelReading, VirtualModelAction]]
    additionalInfo: Optional[dict]

    class Config:
        extra = Extra.forbid


class QueryDataTime(BaseModel):
    startTime: datetime
    finishTime: datetime

    @validator('startTime')
    def give_timezone_start(cls, startTime: datetime):
        return startTime.replace(tzinfo=None)

    @validator('finishTime')
    def give_timezone_finish(cls, finishTime: datetime):
        return finishTime.replace(tzinfo=None)


# Model to query device data
class QueryDataBase(BaseModel):
    ownerToken: str
    readingType: str
    times: QueryDataTime


# Model to query device data based on DeviceId
class QueryDataDeviceId(QueryDataBase):
    deviceId: str


# Model to query device data based on objectId
class QueryDataObjectId(QueryDataBase):
    objectId: str
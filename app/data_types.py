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

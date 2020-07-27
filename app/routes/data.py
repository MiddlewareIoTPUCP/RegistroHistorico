from typing import Union, Dict, List

from aioinflux import iterpoints
from fastapi import APIRouter, Security
from loguru import logger
from starlette import status
from starlette.responses import Response

from app.data_types import QueryDataDeviceId
from app.influx_connection.influx_connection import get_database
from app.utils.hydra_connection import get_current_user

from app.web_requests.user_service import get_owner_tokens

router = APIRouter()


# Obtener información de un dispositivo
@router.post("/get_device_data", tags=["devices"], response_model=Union[List, Dict])
async def get_device_data(query_data: QueryDataDeviceId,
                          response: Response,
                          user: str = Security(get_current_user, scopes=["all"])
                          ) -> Union[List, Dict]:
    owner_tokens = await get_owner_tokens(user=user)
    if owner_tokens is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "User doesn't have owner tokens"}

    if query_data.ownerToken not in owner_tokens:
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"msg": "Owner Token provided is not granted to user"}

    # Search query for InfluxDB where it's searching for device_id
    search_query = "select {},device_id from {} where time < '{}' and time > '{}' and device_id = '{}'".format(
        query_data.readingType, query_data.ownerToken,
        query_data.times.finishTime.isoformat("T")+"Z",
        query_data.times.startTime.isoformat("T")+"Z", query_data.deviceId)

    logger.info(search_query)

    query_list = list()
    client = get_database()
    r = await client.query(search_query)
    for i in iterpoints(r):
        query_list.append(i)
    return query_list

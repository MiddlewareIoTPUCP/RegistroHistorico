from loguru import logger
from typing import Optional
from httpx import AsyncClient
from starlette import status

from app.data_types import DeviceVirtualModel
from config import get_settings

settings = get_settings()


# Query register service
async def query_virtual_model(obj_id: str, owner_token: str) -> Optional[DeviceVirtualModel]:
    async with AsyncClient() as client:
        params = {"obj_id": obj_id, "owner_token": owner_token}
        resp = await client.get(settings.register_device_service_url+"/is_device_registered", params=params)
        if resp.status_code == status.HTTP_200_OK:
            return DeviceVirtualModel.parse_raw(resp.read())
        else:
            return None

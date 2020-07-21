import aiohttp

from loguru import logger
from typing import Optional

from app.data_types import DeviceVirtualModel


# Query register service
async def query_virtual_model(obj_id: str, owner_token: str) -> Optional[DeviceVirtualModel]:
    async with aiohttp.ClientSession() as session:
        params = {"obj_id": obj_id, "owner_token": owner_token}
        async with session.get("http://localhost:8000/is_device_registered", params=params) as resp:
            if resp.status == 200:
                return DeviceVirtualModel.parse_raw(await resp.read())
            else:
                return None

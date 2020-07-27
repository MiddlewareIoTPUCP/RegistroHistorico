from typing import List, Optional
from httpx import AsyncClient, QueryParams
from starlette import status

from app.config import get_settings

settings = get_settings()


# Get user owner tokens
async def get_owner_tokens(user: str) -> Optional[List]:
    params = QueryParams({"username": user})
    async with AsyncClient() as client:
        resp = await client.get(settings.user_service_url+"/user/getOwnerTokens", params=params)
    if resp.status_code == status.HTTP_404_NOT_FOUND:
        return None
    return resp.json()
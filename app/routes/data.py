from fastapi import APIRouter
from app.data_types import Readings

router = APIRouter()


# Obtener información de un dispositivo
@router.post("/get_device", tags=["devices"])
async def get_device(readings: Readings) -> dict:  # TODO: Falta seguridad y sacar de la base de datos
    print(readings.schema())
    return {'device': readings}

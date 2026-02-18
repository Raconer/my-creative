from fastapi import APIRouter
from api.v1.endpoints import system

api_router = APIRouter()

api_router.include_router(system.router, prefix="/api/v1/system", tags=["system"])
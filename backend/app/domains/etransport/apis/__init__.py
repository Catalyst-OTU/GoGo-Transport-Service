from fastapi import APIRouter

from .passenger import passengers_router


etransport_router = APIRouter()
etransport_router.include_router(passengers_router, tags=["PASSENGERS ACCOUNT"])

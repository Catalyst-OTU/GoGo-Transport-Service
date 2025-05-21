from fastapi import APIRouter

from domains.auth.apis import auth_routers

router = APIRouter()
router.include_router(auth_routers)

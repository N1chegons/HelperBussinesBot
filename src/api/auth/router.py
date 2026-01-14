from fastapi import APIRouter

from src.api.auth.repository import UserRepository
from src.api.auth.schemas import UserCreate

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.get("/get_user/{telegram_id}")
async def get_user_by_telegram_id(telegram_id: int):
    user = await UserRepository.get_user_by_telegram_id_repository(telegram_id)
    return user

@router.post("/register")
async def register_user(user_schemas: UserCreate):
    new_user = await UserRepository.create_user_repository(user_schemas)
    return new_user
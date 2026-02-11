from fastapi import APIRouter, HTTPException
from starlette import status

from src.auth.repository import UserRepository
from src.auth.schemas import UserCreate

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.get("/get_user")
async def get_user_by_telegram_id(telegram_id: int):
    user = await UserRepository.get_user_by_telegram_id_repository(telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram id {telegram_id} not found."
        )
    return user

@router.post("/register")
async def register_user(user_schemas: UserCreate):
    new_user = await UserRepository.create_user_repository(user_schemas)
    return new_user

@router.put("/add_timezone")
async def add_timezone(telegram_id: int, timezone: str):
    add_timezone_user = await UserRepository.add_timezone_repository(telegram_id, timezone)
    return add_timezone_user

@router.put("/add_number")
async def add_phone_number(telegram_id: int, phone: str):
    add_phone = await UserRepository.add_phone_number_repository(telegram_id, phone)
    return add_phone
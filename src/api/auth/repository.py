from fastapi import HTTPException
from pydantic import Field
from sqlalchemy import select, insert, update
from sqlalchemy.exc import IntegrityError
from starlette import status
from src.api.auth.exceptions import UserNotFoundError, UserCreatedError, UserAlreadyExistsError, UserUpdateError
from src.api.auth.models import User
from src.api.auth.schemas import UserCreate
from src.api.db import async_session
from src.logger import get_logger

logger = get_logger(__name__)


class UserRepository:
    @staticmethod
    async def get_user_by_telegram_id_repository(tg_id: int):
        async with async_session() as session:
            query = select(User).filter_by(telegram_id=tg_id)
            try:
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                if not user:
                    logger.warning(f"User with TG ID <{tg_id}> not found.")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail=f"User with Telegram ID {tg_id} not found."
                    )
                logger.warning(f"User with TG ID: {tg_id} found. Responce: {user.id}, {user.nickname}, {user.phone}")
                return user
            except UserNotFoundError:
                logger.error(f"Servers Erorrs! Arguments: {tg_id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Server error"
                )

    @classmethod
    async def create_user_repository(cls, user_data: UserCreate):
        async with async_session() as session:
            user = await UserRepository.get_user_by_telegram_id_repository(user_data.telegram_id)
            if user:
                logger.warning(
                    f"User already exists: {user_data.telegram_id}, arguments: {user_data.telegram_id}, {user_data.nickname}"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with telegram_id {user_data.telegram_id} already exists"
                )

            data = user_data.model_dump()
            stmt = insert(User).values(**data).returning(User)
            new_user = await session.execute(stmt)
            try:
                await session.commit()
                logger.info(f"User has created. Arguments:{user_data.telegram_id}, {user_data.nickname}")
                return {"message": "User has created."}

            except UserCreatedError:
                logger.error(f"Servers Erorrs! Arguments: {user_data.telegram_id}, {user_data.nickname}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Server error"
                )

    @classmethod
    async def add_phone_number_repository(cls, tg_id: int, phone: str):
        async with async_session() as session:
            phone = await UserRepository.get_user_by_telegram_id_repository(tg_id)
            if not phone.phone == "NULL":
                logger.warning(
                    f"User TG ID {tg_id}already have phone number:{phone}, arguments: {phone}"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with telegram_id {tg_id} already have phone number"
                )

            stmt = (
                    update(User)
                    .filter_by(telegram_id=tg_id)
                    .values(phone=phone)
                    .returning(User)
                )
            await session.execute(stmt)
            try:
                await session.commit()
                logger.info(f"User TG ID: {tg_id} add phone number. Arguments: {phone}")
                return {
                    "message": f"Phone number {phone} has added."
                }
            except UserUpdateError:
                logger.error(f"Servers Erorrs! Arguments: {phone}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Server error"
                )

from datetime import date, datetime, time, UTC

from fastapi import HTTPException
from sqlalchemy import select, insert
from starlette import status

from src.appointments.exceptions import AppointmentsNotFound, AppointmentsCreatedError
from src.appointments.models import Appointment
from src.appointments.schemas import CreateAppointments
from src.appointments.utilits import get_day_boundaries_in_utc, convert_user_input_to_utc
from src.auth.repository import UserRepository
from src.db import async_session
from src.logger import get_logger

logger = get_logger(__name__)

class AppointmentsRepository:
    @classmethod
    async def get_user_appointments_all_repository(cls, tg_id: int):
        async with async_session() as session:
            exist_user = await UserRepository.get_user_by_telegram_id_repository(tg_id)
            if not exist_user:
                logger.warning(
                    f"User with tg_id: {tg_id} not founded."
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with telegram id {tg_id}  not founded"
                )

            query = select(Appointment).filter_by(user_id=exist_user.id)
            try:
                result = await session.execute(query)
                appointments = result.scalars().all()
                return appointments
            except AppointmentsNotFound:
                logger.error(f"Servers Erorrs! Arguments: {tg_id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Server error"
                )

    @classmethod
    async def get_user_appointments_by_datetime_repository(cls, tg_id: int, apps_date: str, user_timezone: str = "Europe/Moscow"):
        exist_user = await UserRepository.get_user_by_telegram_id_repository(tg_id)
        if not exist_user:
            logger.warning(
                f"User with tg_id: {tg_id} not founded."
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with telegram id {tg_id}  not founded"
            )

        target_date = date.fromisoformat(apps_date)

        start_utc, end_utc = get_day_boundaries_in_utc(target_date, user_timezone)

        async with async_session() as session:
            query = select(Appointment).filter_by(user_id=exist_user.id).where(
                Appointment.appointment_datetime >= start_utc,
                Appointment.appointment_datetime <= end_utc
            ).order_by(Appointment.appointment_datetime)
            try:
                result = await session.execute(query)
                appointments = result.scalars().all()
                return appointments
            except AppointmentsNotFound:
                logger.error(f"Servers Erorrs! Arguments: {tg_id}, {apps_date}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Server error"
                )

    @classmethod
    async def get_user_appointment_by_id_repository(cls, tg_id: int, apps_id: int):
        async with async_session() as session:
            exist_user = await UserRepository.get_user_by_telegram_id_repository(tg_id)
            if not exist_user:
                logger.warning(
                    f"User with tg_id: {tg_id} not founded."
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with telegram id {tg_id}  not founded"
                )

            query = select(Appointment).filter_by(user_id=exist_user.id, id=apps_id)
            try:
                result = await session.execute(query)
                appointments = result.scalar_one_or_none()
                return appointments
            except AppointmentsNotFound:
                logger.error(f"Servers Erorrs! Arguments: {tg_id}, {apps_id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Server error"
                )


    @classmethod
    async def create_user_appointment_repository(cls, tg_id: int, appointments_data: CreateAppointments):
        async with async_session() as session:
            exist_user = await UserRepository.get_user_by_telegram_id_repository(tg_id)
            if not exist_user:
                logger.warning(
                    f"User with tg_id: {tg_id} not founded."
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with telegram id {tg_id}  not founded"
                )

            user_timezone = exist_user.timezone if hasattr(exist_user, 'timezone') else "Europe/Moscow"
            utc_datetime = convert_user_input_to_utc(
                user_date=appointments_data.appointment_date,
                user_time_str=appointments_data.appointment_time,
                user_timezone=user_timezone
            )

            data = appointments_data.model_dump(exclude={'appointment_date', 'appointment_time'})
            stmt = insert(Appointment).values(**data, user_id=exist_user.id, appointment_datetime=utc_datetime).returning(Appointment)
            try:
                new_appointment = await session.execute(stmt)
                await session.commit()
                logger.info(f"Appointment for user {exist_user.telegram_id} {exist_user.nickname} has created. Arguments: {tg_id}")
                return {"message": "Appointment has created."}

            except AppointmentsCreatedError:
                logger.error(f"Servers Erorrs! Arguments: {tg_id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Server error"
                )

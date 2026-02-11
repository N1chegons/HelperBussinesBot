import os
import aiohttp
import json

import logging
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()
base_url = os.getenv("BASE_URL")

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ],
)
logger = logging.getLogger(__name__)

AsyncClient = aiohttp.ClientSession

class AppointmentsBotService:
    @classmethod
    async def get_appointments_bot(cls, telegram_id: int):
        async with AsyncClient() as session:
            params = {
                "telegram_id": telegram_id
            }
            try:
                get_appointments_request = await session.get(f"{base_url}/appointments/get_my_appointments", params=params)
                data_appointment = await get_appointments_request.json()
                if get_appointments_request.status == 200:
                    logger.info(f"The appointments list received successfully, for user id:{telegram_id}")
                    texts = []
                    for i, app in enumerate(data_appointment, 1):
                        dt = datetime.fromisoformat(app['appointment_datetime'])
                        local_dt = dt.astimezone(timezone(timedelta(hours=3)))  # МСК

                        texts.append(
                            f"Встреча №{i}.\n"
                            f"   📅 Дата и время: | {local_dt.strftime('%d.%m.%Y')} | {local_dt.strftime('%H:%M')}\n"
                            f"   📞 Номер телефона собеседника: {app.get('phone', 'Не указан')}\n"
                            f"   📝 Примечание: {app.get('title', 'Без названия')}\n"
                            f"   🔒 ID встречи: {app.get('id')}\n"
                        )

                    return {"text": "💼 Ваши встречи:\n\n" + "\n".join(texts)}

                elif get_appointments_request.status == 404:
                    logger.info(f"User id:{telegram_id} doesn't have appointments")
                    return {"text": f"🗿 У вас нет запланированных встреч."}
                else:
                    logger.warning(f"User id:{telegram_id} doesn't have appointments")
                    return {"text": f"❌ Не удалось получить встречи."}
            except aiohttp.ClientError as e:
                logger.error(
                    f"Network error during appointments. id: {telegram_id}: {e}")
                return {"text": f"🌐 Подключение к серверу потеряно.Попробуйте позже."}

    @classmethod
    async def get_appointments_by_date_bot(cls, telegram_id: int, date: str):
        async with AsyncClient() as session:
            params = {
                "telegram_id": telegram_id,
                "date_apps": date
            }

            try:
                get_tasks_by_date = await session.get(f"{base_url}/appointments/get_my_appointments_by_date")
                data_task_bd = await get_tasks_by_date.json()
                if get_tasks_by_date.status == 200:
                    logger.info(f"The appointments list received successfully, for user id:{telegram_id}")
                    texts = []
                    for i, app in enumerate(data_task_bd, 1):
                        dt = datetime.fromisoformat(app['appointment_datetime'])
                        local_dt = dt.astimezone(timezone(timedelta(hours=3)))  # МСК

                        texts.append(
                            f"Встреча №{i}. 📅 Дата и время: | {local_dt.strftime('%d.%m.%Y')} | {local_dt.strftime('%H:%M')}\n"
                            f"   📞 Номер телефона собеседника: {app.get('phone', 'Не указан')}\n"
                            f"   📝 Примечение {app.get('title', 'Без названия')}\n"      
                            f"   🔒 ID встречи: {app.get('id')}\n"
                        )

                    return {"text": "💼 Ваши встречи:\n\n" + "\n".join(texts)}

                elif get_tasks_by_date.status == 404:
                    logger.info(f"User id:{telegram_id} doesn't have appointments")
                    return {"text": f"🗿 У вас нет запланированных на {date}."}
                else:
                    logger.warning(f"User id:{telegram_id} doesn't have appointments")
                    return {"text": f"❌ Не удалось получить пользователя."}

            except aiohttp.ClientError as e:
                logger.error(
                    f"Network error during appointments. id: {telegram_id}, date: {date}: {e}")
                return {"text": f"🌐 Подключение к серверу потеряно.Попробуйте позже."}


    @classmethod
    async def create_appointment(cls,
                                 telegram_id: int,
                                 phone: str,
                                 date_str: str,
                                 time_str: str,
                                 title: str,
                                 ):
        async with AsyncClient() as session:
            text = ""
            data = {
                "telegram_id": telegram_id,
                "phone": phone,
                "title": title,
                "appointment_date": date_str,
                "appointment_time": time_str,
            }
            try:
                create_appointment_request = await session.post(f"{base_url}/appointments/create_appointment", json=data)
                if create_appointment_request.status == 200:
                    result = await create_appointment_request.json()
                    appointment_id = result.get("appointment_id")

                    logger.info(f"The appointment success created, creator:{telegram_id}")
                    return {"text": f"✅ Встреча создана!\n\n"
                            f"📝 Посмотрите в разделе '📊Мои встречи'",
                            "appointment_id": appointment_id
                            }

                elif create_appointment_request.status == 422:
                    logger.error(f"Validation Error, aegumetns:{telegram_id}")
                    error_data = await create_appointment_request.json()
                    return {"text": "❌ Ошибка валидации:\n"
                            f"{json.dumps(error_data, indent=2)}"}

                else:
                    logger.error(f"The appointment unsuccess created, Arguments:{telegram_id}")
                    return {"text": f"❌ Не удалось создать встречу!\n\n"}

            except aiohttp.ClientError as e:
                logger.error(
                    f"Network error during appointments. id: {telegram_id}: {e}")
                return {"text": f"🌐 Подключение к серверу потеряно.Попробуйте позже."}


    @classmethod
    async def delete_appointment(cls, telegram_id: int, appointment_id: int):
        async with AsyncClient() as session:
            data = {
                "telegram_id": telegram_id,
                "appointment_id": appointment_id
            }
            try:
                create_appointment_request = await session.delete(f"{base_url}/appointments/delete_appointment", params=data)
                if create_appointment_request.status == 200:
                    logger.info(f"The appointment with id:{appointment_id} has deleted, user:{telegram_id}")
                    return {"text": f"✅ Встреча удалена!\n\n"
                                    f"📝 Создайте встречу в разделе '🧾Создать встречу'"
                    }

                elif create_appointment_request.status == 422:
                    logger.error(f"Validation Error, aegumetns:{telegram_id}")
                    error_data = await create_appointment_request.json()
                    return {"text": "❌ Ошибка валидации:\n"
                            f"{json.dumps(error_data, indent=2)}"}

                else:
                    logger.error(f"The appointment unsuccess deleted, Arguments:{telegram_id}")
                    return{"text": f"❌ Не удалось удалить встречу!\n\n"}

            except aiohttp.ClientError as e:
                logger.error(
                    f"Network error during appointments. id: {telegram_id}: {e}")
                return {"text": f"🌐 Подключение к серверу потеряно.Попробуйте позже."}


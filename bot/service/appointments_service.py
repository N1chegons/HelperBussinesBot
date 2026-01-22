import os
import aiohttp

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
            text = ""
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
                            f"   🔸 Статус: {app.get('status', 'pending')}\n"
                        )

                    text = "💼 Ваши встречи:\n\n" + "\n".join(texts)

                elif get_appointments_request.status == 404:
                    logger.info(f"User id:{telegram_id} doesn't have appointments")
                    text = f"🗿 У вас нет запланированных встреч."
                else:
                    logger.warning(f"User id:{telegram_id} doesn't have appointments")
                    text = f"❌ Не удалось получить встречи."
            except aiohttp.ClientError as e:
                logger.error(
                    f"Network error during appointments. id: {telegram_id}: {e}")
                text = f"🌐 Подключение к серверу потеряно.Попробуйте позже."

            return {"text": text}


    @classmethod
    async def create_appointment(cls, telegram_id: int,
        date_str: str,
        time_str: str,
        phone: str,
        title: str = None
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
                    logger.info(f"The appointment success created, creator:{telegram_id}")
                    text = (f"✅ Встреча создана!\n\n"
                            f"📝 Посмотрите в разделе '📊Мои встречи'")

                else:
                    logger.info(f"The appointment success created, creator:{telegram_id}")
                    text = f"❌ Не удалось создать встречу!\n\n"

            except aiohttp.ClientError as e:
                logger.error(
                    f"Network error during appointments. id: {telegram_id}: {e}")
                text = f"🌐 Подключение к серверу потеряно.Попробуйте позже."

            return {"text": text}


    # @classmethod
    # async def get_appointments_by_date_bot(cls, telegram_id: int, date: str):
    #     async with AsyncClient() as session:
    #         text = ""
    #         params = {
    #             "telegram_id": telegram_id,
    #             "date_apps": date
    #         }
    #
    #         try:
    #             get_tasks_by_date = await session.get(f"{base_url}/appointments/get_my_appointments_by_date")
    #             data_task_bd = await get_tasks_by_date.json()
    #             if get_tasks_by_date.status == 200:
    #                 logger.info(f"The appointments list received successfully, for user id:{telegram_id}")
    #                 texts = []
    #                 for i, app in enumerate(data_task_bd, 1):
    #                     dt = datetime.fromisoformat(app['appointment_datetime'])
    #                     local_dt = dt.astimezone(timezone(timedelta(hours=3)))  # МСК
    #
    #                     texts.append(
    #                         f"Встреча №{i}. 📅 Дата и время: | {local_dt.strftime('%d.%m.%Y')} | {local_dt.strftime('%H:%M')}\n"
    #                         f"   📞 Номер телефона собеседника: {app.get('phone', 'Не указан')}\n"
    #                         f"   📝 Примечение {app.get('title', 'Без названия')}\n"
    #                         f"   🔸 Статус: {app.get('status', 'pending')}\n"
    #                     )
    #
    #                 text = "💼 Ваши встречи:\n\n" + "\n".join(texts)
    #
    #             elif get_tasks_by_date.status == 404:
    #                 logger.info(f"User id:{telegram_id} doesn't have appointments")
    #                 text = f"🗿 У вас нет запланированных на {date}."
    #             else:
    #                 logger.warning(f"User id:{telegram_id} doesn't have appointments")
    #                 text = f"❌ Не удалось получить пользователя."
    #
    #         except aiohttp.ClientError as e:
    #             logger.error(
    #                 f"Network error during appointments. id: {telegram_id}, date: {date}: {e}")
    #             text = f"🌐 Подключение к серверу потеряно.Попробуйте позже."
    #
    #         return {"text": text}
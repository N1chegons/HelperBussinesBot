import sys
import os
import aiohttp
from dotenv import load_dotenv
import logging

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

class UserBotService:
    # @staticmethod
    # async def get_user_bot_by_tg_id(telegram_id: int, nickname: str):
    #     async with AsyncClient() as session:
    #         text = "Message for tg id endpoint"
    #         status = True
    #         params = {
    #             "telegram_id": telegram_id
    #         }
    #         try:
    #             request = await session.get(f"{base_url}/user/get_user", params=params)
    #         except aiohttp.ClientError as e:
    #             logger.error(
    #                 f"Network error during user registration {nickname}, id: {telegram_id}: {e}")
    #             text = f"🌐 Подключение к серверу потеряно.Попробуйте позже."
    #             status = False
    #
    #         if request.status == 200:
    #             logger.info(f"The user {nickname}, id:{telegram_id} is already registered.")
    #             text = f"Привет {nickname}\nТы уже зарегестрирован.\nТвой id: {telegram_id}"
    #
    #         return {"status": status, "text": text}
    @classmethod
    async def register_user_bot(cls, telegram_id: int, nickname: str):
        async with AsyncClient() as session:
            try:
                params = {
                    "telegram_id": telegram_id
                }
                get_user_request = await session.get(f"{base_url}/user/get_user", params=params)
                if get_user_request.status == 200:
                    data = await get_user_request.json()
                    logger.info(f"The user {nickname}, id:{telegram_id} is already registered.")
                    return {"text": f"✅ Приветствую {nickname}\n\nТы уже зарегестрирован.\n\nТвой id: {telegram_id}", "timezone": data.get("timezone")}

                elif get_user_request.status == 404:
                    data = {
                        "telegram_id": telegram_id,
                        "nickname": nickname
                    }
                    request = await session.post(f"{base_url}/user/register", json=data)
                    if request.status == 200:
                        logger.info(
                            f"The user {nickname} has registered. Id: {telegram_id}")
                        return {"text": f"🎉 Приветствую {nickname}\n\nТы успешно зарегстрирован.\n\nТвой id: {telegram_id}",  "timezone": data.get("timezone")}

                    else:
                        logger.warning(
                            f"The user {nickname}, id {telegram_id} was unable to register.")
                        return {"text": f"❌ Не получилось зарегестрироваться.",  "timezone": None}

            except aiohttp.ClientError as e:
                logger.error(
                    f"Network error during user registration {nickname}, id: {telegram_id}: {e}")
                return {"text": f"🌐 Подключение к серверу потеряно.Попробуйте позже.",  "timezone": None}


    @classmethod
    async def add_timezone(cls, telegram_id: int, timezone: str):
        async with AsyncClient() as session:
            text = ""
            params = {
                "telegram_id": telegram_id
            }
            get_user_request = await session.get(f"{base_url}/user/get_user", params=params)

            if get_user_request.status != 200:
                logger.error(f"Failed to get user. Status: {get_user_request.status}")
                return {"text": "❌ Ошибка при получении данных пользователя"}

            user_data = await get_user_request.json()

            try:
                if user_data.get('timezone') is None:
                    payload = {
                        "telegram_id": telegram_id,
                        "timezone": timezone
                    }
                    add_timezone_user_request = await session.put(f"{base_url}/user/add_timezone", params=payload)
                    if add_timezone_user_request.status == 200:
                        logger.info(f"The user id:{telegram_id} added the timezone: {timezone}")
                        text = f"✅ Вы успешно добавили ваш часовой пояс: {timezone}"
                    if add_timezone_user_request.status == 422:
                        error_text = await add_timezone_user_request.text()
                        print("="*20,"Error = ", error_text)

                elif user_data.get('timezone') is not None:
                    logger.warning(f"User have timezone {timezone}. Arguments: {timezone}")
                    text = f"✅ Часовой пояс уже известнен: {user_data.get('timezone')}"

                else:
                    logger.warning(f"Can't add a timezone. Arguments: {timezone}")
                    text = f"❌ Не удалось добавить часовой поиск."

            except aiohttp.ClientError as e:
                logger.error(
                    f"Network error. id: {telegram_id}: {e}")
                text = f"🌐 Подключение к серверу потеряно.Попробуйте позже."

            return {"text": text}
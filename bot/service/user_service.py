import sys
import os
import aiohttp

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from bot.logger import get_logger_bot
    logger = get_logger_bot(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

base_url="http://127.0.0.1:1011"
AsyncClient = aiohttp.ClientSession

class UserBotRepository:
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
            text = "Message for crate user"
            data = {
                "telegram_id": telegram_id,
                "nickname": nickname
            }
            params = {
                "telegram_id": telegram_id
            }
            get_user_request = await session.get(f"{base_url}/user/get_user", params=params)
            if get_user_request.status == 200:
                logger.info(f"The user {nickname}, id:{telegram_id} is already registered.")
                text = f"✅ Приветствую {nickname}\n\nТы уже зарегестрирован.\n\nТвой id: {telegram_id}"

            elif get_user_request.status == 404:
                try:
                    request = await session.post(f"{base_url}/user/register", json=data)
                except aiohttp.ClientError as e:
                    logger.error(
                        f"Network error during user registration {nickname}, id: {telegram_id}: {e}")
                    text = f"🌐 Подключение к серверу потеряно.Попробуйте позже."

                if request.status == 200:
                    logger.info(
                        f"The user {nickname} has registered. Id: {telegram_id}")
                    text = f"🎉 Приветствую {nickname}\n\nТы успешно зарегстрирован.\n\nТвой id: {telegram_id}"

                else:
                    logger.warning(
                        f"The user {nickname}, id {telegram_id} was unable to register.")
                    text = f"❌ Не получилось зарегестрироваться."

            return {"text": text}


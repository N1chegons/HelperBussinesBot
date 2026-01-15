import sys
import os
import asyncio


current_dir = sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, current_dir)
from logger import get_logger_bot

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from service.user_service import UserBotRepository

load_dotenv()
logger = get_logger_bot(__name__)

TOKEN = os.getenv("TOKEN_TELEGRAM_BOT")
bot = AsyncTeleBot(TOKEN)

@bot.message_handler(commands=['start'])
async def start(message):
    try:
        register_user = await UserBotRepository.register_user_bot(message.from_user.id, message.from_user.username)
        text_answer = register_user["text"]
        await bot.send_message(message.chat.id, text_answer)

    except Exception as e:
        logger.error(f"Unexpected error during user registration {message.from_user.username}, id: {message.from_user.id}: {e}",
                     exc_info=True)
        text_answer = f"💥 Произошла ошибка. Попробуйте позже или обратитесь к администратору."

        await bot.send_message(message.chat.id, text_answer)

asyncio.run(bot.polling())


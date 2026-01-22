import sys
import os
import asyncio


current_dir = sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, current_dir)
from logger import get_logger_bot

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from service.user_service import UserBotService
from service.appointments_service import AppointmentsBotService

load_dotenv()
logger = get_logger_bot(__name__)

TOKEN = os.getenv("TOKEN_TELEGRAM_BOT")
bot = AsyncTeleBot(TOKEN)

@bot.message_handler(commands=['start'])
async def start_authorisation(message):
    try:
        register_user = await UserBotService.register_user_bot(message.from_user.id, message.from_user.username)
        text_answer = register_user["text"]
        await bot.send_message(message.chat.id, text_answer)
        await bot.send_message(message.chat.id, "📖Чтобы сделать свою личную встречу, напишите в чат или нажмите на: /tasks")

    except Exception as e:
        logger.error(f"Unexpected error during user registration {message.from_user.username}, id: {message.from_user.id}: {e}",
                     exc_info=True)
        text_answer = f"💥 Произошла ошибка. Попробуйте позже или обратитесь к администратору."

        await bot.send_message(message.chat.id, text_answer)


@bot.message_handler(commands=['tasks'])
async def menu(message):
    from telebot import types
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    typese1 = types.KeyboardButton('🧾Создать встречу')
    typese2 = types.KeyboardButton('📊Мои встречи')
    typese3 = types.KeyboardButton('⚙️Профиль')
    # typese4 = types.KeyboardButton('🖥Другое')
    back = types.KeyboardButton('↪️Назад')

    markup.add(typese1, typese2, typese3)

    await bot.send_message(message.chat.id, '🧾 Вы находитесь в меню ваших встреч.\n\n🛠️ При помощи кнопок выберите следующие действия.', reply_markup=markup)

@bot.message_handler(content_types=['text'])
async def bot_message(message):
    if message.chat.type == 'private':
        if message.text == '📊Мои встречи':
            try:
                tasks = await AppointmentsBotService.get_appointments_bot(message.from_user.id)
                text_answer = tasks["text"]
                await bot.send_message(message.chat.id, text_answer)

            except Exception as e:
                logger.error(
                    f"Unexpected error during user registration {message.from_user.username}, id: {message.from_user.id}: {e}",
                    exc_info=True)
                text_answer = f"💥 Произошла ошибка. Попробуйте позже или обратитесь к администратору."

                await bot.send_message(message.chat.id, text_answer)
        elif message.text == '🧾Создать встречу':
            pass
        else:
            await bot.send_message(message.chat.id,
                                   "Я вас не понял:(\n\n"
                                   "📖 Чтобы сделать свою личную встречу, напишите в чат или нажмите на: /tasks\n"
                                   "🗿 Если у вас есть вопросы по поводу работы бота напишите в поддержку.")


asyncio.run(bot.polling())


import sys
import os
import asyncio
import time

from logger import get_logger_bot
from dotenv import load_dotenv
from telebot import types
from telebot.states import StatesGroup, State
from telebot.async_telebot import AsyncTeleBot
from service.user_service import UserBotService
from service.appointments_service import AppointmentsBotService
from timezonefinder import TimezoneFinder

load_dotenv()
logger = get_logger_bot(__name__)

TOKEN = os.getenv("TOKEN_TELEGRAM_BOT")
bot = AsyncTeleBot(TOKEN)
tf = TimezoneFinder()

# STATE
class AppointmentsStates(StatesGroup):
    date = State()
    time = State()
    phone = State()
    title = State()

@bot.message_handler(commands=['start'])
async def start_authorisation(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_location = types.KeyboardButton("📍 Отправить геолокацию", request_location=True)
    markup.add(btn_location)
    try:
        register_user = await UserBotService.register_user_bot(message.from_user.id, message.from_user.username)
        text_answer = register_user["text"]
        timezone = register_user["timezone"]
        await bot.send_message(message.chat.id, text_answer)
        if not timezone:
            time.sleep(1.5)
            await bot.send_message(
                message.chat.id,
                "🛠️ Для настройки напоминаний мне нужна твой часовой пояс.\n\n"
                "🛠️ Отправь свою геолокацию чтобы получать напоминания от бота исходя из вашего часового пояса.",
                reply_markup=markup
            )
        time.sleep(1.5)
        await bot.send_message(message.chat.id,
                               "📖Чтобы сделать свою личную встречу, напишите в чат или нажмите на: /tasks")

    except Exception as e:
        logger.error(f"Unexpected error during user registration {message.from_user.username}, id: {message.from_user.id}: {e}",
                     exc_info=True)
        text_answer = f"💥 Произошла ошибка. Попробуйте позже или обратитесь к администратору."

        await bot.send_message(message.chat.id, text_answer)

# location
@bot.message_handler(content_types=['location'])
async def handle_location(message):
    try:
        lat = message.location.latitude
        lon = message.location.longitude

        timezone_str = tf.timezone_at(lat=lat, lng=lon)

        if not timezone_str:
            await bot.send_message(
                message.chat.id,
                "❌ Не удалось определить таймзону по геолокации.\n"
            )
            return

        if timezone_str:
            put_timezone_user = await UserBotService.add_timezone(message.from_user.id, timezone_str)
            text_answer = put_timezone_user["text"]
            await bot.send_message(
                message.chat.id,
                text_answer,
                reply_markup=types.ReplyKeyboardRemove()
            )
    except Exception as e:
        logger.error(
            f"Unexpected error during user registration {message.from_user.username}, id: {message.from_user.id}: {e}",
            exc_info=True)
        text_answer = f"💥 Произошла ошибка. Попробуйте позже или обратитесь к администратору."

        await bot.send_message(message.chat.id, text_answer)


# ================================= TASKS =================================
user_sessions = {}

# bot menu types
@bot.message_handler(commands=['tasks'])
async def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    typese1 = types.KeyboardButton('🧾Создать встречу')
    typese2 = types.KeyboardButton('📊Мои встречи')
    typese3 = types.KeyboardButton('⚙️Профиль')

    markup.add(typese1, typese2, typese3)

    await bot.send_message(message.chat.id, '🧾 Вы находитесь в меню ваших встреч.\n\n🛠️ При помощи кнопок выберите следующие действия.', reply_markup=markup)

# my appointments
@bot.message_handler(func=lambda m: m.text == '📊Мои встречи')
async def handle_my_appointments(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    but1 = types.KeyboardButton('✂️Изменить встречу')
    but2 = types.KeyboardButton('🗑️Мои встречи')
    but3 = types.KeyboardButton('↩️️Назад')

    markup.add(but1, but2, but3)
    try:
        tasks = await AppointmentsBotService.get_appointments_bot(message.from_user.id)
        text_answer = tasks["text"]
        await bot.send_message(message.chat.id, text_answer, reply_markup=markup)


    except Exception as e:
        logger.error(
            f"Unexpected error during user registration {message.from_user.username}, id: {message.from_user.id}: {e}",
            exc_info=True)
        text_answer = f"💥 Произошла ошибка. Попробуйте позже или обратитесь к администратору."
        await bot.send_message(message.chat.id, text_answer)

# create appointments
@bot.message_handler(func=lambda m: m.text == '🧾Создать встречу')
async def start_creation(message):
    user_sessions[message.from_user.id] = {'step': 'date', 'data': {}}
    await bot.send_message(message.chat.id, "📅 Введите дату (ГГГГ-ММ-ДД):")

@bot.message_handler(func=lambda m: m.from_user.id in user_sessions)
async def handle_session(message):
    user_id = message.from_user.id
    step = user_sessions[user_id]['step']

    if step == 'date':
        user_sessions[user_id]['data']['date'] = message.text
        user_sessions[user_id]['step'] = 'time'
        await bot.delete_message(message.chat.id, message.message_id-1)
        await bot.send_message(message.chat.id, "⏰ Введите время (ЧЧ:ММ):")

    elif step == 'time':
        user_sessions[user_id]['data']['time'] = message.text
        user_sessions[user_id]['step'] = 'phone'
        await bot.delete_message(message.chat.id, message.message_id-1)
        await bot.send_message(message.chat.id, "📞 Введите номер телефона собеседника(поставьте - если не нужно):")

    elif step == 'phone':
        user_sessions[user_id]['data']['phone'] = message.text
        user_sessions[user_id]['step'] = 'title'
        await bot.delete_message(message.chat.id, message.message_id-1)
        await bot.send_message(message.chat.id, "📝 Введите название встречи(поставьте - если не нужно):")

    elif step == 'title':
        user_sessions[user_id]['data']['title'] = message.text

        apps_data = user_sessions[user_id]['data']

        result = await AppointmentsBotService.create_appointment(
            message.from_user.id, apps_data['phone'], apps_data['date'], apps_data['time'], apps_data['title'],
        )
        appointment_id = result.get("appointment_id")

        del user_sessions[user_id]

        markup = types.InlineKeyboardMarkup(row_width=2)

        btn_delete = types.InlineKeyboardButton(
            "🗑️ Удалить встречу",
            callback_data=f"delete_appointment:{appointment_id}" if appointment_id else "delete_appointment"
        )

        btn_recreate = types.InlineKeyboardButton(
            "🔄 Заполнить заново",
            callback_data=f"recreate_appointment:{appointment_id}" if appointment_id else "recreate_appointment"
        )

        markup.add(btn_delete, btn_recreate)

        await bot.delete_message(message.chat.id, message.message_id-1)
        await bot.send_message(
            message.chat.id,
            f"{result['text']}\n\nВыберите действие:",
            reply_markup=markup
        )
        return

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_appointment"))
async def handle_delete_appointment(call):
    try:
        appointment_id = call.data.split(":")[1] if ":" in call.data else None

        if appointment_id:
            result = await AppointmentsBotService.delete_appointment(
                call.from_user.id,
                appointment_id
            )

            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"{result.get('text', '')}",
                reply_markup=None
            )
        else:
            await bot.answer_callback_query(
                call.id,
                "❌ Не удалось удалить встречу: ID не найден",
                show_alert=True
            )

    except Exception as e:
        logger.error(f"Error deleting appointment: {e}")
        await bot.answer_callback_query(
            call.id,
            "💥 Ошибка при удалении встречи",
            show_alert=True
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("recreate_appointment"))
async def handle_recreate_appointment(call):
    user_id = call.from_user.id
    appointment_id = call.data.split(":")[1] if ":" in call.data else None

    if appointment_id:
        result = await AppointmentsBotService.delete_appointment(
            call.from_user.id,
            appointment_id
        )

        if "✅" in result.get('text'):
            user_sessions[user_id] = {
                'step': 'date',
                'data': {}
            }
            await bot.delete_message(call.message.chat.id, call.message.message_id)

            await bot.send_message(
                call.message.chat.id,
                "🔄 Создаем новую встречу...\n\n📅 Введите дату встречи (ДД.ММ.ГГГГ):"
            )
        else:
            await bot.answer_callback_query(
                call.id,
                "❌ Не удалось удалить предыдущую встречу",
                show_alert=True
            )
    else:
        user_sessions[user_id] = {
            'step': 'date',
            'data': {}
        }
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        await bot.send_message(
            call.message.chat.id,
            "🔄 Создаем новую встречу...\n\n📅 Введите дату встречи (ДД.ММ.ГГГГ):"
        )

# ================================= TASKS =================================

asyncio.run(bot.polling())

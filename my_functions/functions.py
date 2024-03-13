import asyncio
import csv
import logging
import datetime

import requests as requests
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from data_bases.connect_data_base import connect_db, DB_NAME
from aiogram import types, Bot
from config_data.config import Config, load_config
from lexicon.lexicon import LEXICON_RU

logging.basicConfig(level=logging.INFO)
config: Config = load_config()

# Инициализируем бот и диспетчер
bot = Bot(token=config.tg_bot.token)



async def check_club_state(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"SELECT club FROM users WHERE user_id = {message.from_user.id}")
    in_club = cursor.fetchone()[0]
    return in_club == 'да'

async def delete_message(message: types.Message, delay: int):
    await asyncio.sleep(delay)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

async def delete_callback_message(message_id, chat_id, time):
    await asyncio.sleep(time)
    await bot.delete_message(chat_id, message_id)


async def send_message_to_user(user_id: int, message: str):
    await bot.send_message(user_id, message)
# Функция для отправки PDF файла
async def send_pdf(chat_id: int, pdf_path: str, bot_token: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    files = {"document": open(pdf_path, "rb")}
    data = {"chat_id": chat_id}
    response = requests.post(url, data=data, files=files)
    if response.status_code == 200:
        logging.info("PDF file sent successfully!")
        return True
    else:
        logging.error("Failed to send PDF file.")
        return False

async def convert_db_to_csv():
    connect, cursor = connect_db(DB_NAME)
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()

    with open('output.csv', 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(rows)
async def send_message_on_time(message: types.Message, msg, seconds, second_to_del, kb=None, parse_mode=None):
    current_time = datetime.datetime.now()
    if current_time.hour >= 8 and current_time.hour < 23:
        delta = datetime.timedelta(seconds=seconds) #
        send_time = current_time + delta
    else:
        send_time = current_time.replace(hour=10, minute=0, second=0) + datetime.timedelta(days=1)

    time_diff = (send_time - current_time).total_seconds()
    await asyncio.sleep(time_diff)
    msg1 = await message.answer(msg, reply_markup=kb, parse_mode=parse_mode)
    asyncio.create_task(delete_message(msg1, second_to_del))




async def send_photo_on_time(message: types.Message, photo, cap, seconds, seconds_to_del, parse_mode):
    current_time = datetime.datetime.now()

    if current_time.hour >= 8 and current_time.hour < 23:
        delta = datetime.timedelta(seconds=seconds) #
        send_time = current_time + delta
    else:
        send_time = current_time.replace(hour=10, minute=0, second=0) + datetime.timedelta(days=1)

    time_diff = (send_time - current_time).total_seconds()
    await asyncio.sleep(time_diff)
    msg1 = await message.answer_photo(photo=photo, caption=cap, parse_mode=parse_mode)
    asyncio.create_task(delete_message(msg1, seconds_to_del))

async def send_kb_yes_no(message: types.Message):
    button_yes = KeyboardButton(text='Да✅')
    button_no = KeyboardButton(text='Нет❌')
    keyboard_yes_no = ReplyKeyboardMarkup(
        keyboard=[[button_yes],
                  [button_no]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    msg = await message.answer(f"{message.from_user.username}, у вас\n"
                               f"открылось предложение?\n",
                               reply_markup=keyboard_yes_no)
    asyncio.create_task(delete_message(msg, 10)) # 1 час

async def create_kb(button):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=button)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return kb

async def send_two_day_msgs(message: types.Message):
    await asyncio.sleep(10) # 2 часа

    msg_artist_should_know = await message.answer(LEXICON_RU['msg_artist_should_know'])
    asyncio.create_task(delete_message(msg_artist_should_know, 30)) # 6 часов
    await asyncio.sleep(30)  # 6 часов

    msg_5years_more = await message.answer(LEXICON_RU['msg_5years_more'])
    asyncio.create_task(delete_message(msg_5years_more, 10))  # 1 часов
    await asyncio.sleep(10)  # 1 час

    msg_reviews = await message.answer(LEXICON_RU['msg_reviews'])
    asyncio.create_task(delete_message(msg_reviews, 60))  # 12 часов или не удалять
    await asyncio.sleep(5)  # 15 мин

    msg_next_offer = await message.answer(LEXICON_RU['msg_next_offer'])
    asyncio.create_task(delete_message(msg_next_offer, 15))  # 3 часа
    await asyncio.sleep(15)  # 3 часа

    msg_error_num1_offer = await message.answer(LEXICON_RU['msg_error_num1_offer'])
    asyncio.create_task(delete_message(msg_error_num1_offer, 30))  # 6 часов
    await asyncio.sleep(30)  # 6 часов

    msg_5_reasons_1 = await message.answer(LEXICON_RU['msg_5_reasons_1'])
    msg_5_reasons_2 = await message.answer(LEXICON_RU['msg_5_reasons_2'])
    asyncio.create_task(delete_message(msg_5_reasons_1, 25))  # 5 часов
    asyncio.create_task(delete_message(msg_5_reasons_2, 25))  # 5 часов
    await asyncio.sleep(25)  # 5 часов

    msg_last_chance = await message.asnwer(LEXICON_RU['msg_last_chance'])
    asyncio.create_task(delete_message(msg_last_chance, 10))  # 59минут



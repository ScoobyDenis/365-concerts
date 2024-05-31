import asyncio
import csv
import logging
import datetime

import requests as requests
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from data_bases.connect_data_base import connect_db, DB_NAME, ADMINS
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

async def check_bot_state(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"SELECT bot_status FROM users WHERE user_id = {message.from_user.id}")
    return cursor.fetchone()[0] == 'on'

async def change_bot_state_to_off(user_id):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET bot_status = '{'off'}'  WHERE user_id = {user_id}")
    connect.commit()
    # cursor.execute(f"SELECT bot_status FROM users WHERE user_id = {user_id}")
    # print(cursor.fetchone())

async def delete_message(message: types.Message, delay: int):
    await asyncio.sleep(delay)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

async def delete_callback_message(message_id, chat_id, time):
    await asyncio.sleep(time)
    await bot.delete_message(chat_id, message_id)

async def send_message_to_user(user_id: int, message: str):
    await bot.send_message(user_id, message)

async def send_msg_to_admins(message, msg):
    try:
        await bot.send_message(user_id=-1002191031861, text=f'{"@" + message.from_user.username} - {msg}')
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


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
    if current_time.hour >= 7 and current_time.hour < 20:
        delta = datetime.timedelta(seconds=seconds) #
        send_time = current_time + delta
    else:
        send_time = current_time.replace(hour=10, minute=0, second=0) + datetime.timedelta(days=1)

    time_diff = (send_time - current_time).total_seconds()
    await asyncio.sleep(time_diff)
    msg1 = await message.answer(msg, reply_markup=kb, parse_mode=parse_mode)
    asyncio.create_task(delete_message(msg1, second_to_del))

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
    asyncio.create_task(delete_message(msg, 3600/100)) # 1 час


async def create_kb(button):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=button)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return kb

async def wait_until(hour, min):
    current_time = datetime.datetime.now().time()
    target_time = datetime.time(hour, min, 0)

    if current_time < target_time:
        delta = datetime.datetime.combine(datetime.date.today(), target_time) - datetime.datetime.now()
    else:
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        delta = datetime.datetime.combine(tomorrow.date(), target_time) - datetime.datetime.now()

    delta_seconds = delta.total_seconds()
    await asyncio.sleep(delta_seconds)

async def send_two_day_msgs(message: types.Message):
    if await check_bot_state(message):
        await wait_until(8, 30) # 11 30
        msg_artist_should_know = await message.answer(LEXICON_RU['msg_artist_should_know'],
                                                      reply_markup=await create_kb('Перестать пахать за копейки🤑'))
        asyncio.create_task(delete_message(msg_artist_should_know, 21600))  # 6 часов
        await asyncio.sleep(21605)  # 6 часов

    if await check_bot_state(message):
        msg_5years_more = await message.answer(LEXICON_RU['msg_5years_more'])
        asyncio.create_task(delete_message(msg_5years_more, 3600))  # 1 часов
        await asyncio.sleep(3600)  # 1 час

    if await check_bot_state(message):
        msg_reviews = await message.answer(LEXICON_RU['msg_reviews'])
        await asyncio.sleep(900)  # 15 мин

    if await check_bot_state(message):
        msg_next_offer = await message.answer(LEXICON_RU['msg_next_offer'])
        asyncio.create_task(delete_message(msg_next_offer, 10800))  # 3 часа
        await asyncio.sleep(10800)  # 3 часа

    if await check_bot_state(message):
        await wait_until(9, 30) # 12 30
        msg_error_num1_offer = await message.answer(LEXICON_RU['msg_error_num1_offer'],
                                                    reply_markup=await create_kb('Присоединиться к клубу 🔥'))
        asyncio.create_task(delete_message(msg_error_num1_offer, 21600))  # 6 часов
        await asyncio.sleep(21605)  # 5 часов

    if await check_bot_state(message):
        msg_5_reasons_1 = await message.answer(LEXICON_RU['msg_5_reasons_1'])
        msg_5_reasons_2 = await message.answer(LEXICON_RU['msg_5_reasons_2'],
                                               reply_markup=await create_kb('бронировать участие 👌'))
        asyncio.create_task(delete_message(msg_5_reasons_1, 16200))  # 4:30 часов
        asyncio.create_task(delete_message(msg_5_reasons_2, 16200))  # 4:30 часов
        await asyncio.sleep(3600)  # 1 час
    if await check_bot_state(message):
        msg_last_chance = await message.answer(LEXICON_RU['msg_last_chance'],
                                               reply_markup=await create_kb('приобрести участие'))
        asyncio.create_task(delete_message(msg_last_chance, 3540))  # 59минут


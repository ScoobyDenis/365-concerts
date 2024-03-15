import asyncio
import re
from aiogram import types, F
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, FSInputFile, InlineKeyboardButton, \
    InlineKeyboardMarkup, CallbackQuery
from lexicon.lexicon import LEXICON_RU
from config_data.config import Config, load_config
from data_bases.connect_data_base import connect_db, DB_NAME, ADMINS
from my_functions.functions import *
from filters.filters import *
config: Config = load_config()

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"SELECT * FROM users WHERE user_id = {message.from_user.id}")
    user = cursor.fetchone()
    if user:
        pass
    else:
        await message.answer(message.from_user.first_name + ', ' + LEXICON_RU['/start'])
        await send_pdf(message.from_user.id, "files/formula.pdf", config.tg_bot.token)

        data = [message.from_user.id, '@'+message.from_user.username, 0, 0, 'нет', '-', 0, 0, 0, 0, 'on']
        cursor.execute("INSERT INTO users (user_id, user_name, mark1, mark2, club, offer_status, mark3, mark4, mark5, mark6, bot_status)  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
        connect.commit()

        await send_message_on_time(message,
                                   LEXICON_RU['msg2_youtube'],
                                   300,  # 5мин
                                   14400,  # 4 часа
                                   kb=await create_kb('Получить запись'))

        offer_1_pic = FSInputFile("files/offer_1.jpg")
        await send_photo_on_time(message,
                                 photo=offer_1_pic,
                                 cap=LEXICON_RU['msg3_offer'],
                                 seconds=15000, #4часа 10мин
                                 seconds_to_del=82800, #23 часа
                                 parse_mode='HTML')
        await asyncio.sleep(82800)
        # проверка писал ли пользователь клуб. если нет то шлем контент дальше
        if await check_club_state(message):
            pass
        else:
            await send_message_on_time(message,
                                       LEXICON_RU['msg4_youtube'],
                                       30, # после задержки 23 часа
                                       14400, # 4часа
                                       kb=await create_kb('Не хотят отдавать гонорар!😡'))

            await asyncio.sleep(14400)
            msg_reels_rules = await message.answer(LEXICON_RU['msg5'], parse_mode='HTML')



@router.message(Command('admin'))
async def get_admin_menu(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer("Команды администратора:\n"
                             "/stats - общая статистика по меткам\n"
                            "/get_file - получить таблицу со всей информацией\n"
                             "/bot_off username - отключение бота")

@router.message(Command('get_file'))
async def send_file(message: types.Message):
    if message.from_user.id in ADMINS:
        await convert_db_to_csv()
        await message.reply_document(FSInputFile('output.csv'))
        await message.answer("mark1 - 'Почему не готовы'"
                             "mark2 - 'Антикидалово'"
                             "mark3 - 'Это должен знать каждый артист'"
                             "mark4 - 'Ошибка N1'"
                             "mark5 - '5 ПРИЧИН'"
                             "mark6 - 'Последний шанс'")

@router.message(Command('bot_off'))
async def send_file(message: types.Message):
    if message.from_user.id in ADMINS:
        try:
            command, user_id = message.text.split(maxsplit=1)
            try:
                await change_bot_state_to_off(user_id)
                await message.answer(f"Пользователь {user_id} отключен от бота")
            except Exception as e:
                await message.answer("Не правильно введен id пользователя")
        except ValueError:
            await message.answer("Пожалуйста, укажите id после команды /get_user_status\n"
                                 "id есть в таблице /get_file")
@router.message(Command('stats'))
async def check_marks(message: types.Message):
    if message.from_user.id in ADMINS:
        connect, cursor = connect_db(DB_NAME)
        cursor.execute(f"SELECT SUM(mark1) FROM users")
        sum_marks1 = cursor.fetchone()[0]
        cursor.execute(f"SELECT SUM(mark2) FROM users")
        sum_marks2 = cursor.fetchone()[0]
        cursor.execute(f"SELECT SUM(mark3) FROM users")
        sum_marks3 = cursor.fetchone()[0]
        cursor.execute(f"SELECT SUM(mark4) FROM users")
        sum_marks4 = cursor.fetchone()[0]
        cursor.execute(f"SELECT SUM(mark5) FROM users")
        sum_marks5 = cursor.fetchone()[0]
        cursor.execute(f"SELECT SUM(mark6) FROM users")
        sum_marks6 = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM users")
        size_db = cursor.fetchone()[0]
        await message.answer(f"Всего человек зашло в бота: <b>{size_db}</b>\n"
                             f"По метке 'Почему не готовы' перешло: <b>{sum_marks1}</b>\n"
                             f"По метке 'Антикидалово' перешло: <b>{sum_marks2}</b>\n"
                             f"По метке 'club offer Это должен знать каждый артист' перешло: <b>{sum_marks3}</b>\n"
                             f"По метке 'club offer Ошибка N1' перешло: <b>{sum_marks4}</b>\n"
                             f"По метке 'club offer 5 ПРИЧИН' перешло: <b>{sum_marks5}</b>\n"
                             f"По метке 'club offer Последний шанс' перешло: <b>{sum_marks6}</b>", parse_mode='HTML')

@router.message(F.text=="Получить запись")
async def cmd_youtube_filter1(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET mark1 =  mark1 + 1 WHERE user_id = {message.from_user.id}")
    connect.commit()

    msg1_youtube_filter1 = await message.answer(f"{'https://youtu.be/8Z4aFPKMPkE'}\n")
    await asyncio.sleep(60) #1min
    msg2_youtube_filter1 = await message.answer(LEXICON_RU['msg2_youtube_filter1'])

    asyncio.create_task(delete_message(msg2_youtube_filter1, 10800)) #3часа
    asyncio.create_task(delete_message(msg1_youtube_filter1, 14400))  # 4часа
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.text=="Не хотят отдавать гонорар!😡")
async def cmd_youtube_filter2(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET mark2 = mark2 + 1 WHERE user_id = {message.from_user.id}")
    connect.commit()
    msg1_youtube_filter2 = await message.answer(f"{'https://youtu.be/4Ltp7kyoZrg'}\n")
    await asyncio.sleep(5)  # сразу
    msg2_youtube_filter2 = await message.answer(LEXICON_RU['msg2_youtube_filter2'])
    asyncio.create_task(delete_message(msg2_youtube_filter2, 10800)) #3часа
    asyncio.create_task(delete_message(msg1_youtube_filter2, 86400))  # 24часа
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.text=='Да✅')
async def process_buttons_press_yes(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET offer_status = 'Да' WHERE user_id = {message.from_user.id}")
    connect.commit()

    msg_personal_yes = await message.answer(LEXICON_RU['msg_personal'])
    asyncio.create_task(delete_message(msg_personal_yes, 7200))  # 2 часа
    await asyncio.sleep(7200)  # 2 часа

    if await check_bot_state(message):
        msg_artist_should_know = await message.answer(LEXICON_RU['msg_artist_should_know'], reply_markup=await create_kb('Получить ссылку 🔗'))
        asyncio.create_task(delete_message(msg_artist_should_know, 21600))  # 6 часов
        await asyncio.sleep(21605)  # 6 часов

    if await check_bot_state(message):
        msg_5years_more = await message.answer(LEXICON_RU['msg_5years_more'])
        asyncio.create_task(delete_message(msg_5years_more, 3600))  # 1 часов
        await asyncio.sleep(3605)  # 1 час

    if await check_bot_state(message):
        msg_reviews = await message.answer(LEXICON_RU['msg_reviews'])
        await asyncio.sleep(900)  # 15 мин

    if await check_bot_state(message):
        msg_next_offer = await message.answer(LEXICON_RU['msg_next_offer'])
        asyncio.create_task(delete_message(msg_next_offer, 10800))  # 3 часа
        await asyncio.sleep(10805)  # 3 часа

    if await check_bot_state(message):
        msg_error_num1_offer = await message.answer(LEXICON_RU['msg_error_num1_offer'], reply_markup=await create_kb('Присоединиться к клубу 🔥'))
        asyncio.create_task(delete_message(msg_error_num1_offer, 21600))  # 6 часов
        await asyncio.sleep(21605)  # 6 часов

    if await check_bot_state(message):
        msg_5_reasons_1 = await message.answer(LEXICON_RU['msg_5_reasons_1'])
        msg_5_reasons_2 = await message.answer(LEXICON_RU['msg_5_reasons_2'], reply_markup=await create_kb('бронировать участие 👌'))
        asyncio.create_task(delete_message(msg_5_reasons_1, 16200))  # 4:30 часов
        asyncio.create_task(delete_message(msg_5_reasons_2, 16200))  # 4:30 часов
        await asyncio.sleep(16205)  # 5 часов

    if await check_bot_state(message):
        msg_last_chance = await message.answer(LEXICON_RU['msg_last_chance'], reply_markup=await create_kb('приобрести участие'))
        asyncio.create_task(delete_message(msg_last_chance, 3540))  # 59минут
        # сообщение админу?



@router.message(F.text=='Нет❌')
async def process_buttons_press_no(message: types.Message):
    msg_not_open = await message.answer(LEXICON_RU['msg_not_open'])
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET offer_status = 'Нет' WHERE user_id = {message.from_user.id}")
    connect.commit()
    await send_msg_to_admins(message, 'нажал кнопку, что оффер не открывается')
    await asyncio.sleep(30)  #30сек
    msg_personal_no = await message.answer(LEXICON_RU['msg_personal'])
    asyncio.create_task(delete_message(msg_not_open, 7200))  # 2часа
    asyncio.create_task(delete_message(msg_personal_no, 7200))  # 2часа, может больше?

@router.message(F.text=='приобрести участие')
async def get_offer_last_chance(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET mark6 =  mark6 + 1 WHERE user_id = {message.from_user.id}")
    connect.commit()
    await send_msg_to_admins(message, 'пришел последний "шанс"')
    msg = await message.answer(LEXICON_RU['msg_last_chance_kb'])
    asyncio.create_task(delete_message(msg, 3300)) # 58 минут
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.text=='бронировать участие 👌')
async def get_offer_five_reasons(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET mark5 =  mark5 + 1 WHERE user_id = {message.from_user.id}")
    connect.commit()
    await send_msg_to_admins(message, 'получил ссылку "5 причин..."')
    msg = await message.answer(LEXICON_RU['msg_5_reasons_kb'])
    asyncio.create_task(delete_message(msg, 18000)) # 5 часов
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.text=='Получить ссылку 🔗')
async def get_offer_after_artist_should_know(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET mark3 =  mark3 + 1 WHERE user_id = {message.from_user.id}")
    connect.commit()
    await send_msg_to_admins(message, 'получил ссылку "Каждый артист.."')
    msg = await message.answer(LEXICON_RU['msg_artist_should_know_kb'])
    asyncio.create_task(delete_message(msg, 21600)) # 6 часов
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.text=='Присоединиться к клубу 🔥')
async def get_offer_after_artist_should_know(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET mark4 =  mark4 + 1 WHERE user_id = {message.from_user.id}")
    connect.commit()
    await send_msg_to_admins(message, 'Ошибка номер 1')
    msg = await message.answer(LEXICON_RU['msg_error_num1_offer_kb'])
    asyncio.create_task(delete_message(msg, 21600)) # 6 часов
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.text.in_(['клуб', 'Клуб', 'КЛУБ', '"КЛУБ"', 'rke,', 'RKE,']))
async def cmd_club_react(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"SELECT club FROM users WHERE user_id = {message.from_user.id}")
    if cursor.fetchone()[0] == 'да':
        await message.answer('Возможно ваше предложение уже истекло.\n'
                             'Наш менеджер свяжется с вами в ближайшее время\n'
                             'и сообщит новые условия')
        await send_msg_to_admins(message, 'написал "КЛУБ" второй раз')
    else:
        cursor.execute(f"UPDATE users SET club = '{'да'}' WHERE user_id = {message.from_user.id}")
        connect.commit()
        await send_msg_to_admins(message, 'написал "КЛУБ"')
        msg_club_offer = await message.answer(f"{message.from_user.first_name}, ваше персональное предложение по закрытому клубу доступно по этой ссылке👇\n\n"
                                 f"{'https://365concerts.ru/club_bot_149'}\n\n"
                                 f"Переходите, предложение доступно\n"
                                 f"2 дня")

        asyncio.create_task(delete_message(msg_club_offer, 3600))  # через час
        await asyncio.sleep(1800) # 30мин
        await send_kb_yes_no(message)
        await asyncio.sleep(3700) #подождать чуть больше часа пока кнопки пропадут
        # Проверка нажал ли кнопку
        cursor.execute(f"SELECT offer_status FROM users WHERE user_id = {message.from_user.id};")
        offer_status = cursor.fetchone()[0]
        if offer_status == '-':
            msg_you_asked = await message.answer(LEXICON_RU['msg_you_asked'])
            asyncio.create_task(delete_message(msg_you_asked, 3600))  # 1час
            await asyncio.sleep(7200) #1час? может больше, надо спросить?
            await send_kb_yes_no(message)
            await asyncio.sleep(3600)  # 1час? может больше, надо спросить?
            msg_not_open = await message.answer(LEXICON_RU['msg_not_open'])




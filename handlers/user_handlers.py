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

        data = [message.from_user.id, '@'+message.from_user.username, 0, 0, 'нет', '-', 0, 0, 0, 0]
        cursor.execute("INSERT INTO users (user_id, user_name, mark1, mark2, club, offer_status, mark3, mark4, mark5, mark6)  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
        connect.commit()

        await send_message_on_time(message,
                                   LEXICON_RU['msg2_youtube'],
                                   5,  # 5мин
                                   25,  # 4 часа
                                   kb=await create_kb('Получить запись'))

        await asyncio.sleep(10)  # 1час

        offer_1_pic = FSInputFile("files/offer_1.jpg")
        await send_photo_on_time(message,
                                 photo=offer_1_pic,
                                 cap=LEXICON_RU['msg3_offer'],
                                 seconds=25, #4часа 10мин
                                 seconds_to_del=20,
                                 parse_mode='HTML')
        await asyncio.sleep(10)
        # проверка писал ли пользователь клуб. если нет то шлем контент дальше
        if await check_club_state(message):
            pass
        else:

            button_youtube_2 = KeyboardButton(text='Не хотят отдавать гонорар!')
            keyboard_youtube2 = ReplyKeyboardMarkup(
                keyboard=[[button_youtube_2]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            await send_message_on_time(message,
                                       LEXICON_RU['msg4_youtube'],
                                       24,
                                       24,
                                       kb=await create_kb('Не хотят отдавать гонорар!😡'))

            await send_message_on_time(message,
                                       LEXICON_RU['msg5'],
                                       45,  # 24 часа
                                       15,  # через сколько удалить?
                                       parse_mode='HTML')



@router.message(Command('admin'))
async def get_admin_menu(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer("Команды администратора:\n"
                             "/stats - общая статистика по меткам\n"
                            "/get_file - получить таблицу со всей информацией")

@router.message(Command('get_file'))
async def send_file(message: types.Message):
    if message.from_user.id in ADMINS:
        await convert_db_to_csv()
        await message.reply_document(FSInputFile('output.csv'))

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
                             f"По метке 'Почему профессиональные музыканты...' перешло: <b>{sum_marks1}</b>\n"
                             f"По метке 'Не хотят отдавать гонорар' перешло: <b>{sum_marks2}</b>\n"
                             f"По метке 'Это должен знать каждый артист' перешло: <b>{sum_marks3}</b>\n"
                             f"По метке 'Ошибка N1' перешло: <b>{sum_marks4}</b>\n"
                             f"По метке '5 ПРИЧИН' перешло: <b>{sum_marks5}</b>\n"
                             f"По метке 'Последний шанс' перешло: <b>{sum_marks6}</b>", parse_mode='HTML')





@router.message(F.text=="Получить запись")
async def cmd_youtube_filter1(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET mark1 =  mark1 + 1 WHERE user_id = {message.from_user.id}")
    connect.commit()


    msg1_youtube_filter1 = await message.answer(f"{'https://youtu.be/8Z4aFPKMPkE'}\n")
    await asyncio.sleep(5) #1min
    msg2_youtube_filter1 = await message.answer(LEXICON_RU['msg2_youtube_filter1'])

    asyncio.create_task(delete_message(msg2_youtube_filter1, 20)) #3часа
    asyncio.create_task(delete_message(msg1_youtube_filter1, 25))  # 4часа
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.text=="Не хотят отдавать гонорар!😡")
async def cmd_youtube_filter2(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET mark2 = mark2 + 1 WHERE user_id = {message.from_user.id}")
    connect.commit()
    msg1_youtube_filter2 = await message.answer(f"{'https://youtu.be/4Ltp7kyoZrg'}\n")
    await asyncio.sleep(5)  # 1min
    msg2_youtube_filter2 = await message.answer(LEXICON_RU['msg2_youtube_filter2'])
    asyncio.create_task(delete_message(msg2_youtube_filter2, 15)) #3часа
    asyncio.create_task(delete_message(msg1_youtube_filter2, 35))  # 24часа
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.text=='Да✅')
async def process_buttons_press_yes(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET offer_status = 'Да' WHERE user_id = {message.from_user.id}")
    connect.commit()

    msg_personal_yes = await message.answer(LEXICON_RU['msg_personal'])
    asyncio.create_task(delete_message(msg_personal_yes, 30))  # 2 часа
    await asyncio.sleep(10)  # 2 часа

    msg_artist_should_know = await message.answer(LEXICON_RU['msg_artist_should_know'], reply_markup=await create_kb('Получить ссылку 🔗'))
    asyncio.create_task(delete_message(msg_artist_should_know, 30))  # 6 часов
    await asyncio.sleep(30)  # 6 часов

    msg_5years_more = await message.answer(LEXICON_RU['msg_5years_more'])
    asyncio.create_task(delete_message(msg_5years_more, 10))  # 1 часов
    await asyncio.sleep(10)  # 1 час

    msg_reviews = await message.answer(LEXICON_RU['msg_reviews'])
    await asyncio.sleep(5)  # 15 мин

    msg_next_offer = await message.answer(LEXICON_RU['msg_next_offer'])
    asyncio.create_task(delete_message(msg_next_offer, 15))  # 3 часа
    await asyncio.sleep(15)  # 3 часа

    msg_error_num1_offer = await message.answer(LEXICON_RU['msg_error_num1_offer'], reply_markup=await create_kb('Присоединиться к клубу 🔥'))
    asyncio.create_task(delete_message(msg_error_num1_offer, 30))  # 6 часов
    await asyncio.sleep(30)  # 6 часов

    msg_5_reasons_1 = await message.answer(LEXICON_RU['msg_5_reasons_1'])
    msg_5_reasons_2 = await message.answer(LEXICON_RU['msg_5_reasons_2'], reply_markup=await create_kb('бронировать участие 👌'))
    asyncio.create_task(delete_message(msg_5_reasons_1, 25))  # 5 часов
    asyncio.create_task(delete_message(msg_5_reasons_2, 25))  # 5 часов
    await asyncio.sleep(25)  # 5 часов

    msg_last_chance = await message.answer(LEXICON_RU['msg_last_chance'], reply_markup=await create_kb('приобрести участие'))
    asyncio.create_task(delete_message(msg_last_chance, 10))  # 59минут
    # await send_two_day_msgs(message)



@router.message(F.text=='Нет❌')
async def process_buttons_press_no(message: types.Message):
    msg_not_open = await message.answer(LEXICON_RU['msg_not_open'])
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET offer_status = 'Нет' WHERE user_id = {message.from_user.id}")
    connect.commit()
    await bot.send_message(1372933011, f'{"@" + message.from_user.username} - нажал кнопку, что оффер не открывается')
    await asyncio.sleep(3)  #30сек
    msg_personal_no = await message.answer(LEXICON_RU['msg_personal'])
    asyncio.create_task(delete_message(msg_not_open, 10))  # 2часа
    asyncio.create_task(delete_message(msg_personal_no, 10))  # 2часа

@router.message(F.text=='приобрести участие')
async def get_offer_last_chance(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET mark6 =  mark6 + 1 WHERE user_id = {message.from_user.id}")
    connect.commit()
    await bot.send_message(1372933011, f'{"@" + message.from_user.username} - пришел последний шанс"')
    msg = await message.answer(LEXICON_RU['msg_last_chance_kb'])
    asyncio.create_task(delete_message(msg, 10)) # 59 часов
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.text=='бронировать участие 👌')
async def get_offer_five_reasons(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET mark5 =  mark5 + 1 WHERE user_id = {message.from_user.id}")
    connect.commit()
    await bot.send_message(1372933011, f'{"@" + message.from_user.username} - получил ссылку "5 причин..."')
    msg = await message.answer(LEXICON_RU['msg_5_reasons_kb'])
    asyncio.create_task(delete_message(msg, 25)) # 5 часов
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.text=='Получить ссылку 🔗')
async def get_offer_after_artist_should_know(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET mark3 =  mark3 + 1 WHERE user_id = {message.from_user.id}")
    connect.commit()
    await bot.send_message(1372933011, f'{"@" + message.from_user.username} - получил ссылку "Каждый артист.."')
    msg = await message.answer(LEXICON_RU['msg_artist_should_know_kb'])
    asyncio.create_task(delete_message(msg, 30)) # 6 часов
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.text=='Присоединиться к клубу 🔥')
async def get_offer_after_artist_should_know(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"UPDATE users SET mark4 =  mark4 + 1 WHERE user_id = {message.from_user.id}")
    connect.commit()
    msg = await message.answer(LEXICON_RU['msg_error_num1_offer_kb'])
    asyncio.create_task(delete_message(msg, 30)) # 6 часов
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.text.in_(['клуб', 'Клуб', 'КЛУБ', '"КЛУБ"', 'rke,', 'RKE,']))
async def cmd_club_react(message: types.Message):
    connect, cursor = connect_db(DB_NAME)
    cursor.execute(f"SELECT club FROM users WHERE user_id = {message.from_user.id}")
    if cursor.fetchone()[0] == 'да':
        pass
    else:
        cursor.execute(f"UPDATE users SET club = '{'да'}' WHERE user_id = {message.from_user.id}")
        connect.commit()
        await bot.send_message(1372933011, f'{"@"+message.from_user.username} - написал "КЛУБ"')
        msg_club_offer = await message.answer(f"{message.from_user.first_name}, ваше персональное предложение по закрытому клубу доступно по этой ссылке👇\n\n"
                                 f"{'https://365concerts.ru/club_bot_149'}\n\n"
                                 f"Переходите, предложение доступно\n"
                                 f"2 дня")

        asyncio.create_task(delete_message(msg_club_offer, 10))  # через час
        await asyncio.sleep(10)
        await send_kb_yes_no(message)
        await asyncio.sleep(13) #подождать чуть больше часа пока кнопки пропадут
        # Проверка нажал ли кнопку
        cursor.execute(f"SELECT offer_status FROM users WHERE user_id = {message.from_user.id};")
        offer_status = cursor.fetchone()[0]
        if offer_status == '-':
            msg_you_asked = await message.answer(LEXICON_RU['msg_you_asked'])
            asyncio.create_task(delete_message(msg_you_asked, 10))  # 1час
            await asyncio.sleep(10) #1час?
            await send_kb_yes_no(message)
            await asyncio.sleep(10)  # 1час?
            msg_not_open = await message.answer(LEXICON_RU['msg_not_open'])




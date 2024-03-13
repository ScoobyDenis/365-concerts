import asyncio

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from data_bases.connect_data_base import connect_db, DB_NAME, ADMINS
from aiogram import types, F

from lexicon.lexicon import LEXICON_RU
from my_functions.functions import *

router = Router()


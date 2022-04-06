import logging
import time
import pprint  # импортируем pprint
import gspread
# -*- coding: utf8 -*-

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,\
    InlineKeyboardButton
import asyncio


from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

from oauth2client.service_account import ServiceAccountCredentials  # Ипортируем ServiceAccountCredentials(GoogleSheets)
from redis import Redis
from rq import Queue


import config  # ИМПОРТИРУЕМ ДАННЫЕ ИЗ ФАЙЛОВ config.py
import keyboard  # ИМПОРТИРУЕМ ДАННЫЕ ИЗ ФАЙЛОВ keyboard.py
import gsheets



storage = MemoryStorage()  # FOR FSM
bot = Bot(token=config.botkey, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,)

q = Queue(connection=Redis())

link = gsheets.link  # Задаем ссылку на Гугл таблици
# Формируем данные для входа из нашего json файла
sheets = gsheets.sheets
client = gsheets.client  # Запускаем клиент для связи с таблицами
sheet = gsheets.sheet  # Открываем нужную на таблицу и лист
printf = pprint.PrettyPrinter()  # Описываем прити принт

with open('pins.txt', 'r') as f:  # Открываем файл с ПИН кодами
    users = [i.rstrip() for i in f]
# users = open('pins.txt', 'r').read()  # Open pin file(a txt document with pin list)
get_data = sheet.get_all_records()  # Получаем все данные из таблицы
user_id: int = 0


def coords(user):  # find a in in google sheet
    for n in range(2, 39):
        if sheet.cell(n, 5).value == str(user):
            return n
    return 2
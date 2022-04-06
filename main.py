import logging
import time
import pprint  # импортируем pprint
import gspread
# -*- coding: utf8 -*-
########################################################################################################################
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,\
    InlineKeyboardButton
import asyncio
########################################################################################################################

########################################################################################################################
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
########################################################################################################################
import oauth2client.service_account
from redis import Redis
from rq import Queue
########################################################################################################################
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
get_data = sheet.get_all_records()  # Получаем все данные из таблицы

with open('pins.txt', 'r') as f:  # Открываем файл с ПИН кодами
    users = [i.rstrip() for i in f]
users = open('pins.txt', 'r').read()  # Open pin file(a txt document with pin list)

user_data = {'477426832':'1111'} # User list id:pin


@dp.message_handler(Command("start"), state=None)
async def start(message):
    await bot.send_message(message.chat.id, text="Введи PIN")

@dp.message_handler(Command("print"), state=None)
async def print(message):
    await bot.send_message(message.chat.id, text=user_data[message.chat.id])

@dp.message_handler(content_types=["text"])
async def auth(message):
    joinedFile = open("user.txt", 'r')
    joinedUsers = set()
    if message.text in users:  # Если ПИН правильный, то переходим к кнопкам
        if message.chat.id not in user_data:  # Checking a list
            user_data[message.chat.id] = message.text
            joinedFile = open("user.txt", "a")
            joinedFile.write(str(message.chat.id) + '/' + str(message.text) + "\n")
            joinedUsers.add(message.chat.id)

        await bot.delete_message(message.chat.id, message.message_id)
    else:  # Если не правильный просим еще раз
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(message.from_user.id, 'Неправильно, попробуй еще раз!')






if __name__ == '__main__':
    print('Бот запущен!')
executor.start_polling(dp)
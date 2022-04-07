import logging
import time
import pprint  # импортируем pprint
import gspread
# -*- coding: utf8 -*-
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
import oauth2client.service_account
from redis import Redis
from rq import Queue
import config  # ИМПОРТИРУЕМ ДАННЫЕ ИЗ ФАЙЛОВ config.py
import keyboard  # ИМПОРТИРУЕМ ДАННЫЕ ИЗ ФАЙЛОВ keyboard.py
import gsheets

storage = MemoryStorage()  # FOR FSM
bot = Bot(token=config.botkey, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO, )
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
user_data = {'477426832': '1111'}  # User list id:pin


@dp.message_handler(Command("start"), state=None)
async def start(message):
    await bot.send_message(message.chat.id, text="Введи PIN")


@dp.message_handler(Command("print"), state=None)
async def print_pin(message):
    await bot.send_message(message.chat.id, text=user_data[message.chat.id])


@dp.message_handler(content_types=["text"])
async def auth(message):
    if message.text in users:  # Если ПИН правильный, то переходим к кнопкам
        if message.chat.id not in user_data:  # Checking a list
            user_data[message.chat.id] = message.text
            joinedFile = open("user.txt", "a")
            joinedFile.write(str(message.chat.id) + '/' + str(message.text) + "\n")
        await bot.delete_message(message.chat.id, message.message_id)
        await start_menu(message)
    else:  # Если не правильный просим еще раз
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(message.from_user.id, 'Неправильно, попробуй еще раз!')


async def start_menu(message):
    await bot.send_message(message.chat.id, f"Привет, *{message.from_user.first_name},* чем я могу вам помочь",
                           reply_markup=keyboard.menu, parse_mode='Markdown')


@dp.callback_query_handler()
async def callback_worker(call: types.CallbackQuery):
    if call.data == "add":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Когда?",
                                    reply_markup=keyboard.date_add, parse_mode='Markdown')
    if call.data == "del":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Когда?",
                                    reply_markup=keyboard.date_del, parse_mode='Markdown')
    if call.data == "today_add":
        today_add = InlineKeyboardMarkup()
        i = 1
        for x in range(9, 24, 2):
            i += 1
            if sheet.cell(i, 2).value not in users:
                today_add.add(types.InlineKeyboardButton(text=str(x) + ":00", callback_data=str(x) + 'A'))
        today_add.add(types.InlineKeyboardButton(text='Меню', callback_data='menu'))
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Доступное время:",
                                    reply_markup=today_add, parse_mode='Markdown')
    if call.data == "tomorrow_add":
        tomorrow_add = InlineKeyboardMarkup()
        i = 1
        for x in range(9, 24, 2):
            i += 1
            if sheet.cell(i, 3).value not in users:
                tomorrow_add.add(types.InlineKeyboardButton(text=str(x) + ":00", callback_data=str(x) + 'A'))
        tomorrow_add.add(types.InlineKeyboardButton(text='Меню', callback_data='menu'))
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Доступное время:",
                                    reply_markup=tomorrow_add, parse_mode='Markdown')
    if call.data == "today_del":
        today_del = InlineKeyboardMarkup()
        i = 1
        for x in range(9, 24, 2):
            i += 1
            if sheet.cell(i, 3).value == str(user_data[call.message.chat.id]):
                today_del.add(types.InlineKeyboardButton(text=str(x) + ":00", callback_data=str(x) + 'DT'))
        today_del.add(types.InlineKeyboardButton(text='Меню', callback_data='menu'))
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Какое время вы хотите удалить?",
                                    reply_markup=today_del, parse_mode='Markdown')
    if call.data == "tomorrow_del":
        tomorrow_del = InlineKeyboardMarkup()
        i = 1
        for x in range(9, 24, 2):
            i += 1
            if sheet.cell(i, 3).value == str(user_data[call.message.chat.id]):
                tomorrow_del.add(types.InlineKeyboardButton(text=str(x) + ":00", callback_data=str(x) + 'DT'))
        tomorrow_del.add(types.InlineKeyboardButton(text='Меню', callback_data='menu'))
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Какое время вы хотите удалить?",
                                    reply_markup=tomorrow_del, parse_mode='Markdown')
    if call.data == "menu":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f"Привет, *{call.from_user.first_name},* чем я могу вам помочь",
                                    reply_markup=keyboard.menu, parse_mode="Markdown")


if __name__ == '__main__':
    print('Бот запущен!')
executor.start_polling(dp)

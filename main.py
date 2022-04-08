# -*- coding: utf8 -*-
import logging
import time
import pprint  # импортируем pprint
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from redis import Redis
from rq import Queue
import config
import keyboard
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
user_data = {}  # User list id:pin


def coords(user):  # Поиск пользователя в таблице
    for n in range(2, 39):
        if sheet.cell(n, 5).value == str(user):
            return n
    return 2


@dp.message_handler(Command("start"), state=None)
async def start(message):
    await bot.send_message(message.chat.id, text="Введи PIN")


@dp.message_handler(Command("print"), state=None)
async def print_pin(message):
    await bot.send_message(message.chat.id, text=user_data[message.chat.id])


@dp.message_handler(content_types=["text"])
async def auth(message):
    if message.text in users:  # Если ПИН правильный, то переходим к кнопкам
        if message.chat.id not in user_data:
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
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Доступное "
                                                                                                           "время:",
                                    reply_markup=today_add, parse_mode='Markdown')
    if call.data == "tomorrow_add":
        tomorrow_add = InlineKeyboardMarkup()
        i = 1
        for x in range(9, 24, 2):
            i += 1
            if sheet.cell(i, 3).value not in users:
                tomorrow_add.add(types.InlineKeyboardButton(text=str(x) + ":00", callback_data=str(x) + 'AT'))
        tomorrow_add.add(types.InlineKeyboardButton(text='Меню', callback_data='menu'))
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Доступное "
                                                                                                           "время:",
                                    reply_markup=tomorrow_add, parse_mode='Markdown')
    if call.data == "today_del":
        today_del = InlineKeyboardMarkup()
        i = 1
        for x in range(9, 24, 2):
            i += 1
            if sheet.cell(i, 2).value == str(user_data[call.message.chat.id]):
                today_del.add(types.InlineKeyboardButton(text=str(x) + ":00", callback_data=str(x) + 'D'))
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
    if call.data == "myadds":
        my_adds = InlineKeyboardMarkup()
        my_adds.add(InlineKeyboardButton(text='Сегодня:', callback_data='N'))
        i = 1
        for x in range(9, 24, 2):
            i += 1
            if sheet.cell(i, 2).value == str(user_data[call.message.chat.id]):
                my_adds.add(InlineKeyboardButton(text=str(x) + ':00', callback_data=str(x)))
        my_adds.add(InlineKeyboardButton(text='Завтра:', callback_data='N'))
        i = 1
        for x in range(9, 24, 2):
            i += 1
            if sheet.cell(i, 3).value == str(user_data[call.message.chat.id]):
                my_adds.add(InlineKeyboardButton(text=str(x) + ':00', callback_data=str(x)))
        my_adds.add(types.InlineKeyboardButton(text='Меню', callback_data='menu'))
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ваши "
                                                                                                           "записи:",
                                    reply_markup=my_adds)
    if call.data == "9A":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 6).value) < 1:
            sheet.update_cell(2, 2, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "11A":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 6).value) < 1:
            sheet.update_cell(3, 2, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "13A":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 6).value) < 1:
            sheet.update_cell(4, 2, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "15A":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 6).value) < 1:
            sheet.update_cell(5, 2, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "17A":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 6).value) < 1:
            sheet.update_cell(6, 2, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "19A":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 6).value) < 1:
            sheet.update_cell(7, 2, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "21A":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 6).value) < 1:
            sheet.update_cell(8, 2, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "23A":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 6).value) < 1:
            sheet.update_cell(9, 2, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "9AT":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 7).value) < 1:
            sheet.update_cell(2, 3, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "11AT":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 7).value) < 1:
            sheet.update_cell(3, 3, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "13AT":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 7).value) < 1:
            sheet.update_cell(4, 3, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "15AT":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 7).value) < 1:
            sheet.update_cell(5, 3, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "17AT":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 7).value) < 1:
            sheet.update_cell(6, 3, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "19AT":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 7).value) < 1:
            sheet.update_cell(7, 3, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "21AT":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 7).value) < 1:
            sheet.update_cell(8, 3, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")

    if call.data == "23AT":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        if int(sheet.cell(coords(str(user_data[call.message.chat.id])), 7).value) < 1:
            sheet.update_cell(9, 3, user_data[call.message.chat.id])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Готово!")
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Вы превысили лимит записей!")
        time.sleep(5)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введи PIN")
    if call.data == "9D":  # Delete the user at 9:00 today
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(2, 2, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
    if call.data == '11D':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(3, 2, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == "13D":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(4, 2, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == '15D':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(5, 2, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == "17D":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(6, 2, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == '19D':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(7, 2, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == "21D":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(8, 2, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == '23D':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(9, 2, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == "9DT":  # Delete the user at 9:00 tomorrow
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(2, 3, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == '11DT':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(3, 3, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == "13DT":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(4, 3, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == '15DT':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(5, 3, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == "17DT":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(6, 3, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == '19DT':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(7, 3, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == "21DT":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(8, 3, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        
    if call.data == '23DT':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Секундочку...")
        sheet.update_cell(9, 3, '')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Готово!")
        time.sleep(5)
        

if __name__ == '__main__':
    print('Бот запущен!')
executor.start_polling(dp)

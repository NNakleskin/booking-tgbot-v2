from aiogram import Bot, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
import gsheets

sheet = gsheets.sheet
with open('pins.txt', 'r') as f:  # Открываем файл с ПИН кодами
    users = [i.rstrip() for i in f]


menu = InlineKeyboardMarkup()
menu.add(InlineKeyboardButton(f'Забронировать корт', callback_data='add'))
menu.add(InlineKeyboardButton(f'Отменить запись', callback_data='delete'))
menu.add(InlineKeyboardButton(f'Мои записи', callback_data='myadds'))


date_add = InlineKeyboardMarkup()
date_add.add(InlineKeyboardButton(text='Сегодня', callback_data='today_add'))
date_add.add(InlineKeyboardButton(text='Завтра', callback_data='tomorrow_add'))
date_add.add(InlineKeyboardButton(text='Меню', callback_data='menu'))


date_del = InlineKeyboardMarkup()
date_del.add(InlineKeyboardButton(text='Сегодня', callback_data='today_del'))
date_del.add(InlineKeyboardButton(text='Завтра', callback_data='tomorrow_del'))
date_del.add(InlineKeyboardButton(text='Меню', callback_data='menu'))


today_add = InlineKeyboardMarkup()
i = 1
for x in range(9, 24, 2):
    i += 1
    if sheet.cell(i, 2).value not in users:
        today_add.add(types.InlineKeyboardButton(text=str(x) + ":00", callback_data=str(x) + 'A'))
today_add.add(types.InlineKeyboardButton(text='Меню', callback_data='menu'))
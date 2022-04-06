from aiogram import Bot, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
import gsheets
sheet = gsheets.sheet


menu = InlineKeyboardMarkup()
menu.add(InlineKeyboardButton(f'Забронировать корт', callback_data='add'))
menu.add(InlineKeyboardButton(f'Отменить запись', callback_data='delete'))
menu.add(InlineKeyboardButton(f'Мои записи', callback_data='myadds'))

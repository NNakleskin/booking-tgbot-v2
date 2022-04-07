import pprint  # импортируем pprint
import gspread
from oauth2client.service_account import ServiceAccountCredentials  # Ипортируем ServiceAccountCredentials(GoogleSheets)
from redis import Redis
from rq import Queue


link = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']  # Задаем ссылку на Гугл таблици
# Формируем данные для входа из нашего json файла
sheets = ServiceAccountCredentials.from_json_keyfile_name('JSONFILE_NAME.json', link)
client = gspread.authorize(sheets)  # Запускаем клиент для связи с таблицами
sheet = client.open('SHEET').sheet1  # Открываем нужную на таблицу и лист
printf = pprint.PrettyPrinter()  # Описываем прити принт
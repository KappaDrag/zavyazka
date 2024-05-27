import telebot
from datetime import datetime
import time
import os
import random
from telebot import types
import pytz
import schedule

API_TOKEN = '6887471012:AAEP0pWVXdlA-oQue8_6r3r-ZFqpo8ouYXs'
bot = telebot.TeleBot(API_TOKEN)

CHAT_ID_FILE = 'chat_id.txt'
file_path = 'fraze.txt'

moscow_tz = pytz.timezone('Europe/Moscow')

# Получаем текущее время в часовом поясе Москвы


# Функция для сохранения CHAT_ID в файл
def save_chat_id(chat_id):
    with open(CHAT_ID_FILE, 'w') as file:
        file.write(str(chat_id))

# Функция для загрузки CHAT_ID из файла
def load_chat_id():
    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, 'r') as file:
            return file.read().strip()
    return None

# Функция для удаления файла с CHAT_ID
def delete_chat_id():
    if os.path.exists(CHAT_ID_FILE):
        os.remove(CHAT_ID_FILE)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    save_chat_id(chat_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Получить сообщение'))
    bot.send_message(chat_id, "Здарова, Чушка! Я буду отправлять тебе ежедневные сообщения. Нажмите кнопку, чтобы получить сообщение.", reply_markup=markup)
    print(f"Сохранён CHAT_ID: {chat_id}")

# Обработчик команды /stop
@bot.message_handler(commands=['stop'])
def stop_bot(message):
    chat_id = message.chat.id
    delete_chat_id()
    bot.send_message(chat_id, "Бот остановлен. Чтобы снова его запустить, используйте команду /start.")
    print(f"Бот остановлен для CHAT_ID: {chat_id}")
    global running
    running = False

# Функция для вычисления количества дней до 29 апреля
def days_until_april_29():
    today = datetime.now().date()
    target_date = datetime(today.year, 4, 29).date()
    if today > target_date:
        target_date = datetime(today.year + 1, 4, 29).date()
    return (target_date - today).days

# Функция для получения случайной строки из файла
def get_random_line_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return random.choice(lines).strip() if lines else "Нет строк в файле"

# Функция для отправки сообщения
def send_daily_message(chat_id):
    random_line = get_random_line_from_file('fraze.txt')
    message = f"{random_line}\n{days_until_april_29()} дней"
    bot.send_message(chat_id, message.encode('utf-8').decode(), parse_mode='HTML')
    print(f"Отправлено сообщение: {message}")

# Обработчик кнопки "Получить сообщение"
@bot.message_handler(func=lambda message: message.text == 'Получить сообщение')
def handle_get_message(message):
    chat_id = message.chat.id
    send_daily_message(chat_id)

def main():
    global running
    running = True
    while running:
        schedule.run_pending()
        # Спим 30 секунд перед следующим проверочным циклом
        time.sleep(1)

if __name__ == '__main__':
    print("Бот запущен")
    bot.polling(none_stop=True)
    try:
        chat_id = load_chat_id()
        schedule.every().day.at("09:00").do(send_daily_message(chat_id))
        main()
    except KeyboardInterrupt:
        print("Бот остановлен вручную")
        running = False
# Импорт библиотек
from aiogram import Bot, Dispatcher # Для создания бота и диспетчера

# Токен API тг-бота
API_TOKEN = 'YOUR_BOT_TOKEN'

# Создаем объект бота с использованием токена
bot = Bot(token=API_TOKEN)

# Создаем диспетчер для управления обновлениями от бота
dp = Dispatcher()

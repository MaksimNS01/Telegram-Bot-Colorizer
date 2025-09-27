# Импорт библиотек
import torch # Для работы с тензорами и построения моделей глубокого обучения
import asyncio # Для асинхронного программирования
import logging # Для ведения логов
from deoldify import device # Для работы с устройствами (CPU/GPU)
from aiogram.filters.command import Command # Для обработки команд бота
from aiogram import F as FILETYPE # Для работы с типами файлов (as FILETYPE т.к. в tensorflow.nn исп-ся F и возникает конфликт)

# Импорт модулей
from app.bot_init import bot, dp # Экземпляры бота и диспетчера из модуля bot_init.py
from app.handlers import cmd_start, handle_text, handle_image # Обработчики команд и сообщений из модуля handlers.py


# Выбор устройства для выполнения вычислений: CPU или одна из доступных GPU (например, GPU0...GPU7):
# В данном случае используется CPU
device = torch.device('cpu')

# Включаем логирование и устанавливаем уровень логов на INFO
# Это позволит выводить сообщения уровня INFO и выше (например, WARNING, ERROR)
logging.basicConfig(level=logging.INFO)

# Регистрируем обработчики (хендлеры) для различных типов сообщений:
# Регистрация обработчика команды /start
dp.message.register(cmd_start, Command("start"))

# Регистрация обработчика для изображений
dp.message.register(handle_image, FILETYPE.photo)

# Регистрация обработчика для текстовых сообщений
dp.message.register(handle_text)


# Асинхронная функция для запуска процесса поллинга новых апдейтов (сообщений) от пользователей
async def main():
    # Запуск поллинга
    await dp.start_polling(bot)

# Проверка, является ли данный скрипт основным модулем, который запущен
if __name__ == "__main__":
    try:
        # Запуск асинхронной функции main() с использованием asyncio.run()
        asyncio.run(main())
    except KeyboardInterrupt:
        # Обработка прерывания программы с клавиатуры (например, Ctrl+C)
        print('Бот отключён')
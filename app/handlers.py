# Импорт библиотек
import os # Стандартный модуль os для работы с операционной системой (например, для работы с файлами и директориями)
import logging # Для ведения логов
from aiogram import types # Для работы с типами данных, используемыми в aiogram
from aiogram.types import FSInputFile # Для работы с файлами в aiogram

import time
import psutil
from collections import deque

# Экземпляр бота из модуля bot_init.py
from .bot_init import bot 

# Импорт функций из модуля functions.py
from .functions import (
    check_and_delete_file,    # Функция для проверки и удаления файла
    colorize_image,           # Функция для раскрашивания изображения
    # add_watermark,            # Функция для добавления водяного знака на изображение
    add_frame_to_image,
    is_safe_content,          # Функция для проверки безопасности контента
    classify_and_check_image, # Функция для классификации и проверки изображения
    convert_to_grayscale      # Функция для преобразования изображения в ЧБ
)


# Очередь для хранения результатов последних 1000 запросов
last_10_processing_times = deque(maxlen=1000)
last_10_memory_usages = deque(maxlen=1000)


# Настраиваемые параметры
IS_WATERMARK = True # Флаг, указывающий, нужно ли добавлять водяной знак на изображения (True/False)
# LOGO_SCALE = 0.5
# LOGO_MARGIN = 25
CHECK_CONTENT = False # Флаг, указывающий, нужно ли проверять контент изображений на безопасность (True/False)
CHECK_SCORE = 0.5 # Пороговое значение для проверки безопасности контента NSFW-детектором
FILTER_VOLUME = 5 # Объем фильтрации нежелательного контента (число объектов на изображении, которые нужно проверить)

# Список меток, которые нужно блокировать (например, для фильтрации контента)
blocked_labels = [
    # 'military_uniform',
    'warplane',
    'butcher_shop',
    'maraca',
    'street_sign',
    'sign',
    'soccer_ball',
    'volleyball',
    'umbrella',
    'solar_dish',
    'maze',
    'necklace',
    'bolo_tie',
    'bearskin',
    'prison',
    'flagpole',
    'bow_tie',
    'Windsor_tie',
    'tench',
    # 'ice_lolly',
    'kimono'
]


# Хэндлер для команды /start
async def cmd_start(message: types.Message):
    # Отправляем ответное сообщение пользователю
    await message.answer("Привет! Отправь мне черно-белое изображение, и я сделаю его цветным!")


# Хэндлер для обработки изображений
async def handle_image(message: types.Message):
    # Устанавливаем статус бота "Отправляет фото..."
    await message.bot.send_chat_action(message.chat.id, 'upload_photo')
    try:
        process = psutil.Process()
    
        # Измерение начальных значений ресурсов
        start_memory = process.memory_info().rss
        start_time = time.time()
        
        # Получаем file_id последнего фото из сообщения
        file_id = message.photo[-1].file_id
        
        # Получаем информацию о файле по его file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path

        # Устанавливаем путь для сохранения входного изображения
        input_path = os.path.join('temp_images', f"{file_id}.jpg")

        # Проверяем и удаляем файл, если он уже существует
        check_and_delete_file(input_path)
        
        # Скачиваем файл по file_path и сохраняем его в input_path
        await bot.download_file(file_path, input_path)

        # Проверяем, безопасен ли контент изображения, и классифицируем его
        if is_safe_content(input_path, CHECK_SCORE) and classify_and_check_image(input_path, blocked_labels, FILTER_VOLUME) or not(CHECK_CONTENT):
            # Устанавливаем директорию и имя файла для выходного изображения
            output_dir = os.path.dirname(input_path)
            input_filename = os.path.basename(input_path)
            output_filename = 'clr_' + input_filename
            output_path = os.path.join(output_dir, output_filename)

            # Проверяем и удаляем файл, если он уже существует
            check_and_delete_file(output_path)

            convert_to_grayscale(input_path, input_path)

            # Раскрашиваем изображение
            colorize_image(input_path, output_path)

            # Если установлен флаг IS_WATERMARK, добавляем водяной знак
            if IS_WATERMARK:
                output_dir_wm = os.path.dirname(output_path)
                input_filename_wm = os.path.basename(output_path)
                output_filename_wm = 'wm_' + input_filename_wm
                output_path_wm = os.path.join(output_dir_wm, output_filename_wm)

                # Добавляем водяной знак на изображение
                # add_watermark(output_path, 'watermarks/logo_victory.png', 'watermarks/logo_rtr .png', output_path_wm, LOGO_SCALE, LOGO_MARGIN)
                add_frame_to_image(output_path, output_path_wm)
                
                # Отправляем пользователю изображение с водяным знаком
                await message.answer_photo(photo=FSInputFile(output_path_wm))

                # Удаляем файл с водяным знаком для очистки памяти
                check_and_delete_file(output_path_wm)

            else:
                # Отправляем пользователю раскрашенное изображение без водяного знака
                await message.answer_photo(photo=FSInputFile(output_path))

            # Удаляем входное и выходное изображения для очистки памяти
            check_and_delete_file(input_path)
            check_and_delete_file(output_path)

            # Измерение конечных значений ресурсов
            end_time = time.time()
            end_memory = process.memory_info().rss
            
            # Вычисление затрат времени и ресурсов
            processing_time = end_time - start_time
            memory_usage = end_memory - start_memory

            print(f"Время обработки одной картинки: {processing_time} секунд")
            print(f"Использование памяти: {memory_usage / (1024 * 1024)} MB")

            # Обновление очередей
            last_10_processing_times.append(processing_time)
            last_10_memory_usages.append(memory_usage)
            
            # Вычисление средних значений
            avg_processing_time = sum(last_10_processing_times) / len(last_10_processing_times)
            avg_memory_usage = sum(last_10_memory_usages) / len(last_10_memory_usages)
            print(f"Среднее время обработки последних 10 картинок: {avg_processing_time} секунд")
            print(f"Среднее использование памяти последних 10 картинок: {avg_memory_usage / (1024 * 1024)} MB")
        else:
            # Отправляем сообщение, если изображение содержит неприличный контент
            await message.answer("Ой, что-то пошло не так.")
            # Удаляем входное и выходное изображения для очистки памяти
            check_and_delete_file(input_path)
            # check_and_delete_file(output_path)

    except Exception as e:
        # Логируем ошибку и отправляем сообщение об ошибке пользователю
        logging.error(f"Error processing image: {e}")
        await message.answer("Произошла ошибка при обработке изображения.")
 
# Хэндлер для текстовых сообщений
async def handle_text(message: types.Message):
    # Отправляем ответное сообщение пользователю
    await message.answer("Пожалуйста, отправьте черно-белое изображение.")
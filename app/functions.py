# Импорт библиотек
import os # Стандартный модуль os для работы с операционной системой (например, для работы с файлами и директориями)
import logging # Для ведения логов
import tensorflow as tf # Для машинного и глубокого обучения
import numpy as np # Для работы с массивами и числовыми операциями

from PIL import Image # Для работы с изображениями
from deoldify.visualize import get_image_colorizer # Для цветокоррекции изображений с помощью DeOldify
from nsfw_detector.model import Model # Для определения нежелательного (NSFW) контента на изображениях
from tensorflow.keras.preprocessing import image # Для работы с изображениями, включая загрузку и предварительную обработку
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions # Ддля работы с массивами и числовыми операциями


# Загрузка предобученной модели MobileNetV2 с весами, обученными на наборе данных ImageNet
model = tf.keras.applications.MobileNetV2(weights='imagenet')

# Инициализация модели DeOldify для цветокоррекции изображений, с использованием художественного режима
colorizer = get_image_colorizer(artistic=True)

# Инициализация модели NSFW Detector для определения нежелательного контента
net = Model()


# Функция для раскрашивания изображения
def colorize_image(input_path, output_path):
    # Раскрашивание изображения с использованием модели DeOldify
    result_path = colorizer.plot_transformed_image(
        path=input_path,  # Путь к входному изображению
        render_factor=35,  # Параметр, влияющий на качество раскрашивания (чем выше значение, тем выше качество)
        display_render_factor=False,  # Не отображать фактор рендеринга
        figsize=(8, 8)  # Размер фигуры для отображения
    )  
    # Сохранение результата
    if result_path:
        os.rename(result_path, output_path)  # Переименование и перемещение результата в указанный путь
        print(f"Результат сохранен в {output_path}")  # Сообщение о сохранении
    else:
        print("Ошибка при раскрашивании изображения.")  # Сообщение об ошибке

# Функция добавления рамки
def add_frame_to_image(image_path, output_path):
    # Открываем изображение
    image = Image.open(image_path)
    # Получаем текущие размеры изображения
    width, height = image.size

    # Выбор рамки
    if (height - width) > 100:
        frame_path = './watermarks/PhotoFrame_v.png'
        target_width = 600
        target_height = 900
        x_offset = 60
        y_offset = 70
        angle = -5.3
    elif (width - height) > 100:
        frame_path = './watermarks/PhotoFrame_h.png'
        target_width = 900
        target_height = 600
        x_offset = 107
        y_offset = 18
        angle = -4.1
    else:
        frame_path = './watermarks/PhotoFrame_s.png'
        target_width = 650
        target_height = 610
        x_offset = 103
        y_offset = 50
        angle = 3.0
    
    # Открываем рамку
    frame = Image.open(frame_path)

    # Изменение размера изображения до размеров рамки (с учетом пустого места)
    # Здесь предполагаем, что пустое место в рамке — это центр рамки
    frame_width, frame_height = frame.size


    # Изменяем размер изображения по ширине до 900 пикселей
    if width != target_width:
        new_width = target_width
        new_height = int((target_width / width) * height)
        image = image.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)
    
    # Обновляем размеры изображения после изменения размера по ширине
    width, height = image.size
    
    # Если высота изображения меньше 900 пикселей, изменяем размер по высоте до 900 пикселей
    if height < target_height:
        new_height = target_height
        new_width = int((target_height / height) * width)
        image = image.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)
    
    # Обновляем размеры изображения после изменения размера по высоте
    width, height = image.size
    
    # Если ширина изображения больше 600 пикселей, обрезаем лишнюю ширину до 600 пикселей
    if width > target_width:
        left = (width - target_width) // 2
        right = left + target_width
        image = image.crop((left, 0, right, height))

    # image = image.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)

    # Поворачиваем изображение
    image = image.rotate(angle, expand=True)

    # Вычисляем координаты для вставки изображения в рамку, чтобы оно было по центру
    x = (frame_width - image.width) // 2 + x_offset
    y = (frame_height - image.height) // 2 + y_offset

    # Создаем пустое изображение с альфа-каналом для наложения
    combined = Image.new('RGBA', frame.size)

    # Вставляем изображение в центр
    combined.paste(image, (x, y), image.convert('RGBA'))

    # Накладываем рамку поверх исходного изображения
    combined = Image.alpha_composite(combined, frame.convert('RGBA'))

    # Конвертируем изображение в режим RGB перед сохранением в формате JPEG
    combined = combined.convert('RGB')

    # Сохраняем результат
    combined.save(output_path, format='JPEG')

# Функция для добавления логотипов
# def add_watermark(image_path, logo1_path, logo2_path, output_path, LOGO_SCALE, LOGO_MARGIN):
#     # Открываем изображение и логотипы
#     image = Image.open(image_path)
#     logo1 = Image.open(logo1_path)
#     logo2 = Image.open(logo2_path)

#     # Изменяем размер изображения
#     width, height = image.size
#     if width > 1300:
#         new_width = 1300
#     else:
#         new_width = 800
#     new_height = int(new_width * height / width)
#     image = image.resize((new_width, new_height))

#     # Размеры логотипов
#     logo1_width, logo1_height = logo1.size
#     logo2_width, logo2_height = logo2.size

#     # Уменьшаем логотипы
#     logo1 = logo1.resize((int(logo1_width * LOGO_SCALE), int(logo1_height * LOGO_SCALE)))
#     logo2 = logo2.resize((int(logo2_width * LOGO_SCALE), int(logo2_height * LOGO_SCALE)))

#     # Обновляем размеры логотипов
#     logo1_width, logo1_height = logo1.size
#     logo2_width, logo2_height = logo2.size

#     # Позиции логотипов
#     margin_top = LOGO_MARGIN
#     margin_left = LOGO_MARGIN
#     margin_right = new_width - logo2_width - LOGO_MARGIN

#     # Вставляем логотипы
#     image.paste(logo1, (margin_left, margin_top), logo1)
#     image.paste(logo2, (margin_right, margin_top), logo2)

#     # Сохраняем результат
#     image.save(output_path)

# Функция проверки существования файлов и их удаления 
def check_and_delete_file(file_path):
    if os.path.exists(file_path):  # Проверяем, существует ли файл по указанному пути
        os.remove(file_path)  # Удаляем файл, если он существует
        print(f"Файл {file_path} был удален.")  # Выводим сообщение о том, что файл был удален
    else:
        print(f"Файл {file_path} не существует.")  # Выводим сообщение, что файл не найден

# Функция проверки безопасности контента
def is_safe_content(image_path, CHECK_SCORE):
    """
    Проверяет изображение на неприемлемый контент.
    Возвращает True, если контент безопасный, и False, если неприемлемый.

    :param image_path: Путь к изображению.
    :param CHECK_SCORE: Пороговое значение для оценки изображения.
    :return: True, если контент безопасный, и False, если неприемлемый.
    """
    # Делаем предсказание на основе изображения
    output = net.predict(image_path)

    # Логируем путь к изображению и результаты предсказания
    logging.info(f"Image Path: {image_path} | Results: {output}")

    # Получаем результат предсказания для данного изображения
    result = output[image_path]
    label = result['Label']  # Метка, указывающая на тип контента
    score = result['Score']  # Оценка уверенности в предсказании

    # Проверяем, является ли контент неприемлемым (NSFW) или оценка превышает пороговое значение
    if label == 'NSFW' or score > CHECK_SCORE:
        return False  # Контент неприемлемый
    else:
        return True  # Контент безопасный

# Функция классификации изображения и проверки его на наличие заблокированных меток
def classify_and_check_image(img_path, blocked_labels, FILTER_VOLUME):
    """
    Классифицирует изображение и проверяет его на наличие заблокированных меток.
    :param img_path: Путь к изображению.
    :param blocked_labels: Список меток, которые считаются заблокированными.
    :param FILTER_VOLUME: Количество топовых предсказаний, которые нужно учитывать.
    :return: True, если изображение безопасное, и False, если содержит заблокированные метки.
    """
    # Загрузка и предобработка изображения
    img = image.load_img(img_path, target_size=(224, 224))  # Загружаем изображение и изменяем его размер
    img_array = image.img_to_array(img)  # Преобразуем изображение в массив
    img_array = np.expand_dims(img_array, axis=0)  # Добавляем дополнительное измерение для пакета
    img_array = preprocess_input(img_array)  # Предобрабатываем изображение для модели

    # Классификация изображения
    predictions = model.predict(img_array)  # Делаем предсказание модели
    decoded_predictions = decode_predictions(predictions, top=FILTER_VOLUME)[0]  # Декодируем предсказания

    # Проходим по декодированным предсказаниям
    for i, (imagenet_id, label, score) in enumerate(decoded_predictions):
        print(f"{i+1}: {label} ({score:.2f})")  # Выводим метку и оценку предсказания
        if label in blocked_labels:  # Проверяем, есть ли метка в списке заблокированных
            return False  # Возвращаем False, если метка заблокирована
    return True  # Возвращаем True, если ни одна из меток не заблокирована

# Функция преобразования изображения в чб
def convert_to_grayscale(img_path, output_path):
    """
    Конвертирует изображение в черно-белое.
    :param img_path: Путь к исходному изображению.
    :param output_path: Путь для сохранения черно-белого изображения.
    """
    img = Image.open(img_path).convert('L')  # Открываем изображение и конвертируем его в черно-белое
    img.save(output_path)  # Сохраняем черно-белое изображение
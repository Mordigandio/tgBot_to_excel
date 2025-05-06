""" Обработчик сообщений для Telegram-бота.

Модуль содержит функции для обработки команды /start, документов и фотографий.
Конвертация происходит в .xlsx и отправки результата пользователю.

"""

import os
import tempfile
import logging
import re
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from app.services.converter import convert_file

router = Router()

@router.message(CommandStart())
async def first_message(message: Message) -> None:
    """Обрабатывает команду /start и отправляет приветственное сообщение

    Args:
        message (Message): Входящее сообщение от пользователя
        
    Returns:
        None
    """

    user_name = message.from_user.first_name
    await message.answer(f"Привет {user_name}! Чтобы начать работу, отправь файл из разрешенных "
                         "форматов: .jpg, .docx, .xls или .bmp и я переведу для тебя файл в " 
                         "excel формат")
    
@router.message(F.document)
async def handle_document(message: Message) -> None:
    """Обрабатывает входящие документы и конвертирует их в формат .xlsx

    Args:
        message (Message): Входящее сообщение с документом
        
    Returns:
        None
    """
    
    document = message.document
    file_name = document.file_name
    file_extension = os.path.splitext(file_name)[1].lower()
    
    # Лог получения файла и расширения
    logging.info(f"Получен файл: {file_name}, расширение {file_extension}")
    
    # Проверка на формат файла
    if file_extension not in ['.jpg', '.jpeg', '.docx', '.xls', '.bmp']:
        await message.reply("Формат файла не поддерживается."
                            "\n Поддерживаемые форматы .jpg, .docx, .xls, .bmp")
        return
    
    # Скачиваем файл во временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_input:
        await message.bot.download(document, destination=temp_input.name)
        input_path = temp_input.name
        logging.info(f"Файл скачан в: {input_path}")
        
        # Создаем имя выходного файла на основе исходного
        base_name = os.path.splitext(file_name)[0]
        output_filename = f"{base_name}.xlsx"
        
        # Заменяем недопустимые символы в имени файла
        output_filename = re.sub(r'[^\w\s.-]', '_', output_filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_output:
        output_path = temp_output.name
        
        # Помещаем в файл с исходным именем
        final_output_path = os.path.join(tempfile.gettempdir(), output_filename)
    try:
      convert_file(input_path, output_path, file_extension)
      
      # Перемещаем файл для сохранения имени
      os.rename(output_path, final_output_path)
      
      # Отправляем конвертированный файл с исходным именем
      await message.reply_document(FSInputFile(final_output_path), caption="Вот твой файл")
    except Exception as e:
        logging.error(f"Возникла ошибка при конвертации: {e}")
        
        await message.reply("К сожалению при конвертации файла произошла ошибка, попытайся снова!")
    finally:
        
        try:
            # Удаляем временные файлы
            os.remove(input_path)
            if os.path.exists(final_output_path):
                os.remove(final_output_path)
        except Exception as e:
            logging.error(f"ошибка при удалении временных файлов: {e}")

@router.message(F.photo)
async def handle_photo(message: Message) -> None:
    """Обрабатывает входящие фотографии и конвертирует их в формат .xlsx
        Создавая базовое имя для фотографий 'photo.xlsx' 

    Args:
        message (Message): Входящее сообщение с фотографией.
        
    Returns:
        None:
    """
    # Фото максимального размера
    photo = message.photo[-1]
    
    # Предпологаем, что формат файла .jpg
    file_extension = '.jpg'
    
    base_name = "photo"
    output_filename = f"{base_name}.xlsx"
    
    # Скачиваем фото во временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_input:
        await message.bot.download(photo, destination=temp_input.name)
        input_path = temp_input.name
    
    # Создаем временный файл для результата 
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_output:
        output_path = temp_output.name
        final_output_path = os.path.join(tempfile.gettempdir(), output_filename)
    try:
        convert_file(input_path, output_path, file_extension)
        
        # Перемещаем файл для сохранения имени
        os.rename(output_path, final_output_path)
        
        # Отправляем конвертированный файл
        await message.reply_document(FSInputFile(final_output_path), caption="Вот твой файл")
    except Exception as e:
        logging.error(f"Возникла ошибка при конвертации: {e}")
      
        await message.reply("К сожалению при конвертации файла произошла ошибка, попытайся снова!")
    finally:
        
        try:
            # Удаляем временные файлы
            os.remove(input_path)
            if os.path.exists(final_output_path):
                os.remove(final_output_path)
        except Exception as e:
            logging.error(f"ошибка при удалении временных файлов: {e}")
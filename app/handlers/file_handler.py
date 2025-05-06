import os
import tempfile
import logging
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from app.services.converter import convert_file

router = Router()

@router.message(CommandStart())
async def first_message(message: Message):
    user_name = message.from_user.first_name
    await message.answer(f"Привет {user_name}! Чтобы начать работу, отправь файл из разрешенных "
                         "форматов: .jpg, .docx, .xls или .bmp и я переведу для тебя файл в " 
                         "excel формат")
    
@router.message(F.document)
async def handle_document(message: Message):
    document = message.document
    file_name = document.file_name
    file_extension = os.path.splitext(file_name)[1].lower()
    
    logging.info(f"Получен файл: {file_name}, расширение {file_extension}")
    
    if file_extension not in ['.jpg', '.jpeg', '.docx', '.xls', '.bmp']:
        await message.reply("Формат файла не поддерживается."
                            "\n Поддерживаемые форматы .jpg, .docx, .xls, .bmp")
        return
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_input:
        await message.bot.download(document, destination=temp_input.name)
        input_path = temp_input.name
        logging.info(f"Файл скачан в: {input_path}")
        
        base_name = os.path.splitext(file_name)[0]
        output_filename = f"{base_name}.xlsx"
        
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_output:
        output_path = temp_output.name
        
        final_output_path = os.path.join(tempfile.gettempdir(), output_filename)
    try:
      convert_file(input_path, output_path, file_extension)
      os.rename(output_path, final_output_path)
      await message.reply_document(FSInputFile(final_output_path), caption="Вот твой файл")
    except Exception as e:
        logging.error(f"Возникла ошибка при конвертации: {e}")
        
        await message.reply("К сожалению при конвертации файла произошла ошибка, попытайся снова!")
    finally:
        try:
            os.remove(input_path)
            if os.path.exists(final_output_path):
                os.remove(final_output_path)
        except Exception as e:
            logging.error(f"ошибка при удалении временных файлов: {e}")

@router.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1]
    file_extension = '.jpg'
    
    base_name = "photo"
    output_filename = f"{base_name}.xlsx"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_input:
        await message.bot.download(photo, destination=temp_input.name)
        input_path = temp_input.name
        
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_output:
        output_path = temp_output.name
        final_output_path = os.path.join(tempfile.gettempdir(), output_filename)
    try:
        convert_file(input_path, output_path, file_extension)
        os.rename(output_path, final_output_path)
        await message.reply_document(FSInputFile(final_output_path), caption="Вот твой файл")
        
    except Exception as e:
        logging.error(f"Возникла ошибка при конвертации: {e}")
      
        await message.reply("К сожалению при конвертации файла произошла ошибка, попытайся снова!")
    finally:
        
        try:
            os.remove(input_path)
            if os.path.exists(final_output_path):
                os.remove(final_output_path)
        except Exception as e:
            logging.error(f"ошибка при удалении временных файлов: {e}")
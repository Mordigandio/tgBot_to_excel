"""Логика конвертации файлов в формат .xlsx

    Модуль предоставляет функцию для конвертации файлов .jpg, .jpeg, .docx, .xls и .bmp
    в формат .xlsx

    Raises:
        ValueError: Проверяем на размер выходного файла
        ValueError: Проверяем не поврежден ли файл формата .docx
        ValueError: Проверяем прислали ли нужный формат
    """

import os
import docx.opc
import docx.opc.exceptions
import pandas as pd
import pytesseract
from PIL import Image
import docx
import logging

def convert_file(input_path: str, output_path: str, file_extension: str) -> None:
    """Конвертирует входной файл в формат .xlsx 
    
        Поддерживает файлы .xls (чтение через xlrd), .jpg/.jpeg/.bmp (OCR через pytesseract) и
        .docx (извлечение текста через python-docx). Результат сохраняется в указанный выходной
        файл

    Args:
        input_path (str): Путь к входному файлу
        output_path (str): Путь для сохранения выходного файла .xlsx
        file_extension (str): Расширирение входного файла, к примеру .docx
        
    Raises:
        ValueError: Обработка файла .xls 
        ValueError: Обработка изображений
        
    Returns:
        None
    """
    
    # Проверка на размер входного файла
    if os.path.getsize(input_path) == 0:
        raise ValueError("Скачанный файл пустой")
    
    if file_extension == '.xls':
        # Конвертация .xls в .xlsx
        
        try:
            df = pd.read_excel(input_path, engine='xlrd')
            df.to_excel(output_path, engine='openpyxl', index=False)
        except Exception as e:
            raise ValueError(f"Ошибка при обработке .xls файла: {str(e)}")
        
    elif file_extension in ['.jpg', 'jpeg', '.bmp']:
        # OCR для изображений
        
        try:
            img = Image.open(input_path)
            text = pytesseract.image_to_string(img)
            df = pd.DataFrame({'Text': [text]})
            df.to_excel(output_path, engine='openpyxl', index=False)
        except Exception as e:
            raise ValueError(f"Ошибка при обработке изображения: {str(e)}")
        
    elif file_extension == '.docx':
        # Извлечение текста из .docx
        
        try:
            logging.info(f"Открытие .docx файла: {input_path}")
            doc = docx.Document(input_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
            df = pd.DataFrame({'Text': [text]})
            df.to_excel(output_path, engine='openpyxl', index=False)
            logging.info(f"Успешно конвертирован в docx: {output_path}")
        except docx.opc.exceptions.PackageNotFoundError:
            raise ValueError("Файл .docx поврежден: {str(e)}")
    else:
        raise ValueError("К сожалению формат не поддерживается")
    
    
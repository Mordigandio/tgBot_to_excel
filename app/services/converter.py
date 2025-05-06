import os
import docx.opc
import docx.opc.exceptions
import pandas as pd
import pytesseract
from PIL import Image
import docx
import logging

def convert_file(input_path, output_path, file_extension):
    
    if os.path.getsize(input_path) == 0:
        raise ValueError("Скачанный файл пустой")
    
    if file_extension == '.xls':
        df = pd.read_excel(input_path, engine='xlrd')
        df.to_excel(output_path, engine='openpyxl', index=False)
    elif file_extension in ['.jpg', 'jpeg', '.bmp']:
        img = Image.open(input_path)
        text = pytesseract.image_to_string(img)
        df = pd.DataFrame({'Text': [text]})
        df.to_excel(output_path, engine='openpyxl', index=False)
    elif file_extension == '.docx':
        try:
            logging.info(f"Открытие .docx файла: {input_path}")
            doc = docx.Document(input_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
            df = pd.DataFrame({'Text': [text]})
            df.to_excel(output_path, engine='openpyxl', index=False)
            logging.info(f"Успешно конвертирован в docx: {output_path}")
        except docx.opc.exceptions.PackageNotFoundError:
            raise ValueError("Файл .docx поврежден")
    else:
        raise ValueError("К сожалению формат не поддерживается")
    
    
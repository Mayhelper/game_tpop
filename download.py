#!/usr/bin/env python3
"""
Скрипт для загрузки файла с Яндекс.Диска
"""

import requests
import json
import os
from datetime import datetime

def download_yandex_file():
    """Загружает файл с Яндекс.Диска"""
    
    # Конфигурация
    FOLDER_URL = 'https://disk.360.yandex.ru/d/ZtwhX-YtLvkxJw'
    TARGET_FILE = 'report.xlsx'
    OUTPUT_DIR = 'data'
    
    print(f"🔄 Начинаем загрузку файла {TARGET_FILE}")
    
    try:
        # 1. Получаем информацию о папке
        print("📁 Получение информации о папке...")
        api_url = f'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={FOLDER_URL}&limit=500'
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # 2. Ищем нужный файл
        print("🔍 Поиск файла...")
        file_info = None
        for item in data.get('_embedded', {}).get('items', []):
            if item.get('name') == TARGET_FILE:
                file_info = item
                break
        
        if not file_info:
            raise Exception(f'Файл {TARGET_FILE} не найден в папке')
        
        print(f"✅ Файл найден: {file_info.get('name')} ({file_info.get('size', 0)} байт)")
        
        # 3. Получаем ссылку для скачивания
        print("🔗 Получение ссылки для скачивания...")
        download_url = f'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={FOLDER_URL}&path={file_info["path"]}'
        download_response = requests.get(download_url, timeout=30)
        download_response.raise_for_status()
        download_data = download_response.json()
        direct_url = download_data.get('href')
        
        if not direct_url:
            raise Exception('Не удалось получить ссылку для скачивания')
        
        # 4. Скачиваем файл
        print("⬇️ Скачивание файла...")
        file_response = requests.get(direct_url, stream=True, timeout=60)
        file_response.raise_for_status()
        
        # Создаем директорию, если не существует
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Сохраняем файл
        output_path = os.path.join(OUTPUT_DIR, TARGET_FILE)
        total_size = int(file_response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in file_response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rПрогресс: {percent:.1f}%", end='')
        
        file_size = os.path.getsize(output_path)
        print(f"\n✅ Файл успешно скачан: {file_size} байт")
        
        # 5. Создаем метаданные
        metadata = {
            'last_updated': datetime.now().isoformat(),
            'source_url': FOLDER_URL,
            'file_name': TARGET_FILE,
            'file_size': file_size,
            'success': True,
            'message': 'Файл успешно загружен'
        }
        
        metadata_path = os.path.join(OUTPUT_DIR, 'metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Метаданные сохранены в {metadata_path}")
        print("🎉 Процесс завершен успешно!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        
        # Сохраняем информацию об ошибке
        error_metadata = {
            'last_attempt': datetime.now().isoformat(),
            'success': False,
            'error': str(e),
            'source_url': FOLDER_URL
        }
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        error_path = os.path.join(OUTPUT_DIR, 'error.json')
        with open(error_path, 'w', encoding='utf-8') as f:
            json.dump(error_metadata, f, ensure_ascii=False, indent=2)
        
        return False

if __name__ == '__main__':
    download_yandex_file()

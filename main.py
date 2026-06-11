import io
from flask import Flask, request, send_file
from PIL import Image, ImageEnhance
import pillow_heif

# Автоматически подключаем поддержку формата HEIC (с айфонов)
pillow_heif.register_heif_opener()

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_and_enhance_image():
    # Проверяем, пришёл ли файл в запросе от Make
    if 'file' not in request.files:
        return 'В запросе нет файла', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'Файл не выбран', 400

    try:
        # 1. Открываем картинку (скрипт сам поймет, HEIC это, PNG или JPG)
        img = Image.open(file.stream)
        
        # Переводим в стандартный цветовой режим RGB (избавляет от проблем с прозрачностью PNG)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # --- БЕЗОПАСНАЯ ЦВЕТОКОРРЕКЦИЯ ТАТУИРОВОК ---
        # Значение 1.0 — это оригинал. Всё, что выше (например, 1.2) — усиление эффекта.

        # Шаг А. БАЛАНС ЧЕРНОГО И КОНТРАСТ 
        # Подтягивает глубокий чёрный цвет пигмента, делает контуры тату чёткими, убирает серую блеклость.
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(1.25)  # Увеличиваем контраст на 25%

        # Шаг Б. НАСЫЩЕННОСТЬ
        # Делает цветные элементы татуировки сочнее, а тон кожи — более живым и тёплым.
        color_enhancer = ImageEnhance.Color(img)
        img = color_enhancer.enhance(1.15)  # Добавляем 15% к сочности цветов

        # Шаг В. ЯРКОСТЬ
        # Слегка высветляет тени, убирает эффект "грязного" или слишком тёмного исходного кадра.
        brightness_enhancer = ImageEnhance.Brightness(img)
        img = brightness_enhancer.enhance(1.05)  # Мягко осветляем на 5%

        # Шаг Г. МИКРО-РЕЗКОСТЬ
        # Аккуратно подчёркивает текстуру кожи и мелкие детали (штрихи, випшейдинг, тонкие линии).
        sharpness_enhancer = ImageEnhance.Sharpness(img)
        img = sharpness_enhancer.enhance(1.30)  # Повышаем чёткость деталей на 30%
        
        # 2. Сохраняем обработанный результат в буфер памяти как качественный JPEG
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=92)  # 92% — идеальный баланс веса и ультра-качества
        output.seek(0)
        
        # Отдаем готовый обработанный JPG обратно в Make
        return send_file(output, mimetype='image/jpeg')
        
    except Exception as e:
        return f"Ошибка при обработке фотографии: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

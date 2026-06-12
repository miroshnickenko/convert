import io
from flask import Flask, request, send_file
from PIL import Image, ImageEnhance
import pillow_heif
import gc  # Подключаем сборщик мусора для принудительной очистки RAM

pillow_heif.register_heif_opener()

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_and_enhance_image():
    if 'file' not in request.files:
        return 'В запросе нет файла', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'Файл не выбран', 400

    try:
        # Принимаем настройки из Make
        contrast_val = float(request.form.get('contrast', 1.25))
        color_val = float(request.form.get('color', 1.15))
        brightness_val = float(request.form.get('brightness', 1.05))
        sharpness_val = float(request.form.get('sharpness', 1.30))

        # Открываем изображение
        img = Image.open(file.stream)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # --- ОПТИМИЗАЦИЯ ПАМЯТИ ---
        # Ограничиваем максимальный размер стороны в 2000px. 
        # Это спасает сервер от падения по лимиту RAM, не ухудшая видимое качество.
        img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
        
        # Применяем фильтры последовательно, перезаписывая одну переменную (сберегает RAM)
        img = ImageEnhance.Contrast(img).enhance(contrast_val)
        img = ImageEnhance.Color(img).enhance(color_val)
        img = ImageEnhance.Brightness(img).enhance(brightness_val)
        img = ImageEnhance.Sharpness(img).enhance(sharpness_val)
        
        # Сохраняем результат
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=90)  # 90% качества снижает вес файла и нагрузку
        output.seek(0)
        
        # Жестко освобождаем ресурсы
        img.close()
        
        # Принудительно вычищаем оперативную память от остатков пикселей
        gc.collect()
        
        return send_file(output, mimetype='image/jpeg')
        
    except Exception as e:
        # В случае ошибки тоже чистим память
        gc.collect()
        return f"Ошибка при обработке фотографии: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

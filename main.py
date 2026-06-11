import io
from flask import Flask, request, send_file
from PIL import Image, ImageEnhance
import pillow_heif

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
        # Читаем настройки из запроса Make (если их нет, берутся дефолты)
        contrast_val = float(request.form.get('contrast', 1.25))
        color_val = float(request.form.get('color', 1.15))
        brightness_val = float(request.form.get('brightness', 1.05))
        sharpness_val = float(request.form.get('sharpness', 1.30))

        img = Image.open(file.stream)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Применяем динамические настройки
        # Контраст
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(contrast_val)

        # Насыщенность (Цвет)
        color_enhancer = ImageEnhance.Color(img)
        img = color_enhancer.enhance(color_val)

        # Яркость
        brightness_enhancer = ImageEnhance.Brightness(img)
        img = brightness_enhancer.enhance(brightness_val)

        # Резкость
        sharpness_enhancer = ImageEnhance.Sharpness(img)
        img = sharpness_enhancer.enhance(sharpness_val)
        
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95) # Подняли качество до 95% для идеальной картинки
        output.seek(0)
        
        return send_file(output, mimetype='image/jpeg')
        
    except Exception as e:
        return f"Ошибка при обработке фотографии: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

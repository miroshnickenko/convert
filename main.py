import io
import os
from flask import Flask, request, send_file
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_to_jpg():
    if 'file' not in request.files:
        return "Файл не найден в запросе", 400
        
    file = request.files['file']
    
    try:
        image = Image.open(file.stream)
        rgb_im = image.convert('RGB')
        
        output = io.BytesIO()
        rgb_im.save(output, format='JPEG', quality=90)
        output.seek(0)
        
        return send_file(
            output, 
            mimetype='image/jpeg', 
            as_attachment=True, 
            download_name='ready.jpg'
        )
    except Exception as e:
        return f"Ошибка конвертации: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

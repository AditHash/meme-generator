import io
from flask import Flask, request, send_file, jsonify
from dotenv import load_dotenv
from main import MemeGenerator
import mimetypes
import logging

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/generate', methods=['POST'])
def generate_meme_api():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    generator = MemeGenerator()
    meme_text = generator.generate_meme_text(prompt)
    logging.debug(f"Generated meme text: {meme_text}")
    image_data, mime_type = generator.generate_meme_image(meme_text)

    if image_data and mime_type:
        file_extension = mimetypes.guess_extension(mime_type) or '.png'
        return send_file(
            io.BytesIO(image_data),
            mimetype=mime_type,
            as_attachment=True,
            download_name=f"generated_meme{file_extension}"
        )
    else:
        logging.error(f"Failed to generate image. image_data: {image_data}, mime_type: {mime_type}")
        return jsonify({"error": "Failed to generate image"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)

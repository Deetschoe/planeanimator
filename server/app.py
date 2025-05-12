from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import base64
import os
from datetime import datetime

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate_image():
    try:
        # Use form for file + text uploads
        prompt = request.form.get("prompt")
        size = request.form.get("size", "1024x1024")
        quality = request.form.get("quality", "high")
        background = request.form.get("background", "transparent")
        output_format = request.form.get("output_format", "png")
        save_folder = request.form.get("save_folder")
        ref_image = request.files.get("ref_image")

        if not prompt:
            return jsonify({"status": "error", "message": "Prompt is required"})

        # Ensure folder exists
        if not save_folder or not os.path.isdir(save_folder):
            return jsonify({"status": "error", "message": "Invalid save_folder path"})

        os.makedirs(save_folder, exist_ok=True)

        # Use the edit endpoint if a reference image is included
        if ref_image:
            result = client.images.edit(
    model="gpt-image-1",
    image=(ref_image.filename, ref_image.stream, ref_image.mimetype),
    prompt=prompt,
    size=size,
    quality=quality,
    background=background
)

        else:
            result = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size=size,
                quality=quality,
                background=background
            )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_name = prompt.replace(" ", "_").replace(":", "").replace("/", "_")[:40]
        filename = f"{safe_name}_{timestamp}.png"
        output_path = os.path.join(save_folder, filename)

        with open(output_path, "wb") as f:
            f.write(image_bytes)

        return jsonify({"status": "success", "image_path": output_path})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(port=5001)

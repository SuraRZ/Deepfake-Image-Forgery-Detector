"""
Flask app — ties the analysis modules to a web UI.

Flow for a single request:
  1. User uploads an image via the browser (templates/index.html).
  2. /analyze saves it, runs ELA -> hotspot detection -> metadata check.
  3. We draw a red box on a copy of the original at the hotspot location.
  4. We return JSON with URLs to the three images (original, ELA heatmap,
     annotated) plus the verdict/reasons — the frontend JS renders these.

Images are saved under static/uploads/ with a random ID per request so
concurrent users don't collide, and so Flask can serve them back as static
files without any extra routing.
"""

import os
import uuid

from flask import Flask, request, render_template, jsonify, url_for
from PIL import Image, ImageDraw

from analysis.ela import compute_ela
from analysis.hotspot import find_hotspot
from analysis.metadata import extract_metadata_flags
from analysis.scorer import build_verdict

app = Flask(__name__)

UPLOAD_DIR = os.path.join("static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {"jpg", "jpeg", "png"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("image")
    if not file or file.filename == "":
        return jsonify({"error": "No image uploaded."}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Please upload a JPG or PNG image."}), 400

    uid = uuid.uuid4().hex[:10]
    ext = file.filename.rsplit(".", 1)[1].lower()
    raw_path = os.path.join(UPLOAD_DIR, f"{uid}_raw.{ext}")
    original_path = os.path.join(UPLOAD_DIR, f"{uid}_original.jpg")

    # Save the untouched upload first — this preserves EXIF exactly as the
    # camera/phone/editor wrote it, so metadata analysis sees the real data.
    file.save(raw_path)

    # Separately, build a normalized JPEG copy for ELA. This step legitimately
    # drops EXIF (re-encoding needs a clean baseline), which is fine because
    # ELA never looks at metadata in the first place.
    Image.open(raw_path).convert("RGB").save(original_path, "JPEG", quality=95)

    ela_image, ela_array = compute_ela(original_path)
    ela_path = os.path.join(UPLOAD_DIR, f"{uid}_ela.jpg")
    ela_image.save(ela_path)

    hotspot = find_hotspot(ela_array)

    annotated_path = os.path.join(UPLOAD_DIR, f"{uid}_annotated.jpg")
    annotated = Image.open(original_path).convert("RGB")
    if hotspot:
        draw = ImageDraw.Draw(annotated)
        x, y, w, h = hotspot["x"], hotspot["y"], hotspot["w"], hotspot["h"]
        draw.rectangle([x, y, x + w, y + h], outline="red", width=4)
    annotated.save(annotated_path)

    metadata_flags, metadata_details = extract_metadata_flags(raw_path)
    verdict, reasons, score = build_verdict(metadata_flags, hotspot)

    return jsonify({
        "original_url": url_for("static", filename=f"uploads/{uid}_original.jpg"),
        "ela_url": url_for("static", filename=f"uploads/{uid}_ela.jpg"),
        "annotated_url": url_for("static", filename=f"uploads/{uid}_annotated.jpg"),
        "verdict": verdict,
        "score": score,
        "reasons": reasons,
        "metadata": metadata_details,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)

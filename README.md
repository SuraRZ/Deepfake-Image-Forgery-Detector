# Deepfake / Image Forgery Detector

## 1. Install Python
Use Python 3.10 or 3.11 if possible.

## 2. Open Command Prompt in this folder

Create a virtual environment:
    python -m venv venv

Activate it on Windows:
    venv\Scripts\activate

Install dependencies:
    pip install -r requirements.txt

## 3. Run
    python app.py

Open:
    http://127.0.0.1:5001

## 4. Test
Upload a JPG or PNG image.

The application:
- saves a normalized JPEG copy
- creates an ELA map
- detects a possible high-error hotspot
- checks EXIF metadata
- combines the signals into a transparent heuristic verdict

IMPORTANT:
This is a forensic screening prototype, not proof that an image is authentic or forged.
ELA and EXIF can produce false positives and false negatives.

## Project structure

app.py
analysis/
    __init__.py
    ela.py
    hotspot.py
    metadata.py
    scorer.py
templates/
    index.html
static/
    script.js
    style.css
    uploads/   (created automatically)
requirements.txt


4. accuracy, precision, recall, F1 and confusion matrix
5. comparison between the ML model and the ELA+metadata baseline
6. optional Grad-CAM/saliency visualization

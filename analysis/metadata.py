"""
Metadata Forensics
====================

Camera-original photos carry EXIF metadata: camera make/model, exposure
settings, GPS (sometimes), and often both a capture timestamp and a
modification timestamp. Editing software tends to leave fingerprints in
this metadata:

  - A "Software" tag naming an editor (Photoshop, GIMP, Lightroom...)
    instead of a camera or phone model.
  - A modification date that differs from the original capture date.
  - EXIF missing entirely — common when an image has been re-saved,
    screenshotted, or passed through certain apps that strip it.

NONE OF THESE PROVE MANIPULATION ON THEIR OWN. A photo can legitimately
lose its EXIF just by being sent through certain messaging apps, and plenty
of authentic photos get brightness/crop adjustments in Lightroom without
being "forged" in any meaningful sense. This is exactly why the app
combines these flags with the ELA hotspot score rather than trusting either
signal alone — see analysis/scorer.py.
"""

from PIL import Image
from PIL.ExifTags import TAGS

KNOWN_EDITORS = [
    "photoshop", "gimp", "snapseed", "lightroom",
    "illustrator", "paint.net", "affinity", "pixelmator",
]


def extract_metadata_flags(image_path):
    flags = []
    details = {}

    img = Image.open(image_path)
    exif_data = img._getexif() if hasattr(img, "_getexif") else None

    if not exif_data:
        flags.append("No EXIF metadata found — common after re-saving or re-uploading, but also seen in edited images with metadata stripped.")
        return flags, details

    tags = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif_data.items()}
    details = {
        k: str(v) for k, v in tags.items()
        if k in ("Make", "Model", "Software", "DateTime", "DateTimeOriginal")
    }

    software = str(tags.get("Software", "")).lower()
    if any(editor in software for editor in KNOWN_EDITORS):
        flags.append(f"Image was processed by editing software: {tags.get('Software')}")

    original = tags.get("DateTimeOriginal")
    modified = tags.get("DateTime")
    if original and modified and original != modified:
        flags.append(f"Capture date ({original}) differs from modification date ({modified}).")

    return flags, details

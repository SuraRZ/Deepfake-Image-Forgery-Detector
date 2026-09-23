"""
Error Level Analysis (ELA)
===========================

THE IDEA
--------
JPEG doesn't store an image pixel-by-pixel. It compresses the image in
8x8 pixel blocks, and every block loses a small, mathematically predictable
amount of detail (this is "lossy" compression). Crucially: the amount lost
depends on how many times that specific block has *already* been compressed.

A camera-original JPEG has been compressed exactly once. Every 8x8 block in
it has seen the same single compression pass, so its blocks all sit at
roughly the same "error level" — how much they'd change if compressed again.

Now suppose someone opens that photo, pastes in a patch from another image
(or clones out an object), and saves it as a JPEG again. The pasted region
was compressed a *different* number of times than the rest of the photo —
it has its own separate compression history. The rest of the image has now
been compressed twice; the pasted patch has a different count entirely.

ELA exploits this. We take the image, re-save it at a known JPEG quality,
and measure the pixel-by-pixel difference between the original and the
resave. In an untouched photo, that difference is small and roughly uniform
everywhere. In an edited photo, the tampered region typically lights up
brighter or darker than its surroundings, because it responds differently
to the extra compression pass.

IMPORTANT HONESTY NOTE
-----------------------
ELA is a well-known *first-pass indicator*, not proof. It has real failure
modes worth knowing (and worth saying out loud in your README/interview):
  - PNG or other lossless sources re-saved as JPEG show ELA differences
    everywhere (there's no "first compression" to compare against).
  - High-contrast edges (text, logos, hard object boundaries) naturally
    show higher ELA response even in authentic images — that's a false
    positive trap if you don't account for it.
  - A skilled editor can flatten/re-compress an edited image repeatedly to
    equalize error levels and evade ELA.
That's *why* this tool combines ELA with metadata analysis rather than
relying on ELA alone — see analysis/metadata.py.
"""

from PIL import Image, ImageChops, ImageEnhance
import numpy as np
import io


def compute_ela(image_path, quality=90, scale_cap=255):
    """
    Returns:
        ela_image: a PIL Image (RGB) visualizing the error map — this is
                   what gets shown to the user, brightness-amplified so
                   differences are actually visible to the human eye.
        ela_array: the same data as a single-channel (grayscale) numpy
                   array, used internally for thresholding/hotspot detection.
    """
    original = Image.open(image_path).convert("RGB")

    # Re-save the image in memory at a fixed JPEG quality. Using an in-memory
    # buffer instead of writing to disk keeps this fast and avoids leaving
    # temp files behind.
    buffer = io.BytesIO()
    original.save(buffer, "JPEG", quality=quality)
    buffer.seek(0)
    resaved = Image.open(buffer)

    # Pixel-by-pixel absolute difference between original and resave.
    diff = ImageChops.difference(original, resaved)

    # The raw difference is usually tiny (values like 2-10 out of 255),
    # which is invisible to the eye. We rescale so the brightest difference
    # in the image maps to full brightness (255) — this is what makes the
    # ELA output visually readable instead of looking like a black square.
    extrema = diff.getextrema()
    max_diff = max(channel_max for _, channel_max in extrema) or 1
    scale = scale_cap / max_diff

    ela_image = ImageEnhance.Brightness(diff).enhance(scale)
    ela_array = np.array(ela_image.convert("L"))  # collapse to grayscale intensity

    return ela_image, ela_array

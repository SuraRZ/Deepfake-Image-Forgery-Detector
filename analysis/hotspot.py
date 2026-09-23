"""
Hotspot Localization
=====================

ELA gives us a full-image error map, but a heatmap alone is hard for a
human to act on quickly. This module finds the single most suspicious
*region* in that map and returns a bounding box, so the app can draw a red
rectangle directly on the original photo — this is the "point at the
suspicious area" moment that makes the tool feel like a real forensic
instrument rather than a generic image filter.

HOW IT WORKS
------------
1. Threshold: convert the grayscale ELA map to pure black/white — any pixel
   brighter than `threshold` becomes "suspicious" (white), everything else
   becomes black. This turns a continuous heatmap into discrete regions.
2. Dilate: suspicious pixels from a real edit are rarely a single blob —
   compression artifacts create scattered bright pixels. Dilation grows
   each white pixel outward, merging nearby scattered spots into one solid
   connected region so we can treat them as a single area of interest.
3. Contours: OpenCV's contour detection finds the outlines of each
   connected white region.
4. Filter + pick largest: tiny contours (a few stray pixels) are noise, not
   tampering — we discard anything below `min_area_ratio` of the image, then
   take the largest surviving contour as "the" hotspot.
"""

import cv2
import numpy as np


def find_hotspot(ela_array, threshold=80, min_area_ratio=0.02):
    _, thresh = cv2.threshold(ela_array, threshold, 255, cv2.THRESH_BINARY)
    thresh = cv2.dilate(thresh, np.ones((5, 5), np.uint8), iterations=2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    image_area = ela_array.shape[0] * ela_array.shape[1]
    candidates = [c for c in contours if cv2.contourArea(c) > image_area * min_area_ratio]
    if not candidates:
        return None

    largest = max(candidates, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    area_ratio = cv2.contourArea(largest) / image_area

    return {"x": int(x), "y": int(y), "w": int(w), "h": int(h), "area_ratio": area_ratio}

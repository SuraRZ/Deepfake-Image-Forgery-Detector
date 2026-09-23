"""
Diagnostic tool — NOT part of the app itself, just for calibration.

Run this against a known-clean photo and a known-edited photo to see the
actual numbers behind the scenes, instead of guessing at threshold values.

Usage:
    python diagnose.py path/to/image.jpg
"""

import sys
import numpy as np
from analysis.ela import compute_ela

def diagnose(path):
    _, ela_array = compute_ela(path)

    print(f"\n=== {path} ===")
    print(f"Image size: {ela_array.shape[1]}x{ela_array.shape[0]} = {ela_array.size} pixels")
    print(f"Min: {ela_array.min()}  Max: {ela_array.max()}  Mean: {ela_array.mean():.2f}")
    percentiles = [50, 75, 90, 95, 97, 99, 99.5]
    values = np.percentile(ela_array, percentiles)
    for p, v in zip(percentiles, values):
        print(f"  {p}th percentile: {v:.1f}")

    print("\n  Threshold -> % of pixels above it (before dilation):")
    for t in [40, 60, 80, 100, 120, 140, 160, 180, 200]:
        pct = (ela_array > t).mean() * 100
        print(f"    threshold={t:>3}: {pct:.2f}% of pixels")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose.py <image1> [image2] ...")
        sys.exit(1)
    for path in sys.argv[1:]:
        diagnose(path)

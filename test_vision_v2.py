"""Quick test of vision components in isolation"""
import sys
sys.path.insert(0, '.')

import mss
from PIL import Image
import numpy as np

print("=== Vision Component Test ===")

# 1. Test screen capture
print("\n[1] Testing MSS Screen Capture...")
try:
    with mss.mss() as sct:
        img = sct.grab(sct.monitors[1])
        pil_img = Image.frombytes('RGB', img.size, img.bgra, 'raw', 'BGRX')
        print(f"    ✓ Captured: {pil_img.size}")
except Exception as e:
    print(f"    ✗ Capture failed: {e}")
    exit(1)

# 2. Test EasyOCR
print("\n[2] Testing EasyOCR (GPU)...")
try:
    import easyocr
    reader = easyocr.Reader(['en'], gpu=True, verbose=False)
    result = reader.readtext(np.array(pil_img), detail=0, paragraph=True)
    print(f"    ✓ OCR Found: {len(result)} text blocks")
    if result:
        sample = result[0][:100] if len(result[0]) > 100 else result[0]
        print(f"    Sample: {sample}")
except Exception as e:
    print(f"    ✗ OCR failed: {e}")

# 3. Test pygetwindow
print("\n[3] Testing pygetwindow...")
try:
    import pygetwindow as gw
    windows = gw.getAllWindows()
    visible = [w.title for w in windows if w.visible and w.title]
    print(f"    ✓ Found {len(visible)} visible windows")
    print(f"    Top 5: {visible[:5]}")
except Exception as e:
    print(f"    ✗ pygetwindow failed: {e}")

print("\n=== Test Complete ===")

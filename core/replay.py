# replay placeholder
import time
from typing import Callable, List, Optional

import cv2
import numpy as np
import pyautogui

from core.matcher import multi_crop_match
from core.ocr import ocr_in_roi_easy
from core.steps import (
    BaseStep,
    ClickStep,
    TextStep,
    KeyStep,
    WaitStep,
    VisionClickStep,
    VisionCheckStep,
)

pyautogui.FAILSAFE = False

def replay(steps: List[BaseStep],
           threshold: float = 0.8,
           on_status: Optional[Callable[[str], None]] = None):
    def status(msg: str):
        if on_status:
            on_status(msg)
        print("[Replay]", msg)

    for idx, step in enumerate(steps):
        # Pause
        if isinstance(step, WaitStep):
            status(f"Pause {step.duration:.2f}s (Schritt {idx+1})")
            time.sleep(step.duration)
            continue

        # Key
        if isinstance(step, KeyStep):
            status(f"Tastendruck '{step.key}' (Schritt {idx+1})")
            pyautogui.press(step.key)
            time.sleep(0.1)
            continue

        # Text
        if isinstance(step, TextStep):
            status(f"Texteingabe \"{step.text}\" (Schritt {idx+1})")
            if step.text:
                pyautogui.write(step.text, interval=0.02)
            time.sleep(0.1)
            continue

        # VisionClick / VisionCheck – aktuell nur Platzhalter-Logik
        if isinstance(step, VisionClickStep):
            status(f"[VisionClick] (noch nicht implementiert) '{step.search_text}' (Schritt {idx+1})")
            continue

        if isinstance(step, VisionCheckStep):
            status(f"[VisionCheck] (noch nicht implementiert) '{step.search_text}' (Schritt {idx+1})")
            continue

        # Klassischer Klick mit Bild + optional OCR
        if isinstance(step, ClickStep):
            status(f"Klick-Schritt {idx+1} wird ausgeführt...")
            screenshot = pyautogui.screenshot()
            screen_np = np.array(screenshot)
            screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

            template = cv2.imread(step.screenshot)
            if template is None:
                status(f"Template nicht gefunden: {step.screenshot}")
                continue

            val, loc, w, h = multi_crop_match(screen_bgr, template)
            x, y = loc
            cx = x + w // 2
            cy = y + h // 2

            if step.ocr_enabled and step.ocr_text:
                roi = (x, y, w, h)
                ocr_res = ocr_in_roi_easy(screen_bgr, roi, step.ocr_text)
                if ocr_res is not None:
                    (cx, cy), (bx, by, bw, bh), conf, text = ocr_res
                    status(f"OCR-Treffer \"{text}\" conf={conf:.2f} @ ({cx},{cy})")
                    pyautogui.click(cx, cy)
                    time.sleep(0.2)
                    continue
                else:
                    status(f"OCR: Kein Treffer für \"{step.ocr_text}\", nutze Bild-Match.")

            status(f"Bild-Match: {val*100:.1f}% @ ({cx},{cy})")
            if val >= threshold:
                pyautogui.click(cx, cy)
            else:
                status("Match unterhalb Schwelle – kein Klick.")
            time.sleep(0.2)
            continue

        status(f"Unbekannter Schritt-Typ: {step.type} (Index {idx})")

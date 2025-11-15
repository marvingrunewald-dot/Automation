# recorder placeholder
import os
from datetime import datetime
from typing import Callable

import pyautogui
from pynput import mouse, keyboard

from core.steps import ClickStep

pyautogui.FAILSAFE = False

class Recorder:
    def __init__(self, folder: str, callback_step_added: Callable,
                 screenshot_size: int = 120):
        self.folder = folder
        self.callback = callback_step_added
        self.screenshot_size = screenshot_size

        self.recording = False
        self.last_click_time = None
        self.m_listener = None
        self.k_listener = None

    def start(self):
        if self.recording:
            return
        self.recording = True
        self.last_click_time = None
        self.m_listener = mouse.Listener(on_click=self._on_click)
        self.k_listener = keyboard.Listener(on_press=self._on_press)
        self.m_listener.start()
        self.k_listener.start()
        print("[Recorder] Aufnahme gestartet (ESC zum Beenden).")

    def stop(self):
        if not self.recording:
            return
        self.recording = False
        if self.m_listener:
            self.m_listener.stop()
        if self.k_listener:
            self.k_listener.stop()
        print("[Recorder] Aufnahme beendet.")

    def _on_press(self, key):
        try:
            if key == keyboard.Key.esc:
                self.stop()
        except Exception:
            pass

    def _on_click(self, x, y, button, pressed):
        if not self.recording or not pressed:
            return

        now = datetime.now()
        ts = now.strftime("%Y%m%d_%H%M%S_%f")
        elapsed = 0.0
        if self.last_click_time is not None:
            elapsed = (now - self.last_click_time).total_seconds()
        self.last_click_time = now

        half = self.screenshot_size // 2
        left = max(int(x - half), 0)
        top = max(int(y - half), 0)

        snap = pyautogui.screenshot(region=(
            left, top, self.screenshot_size, self.screenshot_size
        ))
        os.makedirs(self.folder, exist_ok=True)
        path = os.path.join(self.folder, f"click_{ts}.png")
        snap.save(path)
        print(f"[Recorder] Screenshot gespeichert: {path}")

        step = ClickStep(screenshot=path, elapsed=elapsed)
        self.callback(step)

import os
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

from core.project import save_project, load_project
from core.recorder import Recorder
from core.replay import replay
from core.steps import ClickStep
from gui.step_list import StepListGUI
from gui.dialogs import (
    show_text_dialog,
    show_key_dialog,
    show_wait_dialog,
)
from gui.screenshot_overlay import ScreenshotOverlay

LOG_FOLDER = "click_logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sikulix Vision Automation (Pro)")
        self.root.geometry("900x650")

        self.steps = []

        self.recorder = Recorder(
            folder=LOG_FOLDER,
            callback_step_added=self.add_step,
            screenshot_size=120
        )

        self._build_ui()
        self._setup_hotkeys()

    def _build_ui(self):
        title = tk.Label(self.root, text="Sikulix Vision Automation", font=("Arial", 18))
        title.pack(pady=8)

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5)

        tk.Button(top_frame, text="Aufzeichnen (ESC)", width=18,
                  command=self.start_record).grid(row=0, column=0, padx=4, pady=2)
        tk.Button(top_frame, text="Replay", width=18,
                  command=self.start_replay).grid(row=0, column=1, padx=4, pady=2)
        tk.Button(top_frame, text="Screenshot ziehen", width=18,
                  command=self.manual_screenshot).grid(row=0, column=2, padx=4, pady=2)

        tk.Button(top_frame, text="Text-Schritt", width=18,
                  command=self.add_text_step).grid(row=1, column=0, padx=4, pady=2)
        tk.Button(top_frame, text="Tasten-Schritt", width=18,
                  command=self.add_key_step).grid(row=1, column=1, padx=4, pady=2)
        tk.Button(top_frame, text="Pause-Schritt", width=18,
                  command=self.add_wait_step).grid(row=1, column=2, padx=4, pady=2)

        tk.Button(top_frame, text="Projekt laden", width=18,
                  command=self.load_project).grid(row=2, column=0, padx=4, pady=2)
        tk.Button(top_frame, text="Projekt speichern", width=18,
                  command=self.save_project).grid(row=2, column=1, padx=4, pady=2)
        tk.Button(top_frame, text="Beenden", width=18,
                  command=self.root.destroy).grid(row=2, column=2, padx=4, pady=2)

        self.status_var = tk.StringVar(value="Bereit.")
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill="x", padx=10, pady=4)
        tk.Label(status_frame, textvariable=self.status_var, anchor="w").pack(fill="x")

        self.step_list = StepListGUI(self.root, self.steps, on_change=self.refresh_steps)
        self.step_list.frame.pack(fill="both", expand=True, padx=10, pady=8)

    def _setup_hotkeys(self):
        self.root.bind("<F5>", lambda e: self.start_replay())
        self.root.bind("<F6>", lambda e: self.start_record())
        self.root.bind("<Control-s>", lambda e: self.save_project())
        self.root.bind("<Control-o>", lambda e: self.load_project())

    def set_status(self, text: str):
        self.status_var.set(text)
        self.root.update_idletasks()

    def add_step(self, step):
        self.steps.append(step)
        self.refresh_steps()

    def refresh_steps(self):
        self.step_list.refresh()

    def start_record(self):
        self.set_status("Aufnahme gestartet (ESC zum Beenden)...")
        self.recorder.start()

    def start_replay(self):
        if not self.steps:
            messagebox.showwarning("Replay", "Keine Schritte vorhanden!")
            return
        self.set_status("Replay läuft...")
        replay(self.steps, on_status=self.set_status)
        self.set_status("Replay beendet.")

    def manual_screenshot(self):
        def on_image(img):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(LOG_FOLDER, f"manual_{ts}.png")
            img.save(path)
            step = ClickStep(screenshot=path, elapsed=0.0)
            self.add_step(step)
            self.set_status(f"Manueller Screenshot hinzugefügt: {path}")

        ScreenshotOverlay(self.root, on_image)

    def add_text_step(self):
        step = show_text_dialog(self.root)
        if step:
            self.add_step(step)

    def add_key_step(self):
        step = show_key_dialog(self.root)
        if step:
            self.add_step(step)

    def add_wait_step(self):
        step = show_wait_dialog(self.root)
        if step:
            self.add_step(step)

    def save_project(self, *_args):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON-Dateien", "*.json")]
        )
        if not path:
            return
        save_project(path, self.steps)
        self.set_status(f"Projekt gespeichert: {path}")

    def load_project(self, *_args):
        path = filedialog.askopenfilename(
            filetypes=[("JSON-Dateien", "*.json")]
        )
        if not path:
            return
        self.steps = load_project(path)
        self.step_list.steps = self.steps
        self.refresh_steps()
        self.set_status(f"Projekt geladen: {path}")

    def run(self):
        self.root.mainloop()

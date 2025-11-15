# step list placeholder
import os
import tkinter as tk
from PIL import Image, ImageTk

from gui.dialogs import show_ocr_dialog
from core.steps import ClickStep, TextStep, KeyStep, WaitStep, VisionClickStep, VisionCheckStep

class StepListGUI:
    def __init__(self, parent, steps, on_change):
        self.steps = steps
        self.on_change = on_change

        self.frame = tk.Frame(parent, relief="sunken", borderwidth=2)

        self.canvas = tk.Canvas(self.frame)
        self.scroll = tk.Scrollbar(self.frame, orient="vertical",
                                   command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas)

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")

    def refresh(self):
        for w in self.inner.winfo_children():
            w.destroy()

        for i, step in enumerate(self.steps):
            self._build_row(i, step)

    def _build_row(self, index, step):
        row = tk.Frame(self.inner, pady=3)
        row.pack(fill="x", padx=4)

        if isinstance(step, ClickStep):
            desc = f"{index+1}. Klick (OCR={step.ocr_enabled})"
        elif isinstance(step, TextStep):
            desc = f"{index+1}. Text: {step.text}"
        elif isinstance(step, KeyStep):
            desc = f"{index+1}. Taste: {step.key}"
        elif isinstance(step, WaitStep):
            desc = f"{index+1}. Pause: {step.duration:.2f}s"
        elif isinstance(step, VisionClickStep):
            desc = f"{index+1}. Vision-Klick: \"{step.search_text}\""
        elif isinstance(step, VisionCheckStep):
            must = "muss" if step.must_exist else "darf nicht"
            desc = f"{index+1}. Vision-Check: '{step.search_text}' {must} existieren"
        else:
            desc = f"{index+1}. {step.type}"

        tk.Label(row, text=desc, width=50, anchor="w").pack(side="left")

        if isinstance(step, ClickStep) and os.path.exists(step.screenshot):
            try:
                img = Image.open(step.screenshot)
                img.thumbnail((40, 40))
                tk_img = ImageTk.PhotoImage(img)
                lbl = tk.Label(row, image=tk_img)
                lbl.image = tk_img
                lbl.pack(side="left", padx=4)
            except Exception:
                tk.Label(row, text="[Bildfehler]").pack(side="left", padx=4)
        else:
            tk.Label(row, text="").pack(side="left", padx=4)

        btn_frame = tk.Frame(row)
        btn_frame.pack(side="right")

        tk.Button(btn_frame, text="▲",
                  command=lambda i=index: self.move_up(i)).pack(side="left")
        tk.Button(btn_frame, text="▼",
                  command=lambda i=index: self.move_down(i)).pack(side="left")
        tk.Button(btn_frame, text="✖",
                  command=lambda i=index: self.delete(i)).pack(side="left")

        if isinstance(step, ClickStep):
            tk.Button(btn_frame, text="OCR",
                      command=lambda s=step: self.edit_ocr(s)).pack(side="left", padx=2)

    def edit_ocr(self, step):
        show_ocr_dialog(self.frame, step)
        self.on_change()

    def move_up(self, index):
        if index > 0:
            self.steps[index-1], self.steps[index] = self.steps[index], self.steps[index-1]
            self.on_change()

    def move_down(self, index):
        if index < len(self.steps) - 1:
            self.steps[index+1], self.steps[index] = self.steps[index+1], self.steps[index]
            self.on_change()

    def delete(self, index):
        del self.steps[index]
        self.on_change()

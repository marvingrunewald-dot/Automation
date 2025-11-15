# dialogs placeholder
import tkinter as tk
from tkinter import simpledialog

from core.steps import TextStep, KeyStep, WaitStep

KEY_OPTIONS = [
    "enter", "tab", "esc", "backspace",
    "up", "down", "left", "right",
    "space"
] + [chr(c) for c in range(ord('a'), ord('z') + 1)]

def show_ocr_dialog(parent, step):
    win = tk.Toplevel(parent)
    win.title("OCR Einstellungen")
    win.resizable(False, False)
    win.grab_set()

    enabled = tk.BooleanVar(value=step.ocr_enabled)
    txt = tk.StringVar(value=step.ocr_text)

    tk.Checkbutton(win, text="OCR aktivieren", variable=enabled).pack(pady=5, anchor="w", padx=10)
    tk.Label(win, text="Suchtext (z.B. 'Pflegegrad 1')").pack(anchor="w", padx=10)
    entry = tk.Entry(win, textvariable=txt, width=30)
    entry.pack(padx=10, pady=5)

    def save():
        step.ocr_enabled = enabled.get()
        step.ocr_text = txt.get().strip()
        win.destroy()

    tk.Button(win, text="OK", command=save).pack(pady=10)

def show_text_dialog(parent):
    text = simpledialog.askstring("Texteingabe", "Text eingeben:", parent=parent)
    if text is None:
        return None
    return TextStep(text=text)

def show_key_dialog(parent):
    win = tk.Toplevel(parent)
    win.title("Tastendruck")
    win.resizable(False, False)
    win.grab_set()

    var = tk.StringVar(value=KEY_OPTIONS[0])

    tk.Label(win, text="Taste auswählen:").pack(padx=10, pady=5)
    opt = tk.OptionMenu(win, var, *KEY_OPTIONS)
    opt.pack(padx=10, pady=5)

    chosen = {"step": None}

    def save():
        chosen["step"] = KeyStep(key=var.get())
        win.destroy()

    tk.Button(win, text="OK", command=save).pack(pady=10)
    win.wait_window()
    return chosen["step"]

def show_wait_dialog(parent):
    dur = simpledialog.askfloat("Pause", "Dauer in Sekunden:", minvalue=0.0, parent=parent)
    if dur is None:
        return None
    return WaitStep(duration=float(dur))

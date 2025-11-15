# overlay placeholder
import tkinter as tk
import pyautogui

class ScreenshotOverlay:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.start_x = None
        self.start_y = None

        self.win = tk.Toplevel(parent)
        self.win.attributes("-fullscreen", True)
        self.win.attributes("-alpha", 0.3)
        self.win.configure(bg="black")
        self.win.overrideredirect(True)
        self.win.lift()
        self.win.focus_force()

        self.canvas = tk.Canvas(self.win, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.rect = None

        self.win.bind("<ButtonPress-1>", self.on_down)
        self.win.bind("<B1-Motion>", self.on_move)
        self.win.bind("<ButtonRelease-1>", self.on_up)
        self.win.bind("<Escape>", lambda e: self.win.destroy())

    def on_down(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None

    def on_move(self, event):
        if self.start_x is None or self.start_y is None:
            return
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x_root, event.y_root
        if self.rect:
            self.canvas.coords(self.rect, x1, y1, x2, y2)
        else:
            self.rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline="red", width=3
            )

    def on_up(self, event):
        if self.start_x is None or self.start_y is None:
            self.win.destroy()
            return

        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x_root, event.y_root
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x1 - x2)
        height = abs(y1 - y2)

        self.win.destroy()

        if width < 5 or height < 5:
            return

        img = pyautogui.screenshot(region=(left, top, width, height))
        if self.callback:
            self.callback(img)

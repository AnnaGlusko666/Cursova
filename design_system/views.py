from tkinter import ttk
import tkinter as tk
from var import PALETTE


class BaseView(ttk.Frame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.build()

    def build(self):
        pass

class AlgorithmsView(BaseView):
    def build(self):
        self.master.configure(bg=PALETTE["bg"])
        wrapper = tk.Frame(self, bg=PALETTE["bg"], padx=16, pady=16)
        tk.Label(wrapper, text="Алгоритми (плейсхолдер)", bg=PALETTE["bg"], fg=PALETTE["text"], font=("TkDefaultFont", 16, "bold")).pack(anchor="w")
        tk.Label(wrapper, text="Тут з'являться короткі довідки.", bg=PALETTE["bg"], fg=PALETTE["muted"]).pack(anchor="w", pady=(6,0))
        wrapper.pack(expand=True, fill="both")

class VisualizerView(BaseView):
    def build(self):
        self.master.configure(bg=PALETTE["bg"])
        wrapper = tk.Frame(self, bg=PALETTE["bg"], padx=16, pady=16)
        tk.Label(wrapper, text="Візуалізатор (плейсхолдер)", bg=PALETTE["bg"], fg=PALETTE["text"], font=("TkDefaultFont", 16, "bold")).pack(anchor="w")
        tk.Label(wrapper, text="Тут буде покрокове шифрування.", bg=PALETTE["bg"], fg=PALETTE["muted"]).pack(anchor="w", pady=(6,0))
        wrapper.pack(expand=True, fill="both")

class PlaygroundView(BaseView):
    def build(self):
        self.master.configure(bg=PALETTE["bg"])
        wrapper = tk.Frame(self, bg=PALETTE["bg"], padx=16, pady=16)
        tk.Label(wrapper, text="Пісочниця (плейсхолдер)", bg=PALETTE["bg"], fg=PALETTE["text"], font=("TkDefaultFont", 16, "bold")).pack(anchor="w")
        tk.Label(wrapper, text="Справжнє шифрування підключимо далі.", bg=PALETTE["bg"], fg=PALETTE["muted"]).pack(anchor="w", pady=(6,0))
        wrapper.pack(expand=True, fill="both")

class SettingsView(BaseView):
    def build(self):
        self.master.configure(bg=PALETTE["bg"])
        wrapper = tk.Frame(self, bg=PALETTE["bg"], padx=16, pady=16)
        tk.Label(wrapper, text="Налаштування (плейсхолдер)", bg=PALETTE["bg"], fg=PALETTE["text"], font=("TkDefaultFont", 16, "bold")).pack(anchor="w")
        wrapper.pack(expand=True, fill="both")

class AboutView(BaseView):
    def build(self):
        self.master.configure(bg=PALETTE["bg"])
        wrapper = tk.Frame(self, bg=PALETTE["bg"], padx=16, pady=16)
        tk.Label(wrapper, text="Про застосунок", bg=PALETTE["bg"], fg=PALETTE["text"], font=("TkDefaultFont", 16, "bold")).pack(anchor="w")
        tk.Label(wrapper, text=("Навчальний застосунок для демонстрації симетричних шифрів."), bg=PALETTE["bg"], fg=PALETTE["muted"], justify="left").pack(anchor="w", pady=(6,0))
        wrapper.pack(expand=True, fill="both")

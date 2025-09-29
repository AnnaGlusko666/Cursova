import tkinter as tk
from tkinter import ttk
from var import PALETTE
from design_system import views as vw
from design_system import design as ds

APP_TITLE = "Симетричні шифри — демонстратор"
APP_MIN_SIZE = (1200, 700)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.minsize(*APP_MIN_SIZE)
        self.configure(bg=PALETTE["bg"])
        self._setup_styles()
        self._build_layout()
        self.show_view("Home")

    # Styles
    def _setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=PALETTE["bg"])
        style.configure("Title.TLabel", foreground=PALETTE["text"], background=PALETTE["bg"], font=("TkDefaultFont", 18, "bold"))
        style.configure("Body.TLabel", foreground=PALETTE["muted"], background=PALETTE["bg"], font=("TkDefaultFont", 10))
        style.configure("Nav.TButton", padding=(12, 10))
        style.configure("Card.TFrame", padding=12)
        style.configure("CardTitle.TLabel", foreground=PALETTE["text"], background=PALETTE["card"], font=("TkDefaultFont", 12, "bold"))
        style.configure("CardText.TLabel", foreground=PALETTE["muted"], background=PALETTE["card"], font=("TkDefaultFont", 10))

    # Layout
    def _build_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.content = ttk.Frame(self, style="TFrame")
        self.content.grid(row=0, column=0, sticky="nsew")
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        self.views = {}

    def show_view(self, name: str):
        for child in self.content.winfo_children():
            child.destroy()

        view_cls = {
            "Home": ds.HomeView,
            "Algorithms": vw.AlgorithmsView,
            "Visualizer": vw.VisualizerView,
            "Playground": vw.PlaygroundView,
            "Settings": vw.SettingsView,
            "About": vw.AboutView,
        }.get(name, ds.HomeView)

        view = view_cls(self.content, controller=self)
        view.grid(row=0, column=0, sticky="nsew")
import tkinter as tk
from var import PALETTE
from design_system import views as vw
from ciphers import affine as af
from ciphers import alberti as alb
from ciphers import cesar as ces
from ciphers import playfair as pl
from ciphers import railfence as rf
from ciphers import vigenere as vg


class Card(tk.Frame):
    def __init__(self, master, title: str, desc: str, badge: str | None = None, tags: list[str] | None = None, command=None):
        super().__init__(master, bg=PALETTE["card"], highlightthickness=0, bd=0)
        self.command = command
        self._build(title, desc, badge, tags or [])
        self.bind("<Enter>", lambda e: self.configure(bg=PALETTE["card_hover"]))
        self.bind("<Leave>", lambda e: self.configure(bg=PALETTE["card"]))
        self.bind("<Button-1>", lambda e: self._on_click())
        self._make_clickable()

    def _chip(self, parent, text):
        lbl = tk.Label(parent, text=text, bg=PALETTE["chip"], fg=PALETTE["muted"], padx=8, pady=2)
        lbl.pack(side="left", padx=(0,6))

    def _on_click(self):
        if callable(self.command):
            self.command()

    def _make_clickable(self):
        def bind_recursive(w):
            try:
                w.bind("<Button-1>", lambda e: self._on_click())
            except Exception:
                pass
            try:
                w.configure(cursor="hand2")
            except Exception:
                pass
            for child in getattr(w, "winfo_children", lambda: [])():
                bind_recursive(child)

        bind_recursive(self)

    def _build(self, title, desc, badge, tags):
        container = tk.Frame(self, bg=PALETTE["card"])
        container.pack(fill="both", expand=True, padx=18, pady=16)
        top = tk.Frame(container, bg=PALETTE["card"])
        top.pack(fill="x")
        if badge:
            b = tk.Label(top, text=badge, bg=PALETTE["chip"], fg=PALETTE["muted"], padx=8, pady=3)
            b.pack(side="left")
        title_lbl = tk.Label(container, text=title, bg=PALETTE["card"], fg=PALETTE["text"], font=("TkDefaultFont", 14, "bold"))
        title_lbl.pack(anchor="w", pady=(10,2))
        desc_lbl = tk.Label(container, text=desc, bg=PALETTE["card"], fg=PALETTE["muted"], justify="left", wraplength=340)
        desc_lbl.pack(anchor="w")
        tags_row = tk.Frame(container, bg=PALETTE["card"])
        tags_row.pack(anchor="w", pady=(14,0))
        for t in tags:
            self._chip(tags_row, t)


class HomeView(vw.BaseView):
    def build(self):
        self.configure(style="TFrame")

        header = tk.Frame(self, bg=PALETTE["bg"])
        header.pack(fill="x", padx=24, pady=(18,10))

        badge = tk.Frame(header, bg=PALETTE["panel"], width=44, height=44)
        badge.pack_propagate(False)
        tk.Label(badge, text="Σ", bg=PALETTE["panel"], fg=PALETTE["text"], font=("TkDefaultFont", 18, "bold")).pack(expand=True)
        title_block = tk.Frame(header, bg=PALETTE["bg"])

        title_lbl = tk.Label(title_block, text="Симетричні шифри — демонстратор", bg=PALETTE["bg"], fg=PALETTE["text"], font=("TkDefaultFont", 16, "bold"))
        subtitle_lbl = tk.Label(title_block, text="Курсова робота • Навчальний застосунок", bg=PALETTE["bg"], fg=PALETTE["muted"], font=("TkDefaultFont", 10))
        title_lbl.pack(anchor="w")
        subtitle_lbl.pack(anchor="w")

        search_block = tk.Frame(header, bg=PALETTE["bg"])
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_block, textvariable=self.search_var, bg=PALETTE["panel"], fg=PALETTE["text"], insertbackground=PALETTE["text"], bd=0)
        search_entry.configure(highlightthickness=1, highlightbackground=PALETTE["panel"], relief="flat")
        search_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0,10))
        tk.Button(search_block, text="Розпізнати", command=self._do_search, bg=PALETTE["accent"], fg="#0b1020", activebackground=PALETTE["accent"], bd=0, padx=14, pady=6).pack(side="left")

        badge.grid(row=0, column=0, rowspan=2, sticky="w")
        title_block.grid(row=0, column=1, sticky="w", padx=(12,0))
        search_block.grid(row=0, column=2, sticky="ew", padx=(24,0))
        header.grid_columnconfigure(2, weight=1)

        section = tk.Frame(self, bg=PALETTE["bg"])
        section.pack(fill="x", padx=24)
        tk.Label(section, text="Оберіть шифр для демонстрації", bg=PALETTE["bg"], fg=PALETTE["text"], font=("TkDefaultFont", 18, "bold")).pack(anchor="w", pady=(8,6))
        tk.Label(section, text=("Клацніть по картці, щоб відкрити інтерактивне вікно з демонстрацією. Надалі тут з'являться\n"
                                "теорія, візуалізація та практика."), bg=PALETTE["bg"], fg=PALETTE["muted"], justify="left").pack(anchor="w", pady=(0,10))

        grid = tk.Frame(self, bg=PALETTE["bg"])
        grid.pack(fill="both", expand=True, padx=24, pady=8)

        cards = [
            ("Шифр Цезаря", "Класичний зсув алфавіту на k позицій.", "Базовий", ["алфавіт", "зсув", "моноалфавітний"]),
            ("Шифр Віженера", "Заміна з повторюваним ключем через квадрат Віженера.", "Поліалфавітний", ["ключ", "квадрат", "повторення"]),
            ("Шифр Частокол", "Транспозиційний запис по рядах у вигляді 'змійки'.", "Транспозиція", ["ряди", "зигзаг", "транспозиція"]),
            ("Шифр Альберті", "Поліалфавітний шифр із двома співісними дисками.", "Диски", ["диски", "налаштування", "ключ"]),
            ("Афінний шифр", "Заміна за формулою y = (a·x + b) mod m.", "Лінійний", ["a", "b", "модуль"]),
            ("Шифр Плейфера", "Заміна біграм за допомогою квадрату 5x5.", "5x5", ["біграми", "5x5", "ключ"]),
        ]
        self.cards_data = cards
        self.cards_grid = grid
        self._render_cards(self.cards_data)


        footer = tk.Frame(self, bg=PALETTE["bg"])
        footer.pack(fill="x", padx=24, pady=(6,18))
        tk.Label(footer, text="© 2025 Навчальний застосунок — Симетричні шифри. Створено для курсової роботи.", bg=PALETTE["bg"], fg=PALETTE["muted"]).pack()

    def _do_search(self):
        q = self.search_var.get().strip().lower()
        if not q:
            filtered = self.cards_data
        else:
            def matches(item):
                t, d, b, tags = item
                hay = " ".join([t, d, b, *tags]).lower()
                return q in hay

            filtered = [item for item in self.cards_data if matches(item)]
        self._render_cards(filtered)

    def _render_cards(self, data):
        for w in self.cards_grid.winfo_children():
            w.destroy()

        cols = 3
        for idx, (t, d, b, tags) in enumerate(data):
            r, c = divmod(idx, cols)
            card = Card(
                self.cards_grid,
                title=t, desc=d, badge=b, tags=tags,
                command=lambda n=t: self._open_cipher(n)
            )
            card.grid(row=r, column=c, sticky="nsew", padx=10, pady=10)

        for c in range(cols):
            self.cards_grid.grid_columnconfigure(c, weight=1)
        rows = max(1, (len(data) + cols - 1) // cols)
        for r in range(rows):
            self.cards_grid.grid_rowconfigure(r, weight=1)

    def _open_cipher(self, name: str):
        if name == "Шифр Цезаря":
            ces.CaesarWindow(self, theory_path="theory/caesar_theory.txt")
        elif name == "Шифр Віженера":
            vg.VigenereWindow(self, theory_path="theory/vigenere_theory.txt")
        elif name == "Шифр Частокол":
            rf.RailFenceWindow(self, theory_path="theory/railfence_theory.txt")
        elif name == "Шифр Альберті":
            alb.AlbertiWindow(self, theory_path="theory/alberti_theory.txt")
        elif name == "Афінний шифр":
            af.AffineWindow(self, theory_path="theory/affine_theory.txt")
        elif name == "Шифр Плейфера":
            pl.PlayfairWindow(self, theory_path="theory/playfair_theory.txt")
        else:
            self.controller.show_view("Visualizer")

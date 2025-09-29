import tkinter as tk
from tkinter import ttk
from var import PALETTE, ALPHABETS


class RailFenceWindow(tk.Toplevel):

    def __init__(self, master, theory_path=None):
        super().__init__(master)
        self.title("Шифр Частокол")
        self.configure(bg=PALETTE["bg2"])
        self.resizable(False, False)

        self.theory_path = theory_path
        self.mode = "form"

        # стан
        self.alphabet_name = tk.StringVar(value="LAT (A–Z, 26)")
        self.rails_var = tk.IntVar(value=3)
        self.only_letters = tk.BooleanVar(value=False)
        self.autoplay = tk.BooleanVar(value=False)
        self._after_id = None
        self._demo_index = 0

        self.card = tk.Frame(self, bg=PALETTE["card"], bd=0, highlightthickness=0)
        self.card.pack(padx=24, pady=24, fill="both")

        self.title_lbl = tk.Label(self.card, text="Шифр Частокол",
                                  bg=PALETTE["card"], fg=PALETTE["text"],
                                  font=("TkDefaultFont", 14, "bold"))
        self.title_lbl.pack(anchor="w", pady=(10,6), padx=16)

        self.body = tk.Frame(self.card, bg=PALETTE["card"]); self.body.pack(fill="both", expand=True)
        self.footer = tk.Frame(self.card, bg=PALETTE["card"]); self.footer.pack(fill="x", padx=16, pady=(8,16))

        self._show_form()

        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        xs = self.winfo_screenwidth() // 2 - w // 2
        ys = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"+{xs}+{ys}")

    def _get_current_alphabet(self):
        name = self.alphabet_name.get() if hasattr(self, "alphabet_name") else "LAT (A–Z, 26)"
        return ALPHABETS.get(name, ALPHABETS["LAT (A–Z, 26)"])

    def _filter_text_if_needed(self, text: str) -> str:
        if not self.only_letters.get():
            return text
        alpha = self._get_current_alphabet()
        allowed = set(alpha) | set([ch.lower() for ch in alpha])
        return "".join(ch for ch in text if ch in allowed)

    def _zigzag_rows(self, length: int, rails: int):

        if rails <= 1:
            return [0]*length
        row, step = 0, 1
        out = []
        for _ in range(length):
            out.append(row)
            if row == 0: step = 1
            elif row == rails-1: step = -1
            row += step
        return out

    def _rail_encrypt(self, text: str, rails: int) -> str:
        text2 = self._filter_text_if_needed(text)
        if rails <= 1: return text2
        rows = [""] * rails
        pattern = self._zigzag_rows(len(text2), rails)
        for ch, r in zip(text2, pattern):
            rows[r] += ch
        return "".join(rows)

    def _rail_decrypt(self, cipher: str, rails: int) -> str:
        msg_len = len(cipher)
        if rails <= 1 or msg_len == 0: return cipher
        pattern = self._zigzag_rows(msg_len, rails)

        counts = [0]*rails
        for r in pattern:
            counts[r] += 1

        rails_chunks = []
        i = 0
        for cnt in counts:
            rails_chunks.append(list(cipher[i:i+cnt]))
            i += cnt

        indexes = [0]*rails
        out_chars = []
        for r in pattern:
            out_chars.append(rails_chunks[r][indexes[r]])
            indexes[r] += 1
        return "".join(out_chars)

    def _clear_body(self):
        for w in self.body.winfo_children(): w.destroy()

    def _clear_footer(self):
        for w in self.footer.winfo_children(): w.destroy()

    def _stop_autoplay(self):
        try: self.autoplay.set(False)
        except Exception: pass
        if hasattr(self, "_after_id") and self._after_id:
            try: self.after_cancel(self._after_id)
            except Exception: pass
            self._after_id = None

    def _show_form(self):
        self.mode = "form"
        self._stop_autoplay()
        self._clear_body(); self._clear_footer()
        self.title_lbl.config(text="Шифр Частокол")

        row_alpha = tk.Frame(self.body, bg=PALETTE["card"]); row_alpha.pack(fill="x", padx=16, pady=(0,8))
        tk.Label(row_alpha, text="Алфавіт:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        box = ttk.Combobox(row_alpha, state="readonly", width=18,
                           values=list(ALPHABETS.keys()), textvariable=self.alphabet_name)
        box.pack(side="left", padx=(6,14))
        ttk.Checkbutton(row_alpha, text="Лише літери", variable=self.only_letters).pack(side="left")

        row_rails = tk.Frame(self.body, bg=PALETTE["card"]); row_rails.pack(fill="x", padx=16, pady=(0,8))
        tk.Label(row_rails, text="Кількість рейок:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        tk.Spinbox(row_rails, from_=2, to=10, textvariable=self.rails_var, width=4,
                   bg=PALETTE["panel"], fg=PALETTE["text"], insertbackground=PALETTE["text"]).pack(side="left", padx=(8,0))

        tk.Label(self.body, text="Вхідний текст", bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", padx=16)
        self.input_text = tk.Text(self.body, height=4, bg=PALETTE["panel"], fg=PALETTE["text"], insertbackground=PALETTE["text"])
        self.input_text.pack(fill="x", padx=16, pady=(2,8))

        actions = tk.Frame(self.body, bg=PALETTE["card"]); actions.pack(anchor="w", padx=16, pady=(6,6))
        tk.Button(actions, text="Зашифрувати", command=self.encrypt).pack(side="left", padx=(0,8))
        tk.Button(actions, text="Розшифрувати", command=self.decrypt).pack(side="left", padx=(0,8))
        tk.Button(actions, text="Очистити", command=self.clear).pack(side="left")

        tk.Label(self.body, text="Результат", bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", padx=16)
        self.output_text = tk.Text(self.body, height=4, bg=PALETTE["panel"], fg=PALETTE["text"])
        self.output_text.pack(fill="x", padx=16, pady=(2,0))

        ttk.Button(self.footer, text="Теорія", command=self._show_theory).pack(side="left")
        ttk.Button(self.footer, text="Перейти до демонстрації", command=self._show_demo).pack(side="left")
        ttk.Button(self.footer, text="Закрити", command=self.destroy).pack(side="right")

    def _show_theory(self):
        self.mode = "theory"
        self._stop_autoplay()
        self._clear_body(); self._clear_footer()
        self.title_lbl.config(text="Шифр Частокол — Теорія")

        wrapper = tk.Frame(self.body, bg=PALETTE["card"]); wrapper.pack(fill="both", expand=True, padx=16, pady=(4,0))
        yscroll = tk.Scrollbar(wrapper); yscroll.pack(side="right", fill="y")
        text = tk.Text(wrapper, wrap="word", height=18, bg=PALETTE["panel"], fg=PALETTE["text"],
                       insertbackground=PALETTE["text"], yscrollcommand=yscroll.set)
        text.pack(fill="both", expand=True); yscroll.config(command=text.yview)

        content = "Теоретичний матеріал не вказано."
        if self.theory_path:
            try:
                with open(self.theory_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                content = f"Не вдалося завантажити файл теорії ({self.theory_path}).\nПомилка: {e}"
        text.insert("1.0", content); text.config(state="disabled")

        ttk.Button(self.footer, text="Повернутися", command=self._show_form).pack(side="left")
        ttk.Button(self.footer, text="Закрити", command=self.destroy).pack(side="right")

    def _show_demo(self):
        self.mode = "demo"
        self._stop_autoplay()
        self._clear_body(); self._clear_footer()
        self.title_lbl.config(text="Шифр Частокол — Демонстрація")

        top = tk.Frame(self.body, bg=PALETTE["card"]); top.pack(fill="x", padx=16, pady=(0,8))
        tk.Label(top, text="Алфавіт:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        box = ttk.Combobox(top, state="readonly", width=18,
                           values=list(ALPHABETS.keys()), textvariable=self.alphabet_name)
        box.pack(side="left", padx=(6,14))

        ttk.Checkbutton(top, text="Лише літери", variable=self.only_letters, command=self._redraw_demo).pack(side="left")

        tk.Label(top, text="Рейки:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left", padx=(14,0))
        sp = tk.Spinbox(top, from_=2, to=10, textvariable=self.rails_var, width=4,
                        bg=PALETTE["panel"], fg=PALETTE["text"], insertbackground=PALETTE["text"],
                        command=self._redraw_demo)
        sp.pack(side="left", padx=(6,14))

        ttk.Checkbutton(top, text="Авто", variable=self.autoplay, command=self._toggle_autoplay).pack(side="left")

        inrow = tk.Frame(self.body, bg=PALETTE["card"]); inrow.pack(fill="x", padx=16, pady=(0,6))
        tk.Label(inrow, text="Текст для демонстрації:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        self.demo_input = tk.Entry(inrow, bg=PALETTE["panel"], fg=PALETTE["text"], width=48, insertbackground=PALETTE["text"])
        self.demo_input.pack(side="left", padx=(6,0), fill="x", expand=True)
        self.demo_input.insert(0, "DEFEND THE EAST WALL")  # можна змінити
        self.demo_input.bind("<KeyRelease>", lambda e: self._redraw_demo())

        self.canvas = tk.Canvas(self.body, bg=PALETTE["panel"], width=720, height=360, highlightthickness=0)
        self.canvas.pack(padx=16, pady=(4,8))

        ttk.Button(self.footer, text="Повернутися", command=self._show_form).pack(side="left")
        ttk.Button(self.footer, text="Закрити", command=self.destroy).pack(side="right")

        self._demo_index = 0
        self._redraw_demo()

    def _redraw_demo(self):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists():
            return
        self.canvas.delete("all")

        text_raw = self.demo_input.get()
        text2 = self._filter_text_if_needed(text_raw)
        rails = max(2, min(10, self.rails_var.get()))
        n = len(text2)

        W, H = 720, 360
        self.canvas.config(width=W, height=H)
        top_margin, left_margin, cell_w, cell_h = 30, 24, max(18, min(32, int((W-2*24)/max(1,n)))), 40
        for r in range(rails):
            y = top_margin + r*cell_h
            self.canvas.create_line(left_margin, y, left_margin + max(cell_w*n, 300), y, fill="#3a466b")

        pattern = self._zigzag_rows(n, rails)

        for i, ch in enumerate(text2):
            r = pattern[i]
            x = left_margin + i*cell_w
            y = top_margin + r*cell_h
            hl = (i == self._demo_index)
            bg = PALETTE["accent"] if hl else PALETTE["panel"]
            fg = "#0b1020" if hl else PALETTE["text"]
            self.canvas.create_rectangle(x-2, y-18, x+cell_w-6, y+18, outline="#3a466b", width=1, fill=bg)
            self.canvas.create_text(x+int((cell_w-6)/2), y, text=(ch if ch!=" " else "␣"), fill=fg)

        cipher = self._rail_encrypt(text2, rails)
        self.canvas.create_text(left_margin, top_margin-14, anchor="w",
                                text=f"C: {cipher}", fill=PALETTE["muted"])

        if self.autoplay.get() and n > 0:
            self._demo_index = (self._demo_index + 1) % n
            if self._after_id:
                try: self.after_cancel(self._after_id)
                except Exception: pass
            self._after_id = self.after(600, self._redraw_demo)

    def _toggle_autoplay(self):
        if self.autoplay.get():
            self._demo_index = 0
            self._redraw_demo()
        else:
            self._stop_autoplay()

    def encrypt(self):
        txt = self.input_text.get("1.0", "end-1c")
        rails = max(2, min(10, self.rails_var.get()))
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", self._rail_encrypt(txt, rails))

    def decrypt(self):
        txt = self.input_text.get("1.0", "end-1c")
        rails = max(2, min(10, self.rails_var.get()))
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", self._rail_decrypt(txt, rails))

    def clear(self):
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")

import tkinter as tk
from tkinter import ttk
from var import PALETTE, ALPHABETS


class VigenereWindow(tk.Toplevel):

    def __init__(self, master, theory_path=None):
        super().__init__(master)
        self.title("Шифр Віженера")
        self.configure(bg=PALETTE["bg2"])
        self.resizable(False, False)

        self.theory_path = theory_path
        self.mode = "form"

        self.alphabet_name = tk.StringVar(value="LAT (A–Z, 26)")
        self.key_var = tk.StringVar(value="")
        self.autoplay = tk.BooleanVar(value=False)
        self._after_id = None
        self._demo_index = 0

        self.card = tk.Frame(self, bg=PALETTE["card"], bd=0, highlightthickness=0)
        self.card.pack(padx=24, pady=24, fill="both")

        self.title_lbl = tk.Label(self.card, text="Шифр Віженера",
                                  bg=PALETTE["card"], fg=PALETTE["text"],
                                  font=("TkDefaultFont", 14, "bold"))
        self.title_lbl.pack(anchor="w", pady=(10,6), padx=16)

        self.body = tk.Frame(self.card, bg=PALETTE["card"])
        self.body.pack(fill="both", expand=True)

        self.footer = tk.Frame(self.card, bg=PALETTE["card"])
        self.footer.pack(fill="x", padx=16, pady=(8,16))

        self._show_form()

        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        xs = self.winfo_screenwidth() // 2 - w // 2
        ys = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"+{xs}+{ys}")

    def _get_current_alphabet(self):
        name = self.alphabet_name.get() if hasattr(self, "alphabet_name") else "LAT (A–Z, 26)"
        return ALPHABETS.get(name, ALPHABETS["LAT (A–Z, 26)"])

    def _normalize_key(self, key: str) -> str:
        alpha = self._get_current_alphabet()
        upper = set(alpha)
        lower = set([ch.lower() for ch in alpha])
        keep = []
        for ch in key:
            if ch in upper or ch in lower:
                keep.append(ch)
        return "".join(keep)

    def _vigenere(self, text: str, key: str, decrypt: bool = False) -> str:

        alpha = self._get_current_alphabet()
        n = len(alpha)
        if n == 0:
            return text
        key = self._normalize_key(key)
        if not key:
            return text

        upper = {ch: i for i, ch in enumerate(alpha)}
        lower = {ch.lower(): i for i, ch in enumerate(alpha)}

        shifts = []
        for ch in key:
            if ch in upper: shifts.append(upper[ch])
            elif ch in lower: shifts.append(lower[ch])
        if not shifts:
            return text

        out = []
        ki = 0
        for ch in text:
            if ch in upper:
                s = shifts[ki % len(shifts)]
                out_idx = (upper[ch] - s) % n if decrypt else (upper[ch] + s) % n
                out.append(alpha[out_idx])
                ki += 1
            elif ch in lower:
                s = shifts[ki % len(shifts)]
                out_idx = (lower[ch] - s) % n if decrypt else (lower[ch] + s) % n
                out.append(alpha[out_idx].lower())
                ki += 1
            else:
                out.append(ch)
        return "".join(out)

    def _clear_body(self):
        for w in self.body.winfo_children():
            w.destroy()

    def _clear_footer(self):
        for w in self.footer.winfo_children():
            w.destroy()

    def _stop_autoplay(self):
        if hasattr(self, "autoplay"):
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
        self.title_lbl.config(text="Шифр Віженера")

        row_alphabet = tk.Frame(self.body, bg=PALETTE["card"]); row_alphabet.pack(fill="x", padx=16, pady=(0,8))
        tk.Label(row_alphabet, text="Алфавіт:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        box = ttk.Combobox(row_alphabet, state="readonly", width=18,
                           values=list(ALPHABETS.keys()), textvariable=self.alphabet_name)
        box.pack(side="left", padx=(6,14))
        box.bind("<<ComboboxSelected>>", lambda e: None)

        tk.Label(self.body, text="Відкритий/шифр-текст", bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", padx=16)
        self.input_text = tk.Text(self.body, height=4, bg=PALETTE["panel"], fg=PALETTE["text"], insertbackground=PALETTE["text"])
        self.input_text.pack(fill="x", padx=16, pady=(2,8))

        key_row = tk.Frame(self.body, bg=PALETTE["card"]); key_row.pack(fill="x", padx=16, pady=(0,8))
        tk.Label(key_row, text="Ключ", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        tk.Entry(key_row, textvariable=self.key_var, width=24, bg=PALETTE["panel"], fg=PALETTE["text"]).pack(side="left", fill="x", expand=True, padx=(8,0))

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
        self.title_lbl.config(text="Шифр Віженера — Теорія")

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
        self.title_lbl.config(text="Шифр Віженера — Демонстрація")

        top = tk.Frame(self.body, bg=PALETTE["card"]); top.pack(fill="x", padx=16, pady=(0,8))

        tk.Label(top, text="Алфавіт:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        self.alpha_box = ttk.Combobox(top, state="readonly", width=18,
                                      values=list(ALPHABETS.keys()), textvariable=self.alphabet_name)
        self.alpha_box.pack(side="left", padx=(6,14))
        self.alpha_box.bind("<<ComboboxSelected>>", lambda e: self._redraw_demo())

        tk.Label(top, text="Ключ:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        key_entry = tk.Entry(top, textvariable=self.key_var, width=16, bg=PALETTE["panel"], fg=PALETTE["text"])
        key_entry.pack(side="left", padx=(6,14))
        key_entry.bind("<KeyRelease>", lambda e: self._redraw_demo())

        ttk.Checkbutton(top, text="Авто", variable=self.autoplay, command=self._toggle_autoplay).pack(side="left")

        self.demo_frame = tk.Frame(self.body, bg=PALETTE["card"]); self.demo_frame.pack(fill="both", expand=True, padx=16, pady=(4,8))
        self._build_demo_rows()

        ttk.Button(self.footer, text="Повернутися", command=self._show_form).pack(side="left")
        ttk.Button(self.footer, text="Закрити", command=self.destroy).pack(side="right")

        self._redraw_demo()

    def _build_demo_rows(self):
        self.row_plain = tk.Frame(self.demo_frame, bg=PALETTE["card"]); self.row_plain.pack(anchor="w")
        self.row_key   = tk.Frame(self.demo_frame, bg=PALETTE["card"]); self.row_key.pack(anchor="w")
        self.row_cipher= tk.Frame(self.demo_frame, bg=PALETTE["card"]); self.row_cipher.pack(anchor="w", pady=(0,6))

        tk.Label(self.row_plain, text="P: ", bg=PALETTE["card"], fg=PALETTE["muted"]).pack(side="left")
        tk.Label(self.row_key,   text="K: ", bg=PALETTE["card"], fg=PALETTE["muted"]).pack(side="left")
        tk.Label(self.row_cipher,text="C: ", bg=PALETTE["card"], fg=PALETTE["muted"]).pack(side="left")

        inrow = tk.Frame(self.demo_frame, bg=PALETTE["card"]); inrow.pack(fill="x", pady=(8,0))
        tk.Label(inrow, text="Текст для демонстрації:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        self.demo_input = tk.Entry(inrow, bg=PALETTE["panel"], fg=PALETTE["text"], width=48)
        self.demo_input.pack(side="left", padx=(6,0), fill="x", expand=True)
        self.demo_input.insert(0, "ATTACK AT DAWN" )
        self.demo_input.bind("<KeyRelease>", lambda e: self._redraw_demo())

    def _clear_demo_rows(self):
        for r in (self.row_plain, self.row_key, self.row_cipher):
            for w in r.winfo_children():
                if isinstance(w, tk.Label) and w.cget("text") in ("P: ", "K: ", "C: "):
                    continue
                w.destroy()

    def _make_cell(self, parent, text, highlight=False):
        bg = PALETTE["accent"] if highlight else PALETTE["panel"]
        fg = "#0b1020" if highlight else PALETTE["text"]
        lbl = tk.Label(parent, text=text, bg=bg, fg=fg, padx=6, pady=3)
        lbl.pack(side="left", padx=2, pady=2)

    def _redraw_demo(self):
        self._clear_demo_rows()
        alpha = self._get_current_alphabet()
        n = len(alpha)
        if n == 0:
            return
        txt = self.demo_input.get()
        key = self._normalize_key(self.key_var.get())
        if not key:
            key = "A"

        key_stream = []
        ki = 0
        for ch in txt:
            if ch.upper() in alpha or ch.lower() in [c.lower() for c in alpha]:
                key_stream.append(key[ki % len(key)])
                ki += 1
            else:
                key_stream.append(" ")

        ci = 0
        for i, ch in enumerate(txt):
            is_letter = (ch.upper() in alpha) or (ch.lower() in [c.lower() for c in alpha])
            kch = key_stream[i]
            highlight = is_letter and (ci == self._demo_index)
            self._make_cell(self.row_plain, ch if ch != " " else "␣", highlight=highlight)
            self._make_cell(self.row_key,   kch if kch != " " else " ", highlight=highlight)

            if is_letter:
                idx_key = (alpha.index(kch.upper()) if kch.upper() in alpha else alpha.index(kch.lower().upper()))
                idx_plain = alpha.index(ch.upper()) if ch.upper() in alpha else alpha.index(ch.lower().upper())
                idx_cipher = (idx_plain + idx_key) % n
                ch_out = alpha[idx_cipher]
                if ch.islower(): ch_out = ch_out.lower()
                self._make_cell(self.row_cipher, ch_out, highlight=highlight)
                ci += 1
            else:
                self._make_cell(self.row_cipher, ch if ch != " " else "␣", highlight=False)

        if self.autoplay.get():
            letters_count = sum(1 for ch in txt if (ch.upper() in alpha) or (ch.lower() in [c.lower() for c in alpha]))
            if letters_count == 0:
                self._demo_index = 0
            else:
                self._demo_index = (self._demo_index + 1) % letters_count
            if self._after_id:
                try: self.after_cancel(self._after_id)
                except Exception: pass
            self._after_id = self.after(700, self._redraw_demo)

    def _toggle_autoplay(self):
        if self.autoplay.get():
            self._demo_index = 0
            self._redraw_demo()
        else:
            if self._after_id:
                try: self.after_cancel(self._after_id)
                except Exception: pass
                self._after_id = None

    def encrypt(self):
        txt = self.input_text.get("1.0", "end-1c")
        key = self.key_var.get()
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", self._vigenere(txt, key, decrypt=False))

    def decrypt(self):
        txt = self.input_text.get("1.0", "end-1c")
        key = self.key_var.get()
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", self._vigenere(txt, key, decrypt=True))

    def clear(self):
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.key_var.set("")
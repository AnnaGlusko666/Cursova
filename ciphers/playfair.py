import tkinter as tk
from tkinter import ttk
from var import PALETTE


class PlayfairWindow(tk.Toplevel):

    def __init__(self, master, theory_path=None):
        super().__init__(master)
        self.title("Шифр Плейфера")
        self.configure(bg=PALETTE["bg2"])
        self.resizable(False, False)
        self.theory_path = theory_path

        self.alphabet_name = tk.StringVar(value="LAT 5×5 (I=J)")
        self.keyword_var   = tk.StringVar(value="")
        self.filler_lat = "X"
        self.filler_ukr = "Х"

        self.card = tk.Frame(self, bg=PALETTE["card"]); self.card.pack(padx=24, pady=24, fill="both")
        self.title_lbl = tk.Label(self.card, text="Шифр Плейфера — Форма",
                                  bg=PALETTE["card"], fg=PALETTE["text"],
                                  font=("TkDefaultFont", 14, "bold"))
        self.title_lbl.pack(anchor="w", pady=(8,6), padx=16)
        self.body   = tk.Frame(self.card, bg=PALETTE["card"]); self.body.pack(fill="both", expand=True)
        self.footer = tk.Frame(self.card, bg=PALETTE["card"]); self.footer.pack(fill="x", padx=16, pady=(8,16))

        self._show_form()

        self.update_idletasks()
        w,h = self.winfo_width(), self.winfo_height()
        xs,ys = self.winfo_screenwidth()//2 - w//2, self.winfo_screenheight()//2 - h//2
        self.geometry(f"+{xs}+{ys}")

    def _clear_body(self):
        for w in self.body.winfo_children(): w.destroy()

    def _clear_footer(self):
        for w in self.footer.winfo_children(): w.destroy()

    def _get_alphabet_spec(self):
        name = self.alphabet_name.get()
        if name.startswith("UKR"):
            ukr_letters = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
            extras = "., "
            return (ukr_letters + extras, 6, 6, self.filler_ukr)
        else:
            letters = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
            return (letters, 5, 5, self.filler_lat)

    def _normalize_text(self, text, for_ukr: bool):
        alpha, rows, cols, filler = self._get_alphabet_spec()
        alpha_set = set(alpha)
        res = []
        if for_ukr:
            t = text.upper()
        else:
            t = text.upper().replace("J", "I")
        for ch in t:
            if ch in alpha_set:
                res.append(ch)
        return "".join(res)

    def _build_square(self, keyword):
        alpha, rows, cols, filler = self._get_alphabet_spec()
        used = []
        seen = set()

        def push(ch):
            if ch not in seen and ch in alpha:
                seen.add(ch); used.append(ch)

        if self.alphabet_name.get().startswith("UKR"):
            kw = keyword.upper()
        else:
            kw = keyword.upper().replace("J", "I")
        for ch in kw:
            push(ch)
        for ch in alpha:
            push(ch)

        pos = {}
        for i, ch in enumerate(used):
            r, c = divmod(i, cols)
            pos[ch] = (r, c)

        return "".join(used), pos

    def _pairs(self, clean, filler):
        res = []
        i = 0
        while i < len(clean):
            a = clean[i]
            b = None
            if i+1 < len(clean):
                b = clean[i+1]
                if a == b:
                    b = filler
                    i += 1
                else:
                    i += 2
            else:
                b = filler
                i += 1
            res.append(a + b)
        return res

    def _enc_pair(self, p, square, pos, rows, cols):
        a, b = p[0], p[1]
        ra, ca = pos[a]; rb, cb = pos[b]
        if ra == rb:
            ca2 = (ca + 1) % cols
            cb2 = (cb + 1) % cols
            return square[ra*cols + ca2] + square[rb*cols + cb2]
        elif ca == cb:
            ra2 = (ra + 1) % rows
            rb2 = (rb + 1) % rows
            return square[ra2*cols + ca] + square[rb2*cols + cb]
        else:
            return square[ra*cols + cb] + square[rb*cols + ca]

    def _dec_pair(self, p, square, pos, rows, cols):
        a, b = p[0], p[1]
        ra, ca = pos[a]; rb, cb = pos[b]
        if ra == rb:
            ca2 = (ca - 1) % cols
            cb2 = (cb - 1) % cols
            return square[ra*cols + ca2] + square[rb*cols + cb2]
        elif ca == cb:
            ra2 = (ra - 1) % rows
            rb2 = (rb - 1) % rows
            return square[ra2*cols + ca] + square[rb2*cols + cb]
        else:
            return square[ra*cols + cb] + square[rb*cols + ca]

    def _show_form(self):
        self._clear_body(); self._clear_footer()
        self.title_lbl.config(text="Шифр Плейфера — Форма")

        top = tk.Frame(self.body, bg=PALETTE["card"]); top.pack(fill="x", padx=16, pady=(0,8))
        tk.Label(top, text="Алфавіт:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        box = ttk.Combobox(top, state="readonly", width=20,
                           values=["LAT 5×5 (I=J)", "UKR 6×6 (літери + . , пробіл)"],
                           textvariable=self.alphabet_name)
        box.pack(side="left", padx=(6,14))
        box.bind("<<ComboboxSelected>>", lambda e: self._render_square_preview())

        tk.Label(top, text="Ключове слово:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        entry_kw = tk.Entry(top, textvariable=self.keyword_var, bg=PALETTE["panel"], fg=PALETTE["text"])
        entry_kw.pack(side="left", padx=(6,14))
        entry_kw.bind("<KeyRelease>", lambda e: self._render_square_preview())

        self.square_preview = tk.Label(self.body, bg=PALETTE["card"], fg=PALETTE["muted"], justify="left")
        self.square_preview.pack(anchor="w", padx=16, pady=(4,6))
        self._render_square_preview()

        tk.Label(self.body, text="Вхідний текст", bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", padx=16)
        self.inp = tk.Text(self.body, height=4, bg=PALETTE["panel"], fg=PALETTE["text"], insertbackground=PALETTE["text"])
        self.inp.pack(fill="x", padx=16, pady=(2,8))

        actions = tk.Frame(self.body, bg=PALETTE["card"]); actions.pack(anchor="w", padx=16, pady=(4,6))
        ttk.Button(actions, text="Зашифрувати", command=self._encrypt).pack(side="left", padx=(0,8))
        ttk.Button(actions, text="Розшифрувати", command=self._decrypt).pack(side="left", padx=(0,8))
        ttk.Button(actions, text="Очистити",
                   command=lambda:(self.inp.delete("1.0","end"), self.out.delete("1.0","end"))).pack(side="left")

        tk.Label(self.body, text="Результат", bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", padx=16)
        self.out = tk.Text(self.body, height=4, bg=PALETTE["panel"], fg=PALETTE["text"])
        self.out.pack(fill="x", padx=16, pady=(2,0))

        ttk.Button(self.footer, text="Теорія", command=self._show_theory).pack(side="left")
        ttk.Button(self.footer, text="Перейти до демонстрації", command=self._show_demo).pack(side="left")
        ttk.Button(self.footer, text="Закрити", command=self.destroy).pack(side="right")

    def _render_square_preview(self):
        sq, pos = self._build_square(self.keyword_var.get())
        alpha, rows, cols, filler = self._get_alphabet_spec()
        lines = []
        for r in range(rows):
            line = " ".join(sq[r*cols:(r+1)*cols])
            lines.append(line)
        add = f"(філер: '{filler}')"
        self.square_preview.config(text="Таблиця:\n" + "\n".join(lines) + f"\n{add}")

    def _show_theory(self):
        self._clear_body(); self._clear_footer()
        self.title_lbl.config(text="Шифр Плейфера — Теорія")

        wrap = tk.Frame(self.body, bg=PALETTE["card"]); wrap.pack(fill="both", expand=True, padx=16, pady=(4,0))
        sb = tk.Scrollbar(wrap); sb.pack(side="right", fill="y")
        txt = tk.Text(wrap, wrap="word", yscrollcommand=sb.set,
                      bg=PALETTE["panel"], fg=PALETTE["text"], insertbackground=PALETTE["text"])
        txt.pack(fill="both", expand=True); sb.config(command=txt.yview)

        content = (
            "Шифр Плейфера — класичний біграмний шифр заміни. Ключове слово формує квадрат (5×5 або 6×6).\n"
            "Текст розбивається на пари символів. Для однакових символів у парі вставляється філер (наприклад, X/Х).\n"
            "Правила: (1) однаковий рядок — беремо праві сусідні; (2) однаковий стовпець — беремо нижні сусідні;\n"
            "(3) прямокутник — беремо символи на перетині того ж рядка/стовпця.\n"
            "Дешифрування виконується зворотними кроками."
        )
        try:
            if self.theory_path:
                with open(self.theory_path, "r", encoding="utf-8") as f:
                    content = f.read()
        except Exception as e:
            content += f"\n\n(Не вдалося прочитати файл: {e})"
        txt.insert("1.0", content); txt.config(state="disabled")

        ttk.Button(self.footer, text="Повернутися", command=self._show_form).pack(side="left")
        ttk.Button(self.footer, text="Закрити", command=self.destroy).pack(side="right")

    def _show_demo(self):
        self._clear_body(); self._clear_footer()
        self.title_lbl.config(text="Шифр Плейфера — Демонстрація")

        alpha, rows, cols, filler = self._get_alphabet_spec()
        sq, pos = self._build_square(self.keyword_var.get())

        frame = tk.Frame(self.body, bg=PALETTE["card"]); frame.pack(padx=16, pady=(0,8))
        cell = 46
        self.canvas = tk.Canvas(frame, width=cols*cell+2, height=rows*cell+2, bg=PALETTE["panel"], highlightthickness=0)
        self.canvas.pack()
        for r in range(rows):
            for c in range(cols):
                x0, y0 = c*cell+1, r*cell+1
                x1, y1 = x0+cell-2, y0+cell-2
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="#3a466b")
                ch = sq[r*cols + c]
                self.canvas.create_text(x0+cell/2-1, y0+cell/2-1, text=ch, fill=PALETTE["text"], font=("TkDefaultFont", 12, "bold"))

        io = tk.Frame(self.body, bg=PALETTE["card"]); io.pack(fill="x", padx=16, pady=(10,6))
        tk.Label(io, text="Текст:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        self.demo_text = tk.Entry(io, bg=PALETTE["panel"], fg=PALETTE["text"], width=40)
        self.demo_text.pack(side="left", padx=(6,10))
        ttk.Button(io, text="Показати біграми", command=self._demo_run).pack(side="left")

        self.demo_out = tk.Label(self.body, text="", bg=PALETTE["card"], fg=PALETTE["muted"], justify="left")
        self.demo_out.pack(anchor="w", padx=16, pady=(6,0))

        ttk.Button(self.footer, text="Повернутися", command=self._show_form).pack(side="left")
        ttk.Button(self.footer, text="Закрити", command=self.destroy).pack(side="right")

    def _demo_run(self):
        alpha, rows, cols, filler = self._get_alphabet_spec()
        sq, pos = self._build_square(self.keyword_var.get())
        for_ukr = self.alphabet_name.get().startswith("UKR")
        clean = self._normalize_text(self.demo_text.get(), for_ukr)
        pairs = self._pairs(clean, filler)
        enc_pairs = [self._enc_pair(p, sq, pos, rows, cols) for p in pairs]
        self.demo_out.config(text=f"Пари: {' '.join(pairs)}\nШифр: {' '.join(enc_pairs)}")

    def _encrypt(self):
        alpha, rows, cols, filler = self._get_alphabet_spec()
        sq, pos = self._build_square(self.keyword_var.get())
        for_ukr = self.alphabet_name.get().startswith("UKR")
        clean = self._normalize_text(self.inp.get("1.0","end-1c"), for_ukr)
        pairs = self._pairs(clean, filler)
        out = "".join(self._enc_pair(p, sq, pos, rows, cols) for p in pairs)
        self.out.delete("1.0","end"); self.out.insert("1.0", out)

    def _decrypt(self):
        alpha, rows, cols, filler = self._get_alphabet_spec()
        sq, pos = self._build_square(self.keyword_var.get())
        for_ukr = self.alphabet_name.get().startswith("UKR")
        clean = self._normalize_text(self.inp.get("1.0","end-1c"), for_ukr)
        if len(clean) % 2 == 1:
            clean += filler
        pairs = [clean[i:i+2] for i in range(0, len(clean), 2)]
        out = "".join(self._dec_pair(p, sq, pos, rows, cols) for p in pairs)
        self.out.delete("1.0","end"); self.out.insert("1.0", out)
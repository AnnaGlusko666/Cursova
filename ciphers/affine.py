import tkinter as tk
from tkinter import ttk
from var import PALETTE


class AffineWindow(tk.Toplevel):

    def __init__(self, master, theory_path=None):
        super().__init__(master)
        self.title("Афінний шифр")
        self.configure(bg=PALETTE["bg2"])
        self.resizable(False, False)
        self.theory_path = theory_path

        self.mode = "form"
        self.alphabet_name = tk.StringVar(value="LAT (A–Z, 26)")
        self.a_var = tk.IntVar(value=5)
        self.b_var = tk.IntVar(value=8)

        self.card = tk.Frame(self, bg=PALETTE["card"], bd=0, highlightthickness=0)
        self.card.pack(padx=24, pady=24, fill="both")
        self.title_lbl = tk.Label(self.card, text="Афінний шифр",
                                  bg=PALETTE["card"], fg=PALETTE["text"],
                                  font=("TkDefaultFont", 14, "bold"))
        self.title_lbl.pack(anchor="w", pady=(8,6), padx=16)
        self.body = tk.Frame(self.card, bg=PALETTE["card"]); self.body.pack(fill="both", expand=True)
        self.footer = tk.Frame(self.card, bg=PALETTE["card"]); self.footer.pack(fill="x", padx=16, pady=(8,16))

        self._show_form()

        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        xs = self.winfo_screenwidth()//2 - w//2
        ys = self.winfo_screenheight()//2 - h//2
        self.geometry(f"+{xs}+{ys}")

    def _clear_body(self):  [w.destroy() for w in self.body.winfo_children()]
    def _clear_footer(self):[w.destroy() for w in self.footer.winfo_children()]

    def _get_alpha(self):
        ALPHABETS = {
            "LAT (A–Z, 26)": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            "UKR (А–Я, 33)": list("АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"),
        }
        name = self.alphabet_name.get()
        return ALPHABETS[name] if name in ALPHABETS else ALPHABETS["LAT (A–Z, 26)"]

    @staticmethod
    def _egcd(a, b):
        if b == 0:
            return (a, 1, 0)
        g, x1, y1 = AffineWindow._egcd(b, a % b)
        return (g, y1, x1 - (a // b) * y1)

    @staticmethod
    def _modinv(a, m):
        g, x, _ = AffineWindow._egcd(a % m, m)
        if g != 1:
            return None
        return x % m

    @staticmethod
    def _gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    def _ensure_coprime(self):
        m = len(self._get_alpha())
        a = self.a_var.get() % m
        if self._gcd(a, m) == 1:
            self.a_var.set(a); return
        for delta in range(1, m):
            for cand in (a - delta, a + delta):
                if 1 <= cand < m and self._gcd(cand, m) == 1:
                    self.a_var.set(cand); return
        self.a_var.set(1)  # fallback

    def _show_form(self):
        self.mode = "form"
        self._clear_body(); self._clear_footer()
        self.title_lbl.config(text="Афінний шифр — Форма")

        top = tk.Frame(self.body, bg=PALETTE["card"]); top.pack(fill="x", padx=16, pady=(0,8))
        tk.Label(top, text="Алфавіт:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        box = ttk.Combobox(top, state="readonly", width=16,
                           values=["LAT (A–Z, 26)", "UKR (А–Я, 33)"], textvariable=self.alphabet_name)
        box.pack(side="left", padx=(6,14))
        box.bind("<<ComboboxSelected>>", lambda e: self._ensure_coprime())

        tk.Label(top, text="a:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        ttk.Spinbox(top, from_=1, to=50, width=4, textvariable=self.a_var,
                    command=self._ensure_coprime).pack(side="left", padx=(4,10))
        tk.Label(top, text="b:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        ttk.Spinbox(top, from_=0, to=50, width=4, textvariable=self.b_var).pack(side="left", padx=(4,0))
        ttk.Button(top, text="Автовиправити a", command=self._ensure_coprime).pack(side="left", padx=(10,0))

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

        self._ensure_coprime()

    def _show_theory(self):
        self.mode = "theory"
        self._clear_body(); self._clear_footer()
        self.title_lbl.config(text="Афінний шифр — Теорія")

        wrap = tk.Frame(self.body, bg=PALETTE["card"]); wrap.pack(fill="both", expand=True, padx=16, pady=(4,0))
        sb = tk.Scrollbar(wrap); sb.pack(side="right", fill="y")
        txt = tk.Text(wrap, wrap="word", yscrollcommand=sb.set,
                      bg=PALETTE["panel"], fg=PALETTE["text"], insertbackground=PALETTE["text"])
        txt.pack(fill="both", expand=True); sb.config(command=txt.yview)

        content = (
            "Афінний шифр виконує заміну символа x (його індексу в алфавіті) за формулою\n"
            "y = (a·x + b) mod m, де m — розмір алфавіту. Для можливості розшифрування\n"
            "коефіцієнт a має бути взаємно простим із m. Дешифрування: x = a^{-1}·(y - b) mod m."
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
        self.mode = "demo"
        self._clear_body();
        self._clear_footer()
        self.title_lbl.config(text="Афінний шифр — Діаграма відповідностей")

        top = tk.Frame(self.body, bg=PALETTE["card"]);
        top.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(top, text="Алфавіт:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        box = ttk.Combobox(top, state="readonly", width=16,
                           values=["LAT (A–Z, 26)", "UKR (А–Я, 33)"], textvariable=self.alphabet_name)
        box.pack(side="left", padx=(6, 14))
        box.bind("<<ComboboxSelected>>", lambda e: self._draw_chords())

        tk.Label(top, text="a:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        ttk.Spinbox(top, from_=1, to=50, width=4, textvariable=self.a_var,
                    command=lambda: (self._ensure_coprime(), self._draw_chords())).pack(side="left", padx=(4, 10))
        tk.Label(top, text="b:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        ttk.Spinbox(top, from_=0, to=50, width=4, textvariable=self.b_var,
                    command=self._draw_chords).pack(side="left", padx=(4, 14))

        self.show_all = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="Показати всі стрілки", variable=self.show_all,
                        command=self._draw_chords).pack(side="left")

        self.canvas = tk.Canvas(self.body, bg=PALETTE["panel"], width=700, height=520, highlightthickness=0)
        self.canvas.pack(padx=16, pady=(4, 8))
        self.canvas.bind("<Button-1>", self._on_click_chords)

        self.info_lbl = tk.Label(self.body, text="Клікни по літері, щоб підсвітити її образ.",
                                 bg=PALETTE["card"], fg=PALETTE["muted"])
        self.info_lbl.pack(anchor="w", padx=16)

        ttk.Button(self.footer, text="Повернутися", command=self._show_form).pack(side="left")
        ttk.Button(self.footer, text="Закрити", command=self.destroy).pack(side="right")

        self._ensure_coprime()
        self._draw_chords()

    def _draw_chords(self, highlight_idx=None):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists(): return
        self.canvas.delete("all")

        import math
        alpha = self._get_alpha();
        m = len(alpha)
        a = self.a_var.get() % m;
        b = self.b_var.get() % m

        cx, cy = 350, 280
        r = 210

        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#3a466b")

        self.positions = {}
        for i, ch in enumerate(alpha):
            ang = 2 * math.pi * i / m - math.pi / 2
            x = cx + r * math.cos(ang);
            y = cy + r * math.sin(ang)
            self.positions[i] = (x, y)
            self.canvas.create_text(x, y, text=ch, fill=PALETTE["text"])

        def j_of(i):
            return (a * i + b) % m

        if getattr(self, "show_all", None) and self.show_all.get():
            for i in range(m):
                j = j_of(i)
                x1, y1 = self.positions[i];
                x2, y2 = self.positions[j]
                self.canvas.create_line(x1, y1, x2, y2, fill="#495780")

        if highlight_idx is not None:
            i = highlight_idx;
            j = j_of(i)
            x1, y1 = self.positions[i];
            x2, y2 = self.positions[j]
            self.canvas.create_line(x1, y1, x2, y2, fill=PALETTE["accent"], width=3, arrow=tk.LAST)
            self.canvas.create_oval(x1 - 6, y1 - 6, x1 + 6, y1 + 6, outline=PALETTE["accent"])
            self.canvas.create_oval(x2 - 6, y2 - 6, x2 + 6, y2 + 6, outline=PALETTE["accent"])
            self.info_lbl.config(
                text=f"{alpha[i]}  →  {alpha[j]}   (i={i}, j=(a·i+b) mod {m} = ({a}·{i}+{b}) mod {m} = {j})")
        else:
            self.info_lbl.config(text="Клікни по літері, щоб підсвітити її образ.")

    def _on_click_chords(self, e):
        if not hasattr(self, "positions"): return
        best, idx = 1e9, None
        for i, (x, y) in self.positions.items():
            d = (x - e.x) ** 2 + (y - e.y) ** 2
            if d < best:
                best, idx = d, i
        self._draw_chords(highlight_idx=idx)

    def _draw_chords(self, highlight_idx=None):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists(): return
        self.canvas.delete("all")

        import math
        alpha = self._get_alpha();
        m = len(alpha)
        a = self.a_var.get() % m;
        b = self.b_var.get() % m

        cx, cy = 350, 280
        r = 210

        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#3a466b")

        self.positions = {}
        for i, ch in enumerate(alpha):
            ang = 2 * math.pi * i / m - math.pi / 2
            x = cx + r * math.cos(ang);
            y = cy + r * math.sin(ang)
            self.positions[i] = (x, y)
            self.canvas.create_text(x, y, text=ch, fill=PALETTE["text"])

        def j_of(i):
            return (a * i + b) % m

        if self.show_all.get():
            for i in range(m):
                j = j_of(i)
                x1, y1 = self.positions[i];
                x2, y2 = self.positions[j]
                self.canvas.create_line(x1, y1, x2, y2, fill="#495780")

        if highlight_idx is not None:
            i = highlight_idx;
            j = j_of(i)
            x1, y1 = self.positions[i];
            x2, y2 = self.positions[j]
            self.canvas.create_line(x1, y1, x2, y2, fill=PALETTE["accent"], width=3, arrow=tk.LAST)
            self.canvas.create_oval(x1 - 6, y1 - 6, x1 + 6, y1 + 6, outline=PALETTE["accent"])
            self.canvas.create_oval(x2 - 6, y2 - 6, x2 + 6, y2 + 6, outline=PALETTE["accent"])
            self.info_lbl.config(
                text=f"{alpha[i]}  →  {alpha[j]}   (i={i}, j=(a·i+b) mod m = ({a}·{i}+{b}) mod {m} = {j})")
        else:
            self.info_lbl.config(text="Клікни по літері, щоб підсвітити її образ.")

    def _on_click_chords(self, e):
        if not hasattr(self, "positions"): return
        best, idx = 1e9, None
        for i, (x, y) in self.positions.items():
            d = (x - e.x) ** 2 + (y - e.y) ** 2
            if d < best:
                best, idx = d, i
        self._draw_chords(highlight_idx=idx)

    def _redraw(self):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists(): return
        self.canvas.delete("all")
        import math
        alpha = self._get_alpha(); m = len(alpha)
        a = self.a_var.get() % m; b = self.b_var.get() % m

        cx, cy = 320, 210; rO, rI = 170, 130
        self.canvas.create_oval(cx-rO, cy-rO, cx+rO, cy+rO, outline="#3a466b")
        self.canvas.create_oval(cx-rI, cy-rI, cx+rI, cy+rI, outline="#3a466b")

        self.pos_outer = {}; self.pos_inner = {}
        for i, ch in enumerate(alpha):
            ang = 2*math.pi*i/m - math.pi/2
            x = cx + rO*math.cos(ang); y = cy + rO*math.sin(ang)
            self.pos_outer[ch] = (x, y)
            self.canvas.create_text(x, y, text=ch, fill=PALETTE["text"])
        for i, ch in enumerate(alpha):
            j = (a*i + b) % m
            ang = 2*math.pi*j/m - math.pi/2
            x = cx + rI*math.cos(ang); y = cy + rI*math.sin(ang)
            self.pos_inner[ch] = (x, y)
            self.canvas.create_text(x, y, text=ch, fill=PALETTE["muted"])

    def _on_click(self, e):
        if not hasattr(self, "pos_outer"): return
        best, letter = 1e9, None
        for ch, (x,y) in self.pos_outer.items():
            d = (x-e.x)**2 + (y-e.y)**2
            if d < best: best, letter = d, ch
        if letter is None: return
        self._redraw()
        x1,y1 = self.pos_outer[letter]; x2,y2 = self.pos_inner[letter]
        self.canvas.create_line(x1,y1,x2,y2, fill=PALETTE["accent"], width=2)
        self.canvas.create_oval(x1-6,y1-6,x1+6,y1+6, outline=PALETTE["accent"])
        self.canvas.create_oval(x2-6,y2-6,x2+6,y2+6, outline=PALETTE["accent"])

    def _map_indices(self, a, b, m):
        return {i: (a*i + b) % m for i in range(m)}

    def _encrypt(self):
        alpha = self._get_alpha();
        m = len(alpha)
        self._ensure_coprime()
        a = self.a_var.get() % m
        b = self.b_var.get() % m

        idx = {ch: i for i, ch in enumerate(alpha)}
        mp = {i: (a * i + b) % m for i in range(m)}

        a_mod10 = self.a_var.get() % 10
        b_mod10 = self.b_var.get() % 10

        s = self.inp.get("1.0", "end-1c")
        out = []
        for ch in s:
            up = ch.upper()

            if up in idx:
                y = mp[idx[up]]
                enc = alpha[y]
                out.append(enc.lower() if ch.islower() else enc.upper())
                continue

            if ch.isdigit():
                x = int(ch)
                y = (a_mod10 * x + b_mod10) % 10
                out.append(str(y))
                continue

            out.append(ch)

        self.out.delete("1.0", "end")
        self.out.insert("1.0", "".join(out))

    def _decrypt(self):
        alpha = self._get_alpha();
        m = len(alpha)
        self._ensure_coprime()
        a = self.a_var.get() % m
        b = self.b_var.get() % m

        a_inv = self._modinv(a, m)
        if a_inv is None:
            self.out.delete("1.0", "end")
            self.out.insert("1.0", "Помилка: a не взаємно просте з m")
            return

        idx = {ch: i for i, ch in enumerate(alpha)}

        a_mod10 = self.a_var.get() % 10
        b_mod10 = self.b_var.get() % 10
        a10_inv = self._modinv(a_mod10, 10)

        s = self.inp.get("1.0", "end-1c")
        out = []
        for ch in s:
            up = ch.upper()

            if up in idx:
                y = idx[up]
                x = (a_inv * (y - b)) % m
                dec = alpha[x]
                out.append(dec.lower() if ch.islower() else dec.upper())
                continue

            if ch.isdigit():
                if a10_inv is not None:
                    y = int(ch)
                    x = (a10_inv * (y - b_mod10)) % 10
                    out.append(str(x))
                else:
                    out.append(ch)
                continue

            out.append(ch)

        self.out.delete("1.0", "end")
        self.out.insert("1.0", "".join(out))
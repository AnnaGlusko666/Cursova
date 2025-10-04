import tkinter as tk
from tkinter import ttk
from var import PALETTE, ALPHABETS
import random
import math


class AlbertiWindow(tk.Toplevel):

    def __init__(self, master, theory_path=None):
        super().__init__(master)
        self.title("Шифр Альберті")
        self.configure(bg=PALETTE["bg2"])
        self.resizable(False, False)
        self._inner_key = None
        self.inner_map = {}

        self.theory_path = theory_path
        self.mode = "form"

        self.index_mark = 'a'
        self.current_inner = []
        self.index_at = 'A'

        self.alphabet_name = tk.StringVar(value="LAT (A–Z, 26)")
        self.shift_var = tk.IntVar(value=0)
        self.only_letters = tk.BooleanVar(value=False)
        self.autoplay = tk.BooleanVar(value=False)
        self._after_id = None

        self.card = tk.Frame(self, bg=PALETTE["card"])
        self.card.pack(padx=24, pady=24, fill="both")
        self.title_lbl = tk.Label(self.card, text="Шифр Альберті",
                                  bg=PALETTE["card"], fg=PALETTE["text"],
                                  font=("TkDefaultFont", 14, "bold"))
        self.title_lbl.pack(anchor="w", pady=(10,6), padx=16)
        self.body = tk.Frame(self.card, bg=PALETTE["card"]); self.body.pack(fill="both", expand=True)
        self.footer = tk.Frame(self.card, bg=PALETTE["card"]); self.footer.pack(fill="x", padx=16, pady=(8,16))
        self._init_inner_alpha()

        self._show_form()
        self.update_idletasks()
        w,h=self.winfo_width(),self.winfo_height()
        self.geometry(f"+{self.winfo_screenwidth()//2-w//2}+{self.winfo_screenheight()//2-h//2}")

    def _get_alpha(self):
        name = self.alphabet_name.get()
        return ALPHABETS[name] if name in ALPHABETS else ALPHABETS["LAT (A–Z, 26)"]

    def _ensure_inner_sync(self):
        outer = tuple(self._get_alpha())
        if self._inner_key != outer:
            self._init_inner_alpha(reset_cache=False)
            self._rotate_to_index(self.index_at)

    def _init_inner_alpha(self, reset_cache: bool = False):
        outer = tuple(self._get_alpha())
        if reset_cache:
            self.inner_map = {}
        if outer not in self.inner_map:
            inner = list(outer)
            random.shuffle(inner)
            self.inner_map[outer] = inner
        self.current_inner = list(self.inner_map[outer])
        self._inner_key = outer

    def _rotate_to_index(self, outer_letter: str):
        outer = self._get_alpha()
        if not outer_letter or outer_letter.upper() not in outer:
            return
        self.index_at = outer_letter.upper()

        n = len(self.current_inner)
        if n == 0:
            return

        inner_up = [c.upper() for c in self.current_inner]
        mark = (getattr(self, "index_mark", "a") or "a").upper()
        p = inner_up.index(mark) if mark in inner_up else 0
        q = outer.index(self.index_at)

        r = (q - p) % n
        if r:
            self.current_inner = self.current_inner[-r:] + self.current_inner[:-r]

        if hasattr(self, "index_choice") and self.index_choice.winfo_exists():
            try:
                self.index_choice.set(self.index_at)
            except Exception:
                pass

    def _filter_text(self, txt):
        if not self.only_letters.get():
            return txt
        alpha = self._get_alpha()
        allowed = set(alpha) | {c.lower() for c in alpha}
        return "".join(c if c in allowed else " " for c in txt)

    def _alberti_encrypt(self, text,k):
        a=self._get_alpha()
        return "".join(a[(a.index(ch.upper())+k)%len(a)] if ch.upper() in a else ch for ch in text)

    def _alberti_decrypt(self, text,k):
        a=self._get_alpha()
        return "".join(a[(a.index(ch.upper())-k)%len(a)] if ch.upper() in a else ch for ch in text)

    def _clear_body(self): [w.destroy() for w in self.body.winfo_children()]
    def _clear_footer(self): [w.destroy() for w in self.footer.winfo_children()]
    def _stop_auto(self):
        if self._after_id:
            try: self.after_cancel(self._after_id)
            except: pass
            self._after_id=None

    def _show_form(self):
        self.mode="form"; self._stop_auto(); self._clear_body(); self._clear_footer()
        self.title_lbl.config(text="Шифр Альберті")

        row=tk.Frame(self.body,bg=PALETTE["card"]);row.pack(fill="x",padx=16,pady=(0,8))
        tk.Label(row,text="Алфавіт:",bg=PALETTE["card"],fg=PALETTE["text"]).pack(side="left")
        ttk.Combobox(row,state="readonly",width=18,values=list(ALPHABETS.keys()),textvariable=self.alphabet_name).pack(side="left",padx=(6,14))
        ttk.Checkbutton(row,text="Лише літери",variable=self.only_letters).pack(side="left")

        tk.Label(self.body,text="Зсув k:",bg=PALETTE["card"],fg=PALETTE["text"]).pack(anchor="w",padx=16)
        tk.Spinbox(self.body,from_=0,to=50,textvariable=self.shift_var,width=4,bg=PALETTE["panel"],fg=PALETTE["text"]).pack(anchor="w",padx=16)

        tk.Label(self.body,text="Вхідний текст",bg=PALETTE["card"],fg=PALETTE["text"]).pack(anchor="w",padx=16)
        self.inp=tk.Text(self.body,height=4,bg=PALETTE["panel"],fg=PALETTE["text"])
        self.inp.pack(fill="x",padx=16,pady=2)

        btns=tk.Frame(self.body,bg=PALETTE["card"]);btns.pack(anchor="w",padx=16,pady=6)
        tk.Button(btns,text="Зашифрувати",command=self.encrypt).pack(side="left",padx=4)
        tk.Button(btns,text="Розшифрувати",command=self.decrypt).pack(side="left",padx=4)
        tk.Button(btns,text="Очистити",command=self.clear).pack(side="left",padx=4)

        tk.Label(self.body,text="Результат",bg=PALETTE["card"],fg=PALETTE["text"]).pack(anchor="w",padx=16)
        self.out=tk.Text(self.body,height=4,bg=PALETTE["panel"],fg=PALETTE["text"])
        self.out.pack(fill="x",padx=16,pady=(2,0))

        ttk.Button(self.footer,text="Теорія",command=self._show_theory).pack(side="left")
        ttk.Button(self.footer,text="Перейти до демонстрації",command=self._show_demo).pack(side="left")
        ttk.Button(self.footer,text="Закрити",command=self.destroy).pack(side="right")

    def _show_theory(self):
        self.mode="theory"; self._stop_auto(); self._clear_body(); self._clear_footer()
        self.title_lbl.config(text="Шифр Альберті — Теорія")
        wrap=tk.Frame(self.body,bg=PALETTE["card"]);wrap.pack(fill="both",expand=True,padx=16,pady=4)
        s=tk.Scrollbar(wrap);s.pack(side="right",fill="y")
        t=tk.Text(wrap,wrap="word",bg=PALETTE["panel"],fg=PALETTE["text"],yscrollcommand=s.set)
        t.pack(fill="both",expand=True);s.config(command=t.yview)
        content="Теорія недоступна"
        if self.theory_path:
            try:
                content = open(self.theory_path, encoding="utf-8").read()
            except Exception as e:
                content = f"Помилка: {e}"
        t.insert("1.0",content);t.config(state="disabled")
        ttk.Button(self.footer,text="Повернутися",command=self._show_form).pack(side="left")
        ttk.Button(self.footer,text="Закрити",command=self.destroy).pack(side="right")

    def _show_demo(self):
        self.mode = "demo";
        self._stop_auto();
        self._clear_body();
        self._clear_footer()
        self.title_lbl.config(text="Шифр Альберті — Демонстрація")

        top = tk.Frame(self.body, bg=PALETTE["card"]);
        top.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(top, text="Алфавіт:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        box = ttk.Combobox(top, state="readonly", width=18,
                           values=list(ALPHABETS.keys()), textvariable=self.alphabet_name)
        box.pack(side="left", padx=(6, 14))
        box.bind("<<ComboboxSelected>>",
                 lambda e: (self._init_inner_alpha(reset_cache=True),
                            self._rotate_to_index(self.index_at),
                            self._redraw_demo()))

        tk.Label(top, text="Індекс-літера (зовнішній диск):", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        self.index_choice = ttk.Combobox(top, state="readonly", width=4, values=self._get_alpha())
        self.index_choice.pack(side="left", padx=(6, 14))
        self.index_choice.set(self.index_at)
        self.index_choice.bind("<<ComboboxSelected>>",
                               lambda e: (self._rotate_to_index(self.index_choice.get()),
                                          self._redraw_demo()))

        ttk.Button(top, text="Перевстановити індекс",
                   command=lambda: self._rotate_to_index(self.index_choice.get())).pack(side="left")

        ttk.Checkbutton(top, text="Авто", variable=self.autoplay, command=self._toggle_auto).pack(side="right")

        row = tk.Frame(self.body, bg=PALETTE["card"]);
        row.pack(fill="x", padx=16, pady=(0, 6))
        tk.Label(row, text="Текст (великі літери = сигнал ре-індексації):", bg=PALETTE["card"],
                 fg=PALETTE["text"]).pack(side="left")
        self.demo_in = tk.Entry(row, bg=PALETTE["panel"], fg=PALETTE["text"], insertbackground=PALETTE["text"])
        self.demo_in.pack(side="left", padx=(6, 0), fill="x", expand=True)
        self.demo_in.insert(0, "ATTACK! REINDEX AT D")  # приклад
        self.demo_in.bind("<KeyRelease>", lambda e: self._redraw_demo())

        self.canvas = tk.Canvas(self.body, bg=PALETTE["panel"], width=640, height=420, highlightthickness=0)
        self.canvas.pack(padx=16, pady=(4, 8))
        self.canvas.bind("<Button-1>", lambda e: None)

        ttk.Button(self.footer, text="Повернутися", command=self._show_form).pack(side="left")
        ttk.Button(self.footer, text="Закрити", command=self.destroy).pack(side="right")

        self._redraw_demo()

    def _redraw_demo(self):
        self._ensure_inner_sync()
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists(): return
        self.canvas.delete("all")

        outer = self._get_alpha()
        inner = self.current_inner[:]
        n = len(outer)
        cx, cy = 320, 210
        r_outer, r_inner = 170, 130

        self.canvas.create_oval(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer, outline="#3a466b")
        self.canvas.create_oval(cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner, outline="#3a466b")

        pos_outer, pos_inner = {}, {}
        for i, ch in enumerate(outer):
            ang = 2 * math.pi * i / n - math.pi / 2
            x = cx + r_outer * math.cos(ang);
            y = cy + r_outer * math.sin(ang)
            pos_outer[ch] = (x, y)
            self.canvas.create_text(x, y, text=ch, fill=PALETTE["text"])

        for i, ch in enumerate(inner):
            ang = 2 * math.pi * i / n - math.pi / 2
            x = cx + r_inner * math.cos(ang);
            y = cy + r_inner * math.sin(ang)
            pos_inner[ch.upper()] = (x, y)
            self.canvas.create_text(x, y, text=ch.lower(), fill=PALETTE["muted"])

        x1, y1 = pos_outer.get(self.index_at, (cx, cy - r_outer))
        self.canvas.create_line(x1, y1, cx, cy, fill=PALETTE["accent"])

        text = self.demo_in.get()
        out = []
        for ch in text:
            if ch.upper() in outer and ch.isupper():
                self._rotate_to_index(ch.upper())
                outer = self._get_alpha()
                inner = self.current_inner[:]
                self.canvas.delete("all")
                self.canvas.create_oval(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer, outline="#3a466b")
                self.canvas.create_oval(cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner, outline="#3a466b")
                pos_outer, pos_inner = {}, {}
                for i, c2 in enumerate(outer):
                    ang = 2 * math.pi * i / n - math.pi / 2
                    x = cx + r_outer * math.cos(ang);
                    y = cy + r_outer * math.sin(ang)
                    pos_outer[c2] = (x, y);
                    self.canvas.create_text(x, y, text=c2, fill=PALETTE["text"])
                for i, c2 in enumerate(inner):
                    ang = 2 * math.pi * i / n - math.pi / 2
                    x = cx + r_inner * math.cos(ang);
                    y = cy + r_inner * math.sin(ang)
                    pos_inner[c2.upper()] = (x, y);
                    self.canvas.create_text(x, y, text=c2.lower(), fill=PALETTE["muted"])
                x1, y1 = pos_outer.get(self.index_at, (cx, cy - r_outer))
                self.canvas.create_line(x1, y1, cx, cy, fill=PALETTE["accent"])
                out.append(" ")
                continue

            if ch.upper() in outer:
                i = outer.index(ch.upper())
                enc = inner[i]
                enc = enc.lower() if ch.islower() else enc.upper()
                out.append(enc)
                xo, yo = pos_outer[ch.upper()]
                xi, yi = pos_inner[enc.upper()]
                self.canvas.create_line(xo, yo, xi, yi, fill=PALETTE["accent"])
                self.canvas.create_oval(xo - 6, yo - 6, xo + 6, yo + 6, outline=PALETTE["accent"])
                self.canvas.create_oval(xi - 6, yi - 6, xi + 6, yi + 6, outline=PALETTE["accent"])
            else:
                out.append(ch)

        self.canvas.create_text(24, 20, anchor="w", text="C: " + "".join(out), fill=PALETTE["muted"])

    def _toggle_auto(self):
        if self.autoplay.get(): self._redraw_demo()
        else: self._stop_auto()

    def encrypt(self):
        self._ensure_inner_sync()
        text = self.inp.get("1.0", "end-1c")
        outer = self._get_alpha()
        inner = self.current_inner[:]
        res = []
        for ch in text:
            up = ch.upper()
            if up in outer:
                i = outer.index(up)
                enc = inner[i]
                res.append(enc.lower() if ch.islower() else enc.upper())
            else:
                res.append(ch)
        self.out.delete("1.0", "end")
        self.out.insert("1.0", "".join(res))

    def decrypt(self):
        self._ensure_inner_sync()
        text = self.inp.get("1.0", "end-1c")
        outer = self._get_alpha()
        inner = self.current_inner[:]
        res = []
        inner_up = [c.upper() for c in inner]
        for ch in text:
            up = ch.upper()
            if up in inner_up:
                i = inner_up.index(up)
                dec = outer[i]
                res.append(dec.lower() if ch.islower() else dec.upper())
            else:
                res.append(ch)
        self.out.delete("1.0", "end")
        self.out.insert("1.0", "".join(res))

    def clear(self):
        self.inp.delete("1.0","end")
        self.out.delete("1.0","end")

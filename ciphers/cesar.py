import tkinter as tk
from tkinter import ttk
from var import PALETTE, ALPHABETS
import math


class CaesarWindow(tk.Toplevel):

    def __init__(self, master, theory_path=None):
        super().__init__(master)
        self.title("Шифр Цезаря")
        self.configure(bg=PALETTE["bg2"])
        self.theory_path = theory_path
        self.resizable(False, False)

        self.mode = "form"
        self.alphabet_name = tk.StringVar(value="LAT (A–Z, 26)")
        self.shift_var = tk.IntVar(value=3)
        self.autoplay = tk.BooleanVar(value=False)
        self._after_id = None

        self.card = tk.Frame(self, bg=PALETTE["card"], bd=0, highlightthickness=0)
        self.card.pack(padx=24, pady=24, fill="both")

        self.title_lbl = tk.Label(self.card, text="Шифр Цезаря",
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

    def _show_form(self):
        self.mode = "form"
        self._stop_autoplay()
        self._clear_body(); self._clear_footer()
        self.title_lbl.config(text="Шифр Цезаря")

        row_alphabet = tk.Frame(self.body, bg=PALETTE["card"])
        row_alphabet.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(row_alphabet, text="Алфавіт:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        box = ttk.Combobox(row_alphabet, state="readonly", width=18,
                           values=list(ALPHABETS.keys()), textvariable=self.alphabet_name)
        box.pack(side="left", padx=(6, 14))
        box.bind("<<ComboboxSelected>>", self._on_alphabet_change)

        tk.Label(self.body, text="Відкритий текст", bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", padx=16)
        self.input_text = tk.Text(self.body, height=4, bg=PALETTE["panel"], fg=PALETTE["text"], insertbackground=PALETTE["text"])
        self.input_text.pack(fill="x", padx=16, pady=(2,8))

        row = tk.Frame(self.body, bg=PALETTE["card"]); row.pack(fill="x", padx=16, pady=(0,8))
        tk.Label(row, text="Зсув (k)", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        tk.Scale(row, from_=0, to=33, orient="horizontal", variable=self.shift_var,
                 bg=PALETTE["card"], fg=PALETTE["text"], highlightthickness=0).pack(side="left", fill="x", expand=True, padx=10)
        tk.Entry(row, textvariable=self.shift_var, width=4, bg=PALETTE["panel"], fg=PALETTE["text"]).pack(side="left")

        actions = tk.Frame(self.body, bg=PALETTE["card"]); actions.pack(anchor="w", padx=16, pady=(6,6))
        tk.Button(actions, text="Зашифрувати", command=self.encrypt).pack(side="left", padx=(0,8))
        tk.Button(actions, text="Розшифрувати", command=self.decrypt).pack(side="left", padx=(0,8))
        tk.Button(actions, text="Очистити", command=self.clear).pack(side="left")

        tk.Label(self.body, text="Результат", bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", padx=16)
        self.output_text = tk.Text(self.body, height=4, bg=PALETTE["panel"], fg=PALETTE["text"])
        self.output_text.pack(fill="x", padx=16, pady=(2,0))

        ttk.Button(self.footer, text="Теорія", command=self._show_theory).pack(side="left")
        ttk.Button(self.footer, text="Перейти до демонстрації", command=self._show_demo).pack(side="left")
        ttk.Button(self.footer, text="Закрити", command=self.destroy).pack(side="right", padx=(8,0))

    def _show_theory(self):
        self.mode = "theory"
        self._clear_body()
        self._clear_footer()
        self.title_lbl.config(text="Шифр Цезаря — Теорія")

        wrapper = tk.Frame(self.body, bg=PALETTE["card"])
        wrapper.pack(fill="both", expand=True, padx=16, pady=(4, 0))

        yscroll = tk.Scrollbar(wrapper)
        yscroll.pack(side="right", fill="y")

        text = tk.Text(
            wrapper, wrap="word", height=18,
            bg=PALETTE["panel"], fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            yscrollcommand=yscroll.set
        )
        text.pack(fill="both", expand=True)
        yscroll.config(command=text.yview)

        content = "Теоретичний матеріал не вказано."
        if hasattr(self, "theory_path") and self.theory_path:
            try:
                with open(self.theory_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                content = f"Не вдалося завантажити файл теорії ({self.theory_path}).\nПомилка: {e}"
        text.insert("1.0", content)
        text.config(state="disabled")

        ttk.Button(self.footer, text="Повернутися", command=self._show_form).pack(side="left")
        ttk.Button(self.footer, text="Закрити", command=self.destroy).pack(side="right")

    def _show_demo(self):
        self.mode = "demo"
        if hasattr(self, "_after_id") and self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

        if not hasattr(self, "alphabet_name"):
            self.alphabet_name = tk.StringVar(value="LAT (A–Z, 26)")
        if not hasattr(self, "shift_var"):
            self.shift_var = tk.IntVar(value=3)
        if not hasattr(self, "autoplay"):
            self.autoplay = tk.BooleanVar(value=False)

        self._clear_body();
        self._clear_footer()
        self.title_lbl.config(text="Шифр Цезаря — Демонстрація")

        top = tk.Frame(self.body, bg=PALETTE["card"]);
        top.pack(fill="x", padx=16, pady=(0, 8))

        tk.Label(top, text="Алфавіт:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        self.alphabet_box = ttk.Combobox(
            top, state="readonly",
            values=list(ALPHABETS.keys()),
            textvariable=self.alphabet_name, width=18
        )
        self.alphabet_box.pack(side="left", padx=(6, 14))
        self.alphabet_box.bind("<<ComboboxSelected>>", self._on_alphabet_change)

        tk.Label(top, text="Зсув k:", bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        self._demo_scale = tk.Scale(
            top, from_=0, to=len(self._get_current_alphabet()) - 1,
            orient="horizontal", variable=self.shift_var,
            bg=PALETTE["card"], fg=PALETTE["text"], highlightthickness=0,
            command=lambda _=None: self._redraw()
        )
        self._demo_scale.pack(side="left", fill="x", expand=True, padx=(6, 6))

        tk.Entry(top, textvariable=self.shift_var, width=4, bg=PALETTE["panel"], fg=PALETTE["text"]).pack(side="left",
                                                                                                          padx=(0, 8))

        ttk.Checkbutton(top, text="Автообертання", variable=self.autoplay, command=self._toggle_autoplay).pack(
            side="left")

        self.canvas = tk.Canvas(self.body, bg=PALETTE["panel"], width=640, height=420, highlightthickness=0)
        self.canvas.pack(padx=16, pady=(4, 8))
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        tk.Label(
            self.body,
            text="Натисни на літеру зовнішнього диска — побачиш відповідну літеру на внутрішньому при вибраному зсуві k.",
            bg=PALETTE["card"], fg=PALETTE["muted"], wraplength=640, justify="left"
        ).pack(anchor="w", padx=16)

        ttk.Button(self.footer, text="Повернутися", command=self._show_form).pack(side="left")
        ttk.Button(self.footer, text="Закрити", command=self.destroy).pack(side="right")

        self._redraw()


    def _redraw(self):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists():
            return
        self.canvas.delete("all")
        letters = self._get_current_alphabet()
        n = len(letters)
        if n == 0:
            return
        k = self.shift_var.get() % n

        cx, cy = 320, 210
        r_outer, r_inner = 170, 130

        self.canvas.create_oval(cx-r_outer, cy-r_outer, cx+r_outer, cy+r_outer, outline="#3a466b")
        self.canvas.create_oval(cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner, outline="#3a466b")

        self.pos_outer = {}
        self.pos_inner = {}
        for i, ch in enumerate(letters):
            ang = 2*math.pi * i / n - math.pi/2
            x = cx + r_outer*math.cos(ang)
            y = cy + r_outer*math.sin(ang)
            self.pos_outer[ch] = (x, y)
            self.canvas.create_text(x, y, text=ch, fill=PALETTE["text"])

        for i, ch in enumerate(letters):
            ang = 2*math.pi * ((i + k) % n) / n - math.pi/2
            x = cx + r_inner*math.cos(ang)
            y = cy + r_inner*math.sin(ang)
            self.pos_inner[letters[i]] = (x, y)
            self.canvas.create_text(x, y, text=letters[i], fill=PALETTE["muted"])


        self.canvas.create_line(cx, cy - r_inner, cx, cy - r_outer, fill=PALETTE["accent"], width=2)

    def _on_canvas_click(self, event):
        if not hasattr(self, "pos_outer"): return
        nearest = None; best = 1e9
        for ch, (x, y) in self.pos_outer.items():
            d = (x - event.x)**2 + (y - event.y)**2
            if d < best:
                best, nearest = d, ch
        if nearest is None: return

        x1, y1 = self.pos_outer[nearest]
        x2, y2 = self.pos_inner[nearest]
        self._redraw()
        self.canvas.create_line(x1, y1, x2, y2, fill=PALETTE["accent"], width=2)
        self.canvas.create_oval(x1-6, y1-6, x1+6, y1+6, outline=PALETTE["accent"])
        self.canvas.create_oval(x2-6, y2-6, x2+6, y2+6, outline=PALETTE["accent"])

    def _toggle_autoplay(self):
        if self.autoplay.get():
            self._tick()
        else:
            if hasattr(self, "_after_id") and self._after_id:
                self.after_cancel(self._after_id)
                self._after_id = None

    def _stop_autoplay(self):
        if hasattr(self, "autoplay"):
            try:
                self.autoplay.set(False)
            except Exception:
                pass
        if hasattr(self, "_after_id") and self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _tick(self):
        if not getattr(self, "autoplay", None) or not self.autoplay.get():
            return
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists():
            self._stop_autoplay()
            return
        self.shift_var.set((self.shift_var.get() + 1) % 26)
        self._redraw()
        self._after_id = self.after(600, self._tick)

    def _clear_body(self):
        for w in self.body.winfo_children(): w.destroy()

    def _clear_footer(self):
        for w in self.footer.winfo_children(): w.destroy()

    def encrypt(self):
        text = self.input_text.get("1.0", "end-1c"); k = self.shift_var.get()
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", self._caesar(text, k))

    def decrypt(self):
        text = self.input_text.get("1.0", "end-1c"); k = self.shift_var.get()
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", self._caesar(text, -k))

    def clear(self):
        self.input_text.delete("1.0", "end"); self.output_text.delete("1.0", "end")

    def _caesar(self, text, k):

        alphabet = self._get_current_alphabet()
        n = len(alphabet)
        if n == 0:
            return text
        k = k % n

        upper = {ch: i for i, ch in enumerate(alphabet)}
        lower = {ch.lower(): i for i, ch in enumerate(alphabet)}

        out = []
        for ch in text:
            if ch in upper:
                idx = (upper[ch] + k) % n
                out.append(alphabet[idx])
            elif ch in lower:
                idx = (lower[ch] + k) % n
                out.append(alphabet[idx].lower())
            else:
                out.append(ch)
        return "".join(out)

    def _get_current_alphabet(self):
        name = self.alphabet_name.get() if hasattr(self, "alphabet_name") else "LAT (A–Z, 26)"
        return ALPHABETS.get(name, ALPHABETS["LAT (A–Z, 26)"])

    def _on_alphabet_change(self, *_):
        n = len(self._get_current_alphabet())
        if hasattr(self, "_demo_scale") and self._demo_scale.winfo_exists():
            try:
                self._demo_scale.configure(to=n - 1)
            except Exception:
                pass
        if hasattr(self, "shift_var"):
            self.shift_var.set(self.shift_var.get() % n)
        if getattr(self, "mode", "") == "demo":
            self._redraw()
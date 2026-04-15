import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import math

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pjesme.csv")

STAR_COLOR = "#FFD700"
STAR_EMPTY = "#555555"
BG_DARK = "#1e1e1e"
BG_TABLE = "#2b2b2b"
BG_ROW_ALT = "#323232"
BG_SELECTED = "#24b5a2"
TEAL = "#2bd5bf"


# ── Zvjezdice (Canvas) ─────────────────────────────────────────────────

def _star_polygon(cx, cy, outer_r, inner_r):
    """Vraća listu koordinata za 5-kračnu zvjezdicu."""
    points = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = outer_r if i % 2 == 0 else inner_r
        points.append(cx + r * math.cos(angle))
        points.append(cy + r * math.sin(angle))
    return points


def _clip_polygon_left(points, clip_x):
    """Odsijeca poligon lijevo od clip_x (Sutherland-Hodgman za jednu ivicu)."""
    pts = [(points[i], points[i + 1]) for i in range(0, len(points), 2)]
    result = []
    n = len(pts)
    for i in range(n):
        curr = pts[i]
        nxt = pts[(i + 1) % n]
        c_in = curr[0] <= clip_x
        n_in = nxt[0] <= clip_x
        if c_in:
            result.append(curr)
        if c_in != n_in:
            dx = nxt[0] - curr[0]
            if dx != 0:
                t = (clip_x - curr[0]) / dx
                result.append((clip_x, curr[1] + t * (nxt[1] - curr[1])))
    flat = []
    for p in result:
        flat.extend(p)
    return flat


class StarRating(tk.Canvas):
    """Canvas koji crta precizno popunjene žute zvjezdice."""

    def __init__(self, parent, rating, max_stars=10, star_size=11, bg=BG_TABLE, **kwargs):
        self.star_size = star_size
        self.max_stars = max_stars
        self.spacing = star_size * 2 + 2
        width = self.spacing * max_stars + 4
        height = star_size * 2 + 4
        super().__init__(parent, width=width, height=height, bg=bg,
                         highlightthickness=0, **kwargs)
        self._draw(rating, bg)

    def _draw(self, rating, bg):
        r_out = self.star_size
        r_in = r_out * 0.38
        cy = self.star_size + 2
        rating = max(0.0, min(float(self.max_stars), float(rating)))

        for i in range(self.max_stars):
            cx = self.spacing * i + self.star_size + 2
            pts = _star_polygon(cx, cy, r_out, r_in)
            fill_amount = rating - i

            if fill_amount >= 1.0:
                self.create_polygon(pts, fill=STAR_COLOR, outline=STAR_COLOR)
            elif fill_amount <= 0.0:
                self.create_polygon(pts, fill=STAR_EMPTY, outline=STAR_EMPTY)
            else:
                self.create_polygon(pts, fill=STAR_EMPTY, outline=STAR_EMPTY)
                clip_x = cx - r_out + (2 * r_out) * fill_amount
                clipped = _clip_polygon_left(pts, clip_x)
                if len(clipped) >= 6:
                    self.create_polygon(clipped, fill=STAR_COLOR, outline=STAR_COLOR)


# ── Custom tabela ───────────────────────────────────────────────────────

class FilmTable(tk.Frame):
    """Scrollable tabela sa Canvas zvjezdicama za ocjenu."""

    def __init__(self, parent, on_select=None):
        super().__init__(parent, bg=BG_TABLE)
        self.on_select = on_select
        self.selected_index = None
        self.row_frames = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header
        hdr = tk.Frame(self, bg=TEAL)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        cols = [("Naziv", 3), ("Žanr", 2), ("Godina", 1), ("Ocjena", 2)]
        for i, (text, w) in enumerate(cols):
            hdr.columnconfigure(i, weight=w)
            tk.Label(hdr, text=text, bg=TEAL, fg="white",
                     font=("Arial", 10, "bold"), pady=6).grid(row=0, column=i, sticky="ew")

        # Scrollable body
        self.canvas = tk.Canvas(self, bg=BG_TABLE, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.body = tk.Frame(self.canvas, bg=BG_TABLE)
        self.body.columnconfigure(0, weight=3)
        self.body.columnconfigure(1, weight=2)
        self.body.columnconfigure(2, weight=1)
        self.body.columnconfigure(3, weight=2)

        self.body_window = self.canvas.create_window((0, 0), window=self.body, anchor="nw")
        self.body.bind("<Configure>", self._on_body_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Placeholder
        self.empty_label = tk.Label(
            self.canvas, text="Nema pjesama. Dodaj prvu!",
            fg="#888888", bg=BG_TABLE, font=("Arial", 12)
        )

        # Bind Delete key
        self.canvas.bind_all("<Delete>", self._on_delete)
        self._delete_callback = None

    def bind_delete(self, callback):
        self._delete_callback = callback

    def _on_delete(self, event):
        if self._delete_callback and self.selected_index is not None:
            self._delete_callback()

    def _on_body_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.body_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _select_row(self, index):
        if self.selected_index is not None and self.selected_index < len(self.row_frames):
            old_bg = BG_TABLE if self.selected_index % 2 == 0 else BG_ROW_ALT
            self._set_row_bg(self.selected_index, old_bg)
        self.selected_index = index
        self._set_row_bg(index, BG_SELECTED)
        if self.on_select:
            self.on_select(index)

    def _set_row_bg(self, index, bg):
        if index >= len(self.row_frames):
            return
        frame = self.row_frames[index]
        frame.configure(bg=bg)
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=bg)
            elif isinstance(widget, StarRating):
                widget.configure(bg=bg)

    def get_selected_index(self):
        return self.selected_index

    def refresh(self, filmovi):
        for f in self.row_frames:
            f.destroy()
        self.row_frames.clear()
        self.selected_index = None

        if not filmovi:
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
            return
        self.empty_label.place_forget()

        for i, (naziv, zanr, godina, ocjena) in enumerate(filmovi):
            bg = BG_TABLE if i % 2 == 0 else BG_ROW_ALT
            row = tk.Frame(self.body, bg=bg)
            row.grid(row=i, column=0, columnspan=4, sticky="ew", padx=0)
            row.columnconfigure(0, weight=3)
            row.columnconfigure(1, weight=2)
            row.columnconfigure(2, weight=1)
            row.columnconfigure(3, weight=2)

            tk.Label(row, text=naziv, bg=bg, fg="white",
                     font=("Arial", 10), anchor="center").grid(row=0, column=0, sticky="ew", pady=5)
            tk.Label(row, text=zanr, bg=bg, fg="white",
                     font=("Arial", 10), anchor="center").grid(row=0, column=1, sticky="ew", pady=5)
            tk.Label(row, text=godina, bg=bg, fg="white",
                     font=("Arial", 10), anchor="center").grid(row=0, column=2, sticky="ew", pady=5)

            try:
                rating = float(ocjena)
            except (ValueError, TypeError):
                rating = 0
            stars = StarRating(row, rating, bg=bg)
            stars.grid(row=0, column=3, pady=3, padx=5)

            idx = i
            row.bind("<Button-1>", lambda e, ii=idx: self._select_row(ii))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, ii=idx: self._select_row(ii))

            self.row_frames.append(row)

        # Body columns match header
        self.body.columnconfigure(0, weight=3)
        self.body.columnconfigure(1, weight=2)
        self.body.columnconfigure(2, weight=1)
        self.body.columnconfigure(3, weight=2)


# ── Zaobljeni widgeti ───────────────────────────────────────────────────

def _draw_rounded_rect(canvas, x1, y1, x2, y2, r, fill):
    canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, fill=fill, outline=fill)
    canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, fill=fill, outline=fill)
    canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, fill=fill, outline=fill)
    canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, fill=fill, outline=fill)
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline=fill)
    canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill, outline=fill)


class RoundedEntry(tk.Canvas):
    def __init__(self, parent, width=200, height=32, radius=12, bg_color="#3c3f41",
                 fg="white", font=("Arial", 10), **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"], highlightthickness=0, **kwargs)
        _draw_rounded_rect(self, 0, 0, width, height, radius, bg_color)
        self.entry = tk.Entry(self, bg=bg_color, fg=fg, font=font,
                              insertbackground=fg, relief="flat", border=0)
        self.create_window(width // 2, height // 2, window=self.entry,
                           width=width - radius * 2 + 4, height=height - 8)

    def get(self):
        return self.entry.get()

    def delete(self, first, last):
        self.entry.delete(first, last)

    def insert(self, index, string):
        self.entry.insert(index, string)


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text="", width=160, height=36, radius=14,
                 bg_color=TEAL, fg="white", font=("Arial", 11, "bold"),
                 command=None, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"], highlightthickness=0, **kwargs)
        self.command = command
        _draw_rounded_rect(self, 0, 0, width, height, radius, bg_color)
        self.create_text(width // 2, height // 2, text=text, fill=fg, font=font)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda e: self.config(cursor="hand2"))

    def _on_click(self, event):
        if self.command:
            self.command()


# ── Aplikacija ──────────────────────────────────────────────────────────

class Filmoteka:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify")
        self.root.geometry("850x550")
        self.root.minsize(750, 500)
        self.root.configure(bg=BG_DARK)

        self.filmovi = []

        self._build_ui()
        self._load_csv()
        self._refresh_table()

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(5, weight=1)

        # ── Header ──
        header = tk.Frame(self.root, bg=TEAL)
        header.grid(row=0, column=0, sticky="ew")
        tk.Label(header, text="Spotify", font=("Arial", 22, "bold"),
                 fg="white", bg=TEAL).pack(pady=(14, 14))

        # ── Dodaj novi film ──
        tk.Label(self.root, text="Dodaj novi film", font=("Arial", 11, "bold"),
                 fg="white", bg=BG_DARK, anchor="w"
                 ).grid(row=1, column=0, sticky="w", padx=25, pady=(0, 6))

        input_row = tk.Frame(self.root, bg=BG_DARK)
        input_row.grid(row=2, column=0, sticky="ew", padx=25)
        input_row.columnconfigure(1, weight=4)
        input_row.columnconfigure(3, weight=2)
        input_row.columnconfigure(5, weight=1)
        input_row.columnconfigure(7, weight=1)

        fields = [
            ("Naziv pjesme:", 1, 220), ("Žanr:", 3, 140),
            ("Godina:", 5, 90), ("Ocjena:", 7, 70)
        ]
        self.entries = []
        for text, col, w in fields:
            tk.Label(input_row, text=text, fg="#bbbbbb", bg=BG_DARK,
                     font=("Arial", 10)).grid(row=0, column=col - 1, sticky="w", padx=(0, 6))
            entry = RoundedEntry(input_row, width=w, height=32)
            entry.grid(row=0, column=col, sticky="ew", padx=(0, 12) if col < 7 else (0, 0))
            self.entries.append(entry)

        self.naziv_entry, self.zanr_entry, self.godina_entry, self.ocjena_entry = self.entries

        # Dugme Dodaj
        btn_add_frame = tk.Frame(self.root, bg=BG_DARK)
        btn_add_frame.grid(row=3, column=0, pady=(10, 0))
        RoundedButton(btn_add_frame, text="+ Dodaj pjesmu", width=170, height=36,
                      radius=14, bg_color=TEAL, command=self.dodaj_film).pack()

        # ── Kolekcija filmova ──
        tk.Label(self.root, text="Kolekcija pjesama  \u2014 klikni na red da ga odabereš",
                 font=("Arial", 11, "bold"), fg="white", bg=BG_DARK, anchor="w"
                 ).grid(row=4, column=0, sticky="nw", padx=25, pady=(14, 4))

        # Tabela
        self.table = FilmTable(self.root)
        self.table.grid(row=5, column=0, padx=25, sticky="nsew")
        self.table.bind_delete(self.obrisi_film)

        # ── Dugmad na dnu ──
        btn_frame = tk.Frame(self.root, bg=BG_DARK)
        btn_frame.grid(row=6, column=0, pady=(12, 15))
        RoundedButton(btn_frame, text="Uredi odabrani", width=170, height=38,
                      radius=14, bg_color="#ff9800", command=self.izmijeni_film
                      ).pack(side="left", padx=12)
        RoundedButton(btn_frame, text="Obriši odabrani", width=170, height=38,
                      radius=14, bg_color="#f44336", command=self.obrisi_film
                      ).pack(side="left", padx=12)

    # ── CSV ─────────────────────────────────────────────────────────────

    def _load_csv(self):
        if not os.path.exists(CSV_PATH):
            return
        try:
            with open(CSV_PATH, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header is None:
                    return
                for row in reader:
                    if len(row) == 4:
                        self.filmovi.append(tuple(row))
        except Exception as e:
            messagebox.showerror("Greška pri čitanju", f"Nije moguće učitati CSV fajl:\n{e}")

    def _save_csv(self):
        try:
            with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["naziv", "zanr", "godina", "ocjena"])
                for film in self.filmovi:
                    writer.writerow(film)
        except Exception as e:
            messagebox.showerror("Greška pri snimanju", f"Nije moguće sačuvati CSV fajl:\n{e}")

    # ── Pomoćne ─────────────────────────────────────────────────────────

    def _refresh_table(self):
        self.table.refresh(self.filmovi)

    def _clear_entries(self):
        for entry in self.entries:
            entry.delete(0, tk.END)

    def _validate(self, naziv, zanr, godina, ocjena, parent=None):
        parent = parent or self.root
        if not naziv:
            messagebox.showerror("Greška", "Naziv pjesme je obavezan!", parent=parent)
            return False
        if not zanr:
            messagebox.showerror("Greška", "Žanr je obavezan!", parent=parent)
            return False
        if not godina:
            messagebox.showerror("Greška", "Godina je obavezna!", parent=parent)
            return False
        if not godina.isdigit():
            messagebox.showerror("Greška", "Godina mora biti cijeli broj!", parent=parent)
            return False
        if not ocjena:
            messagebox.showerror("Greška", "Ocjena je obavezna!", parent=parent)
            return False
        try:
            o = float(ocjena)
            if not (1 <= o <= 10):
                messagebox.showerror("Greška", "Ocjena mora biti između 1 i 10!", parent=parent)
                return False
        except ValueError:
            messagebox.showerror("Greška", "Ocjena mora biti broj!", parent=parent)
            return False
        return True

    # ── CRUD ────────────────────────────────────────────────────────────

    def dodaj_film(self):
        naziv = self.naziv_entry.get().strip()
        zanr = self.zanr_entry.get().strip()
        godina = self.godina_entry.get().strip()
        ocjena = self.ocjena_entry.get().strip()

        if not self._validate(naziv, zanr, godina, ocjena):
            return

        self.filmovi.append((naziv, zanr, godina, ocjena))
        self._save_csv()
        self._refresh_table()
        self._clear_entries()

    def izmijeni_film(self):
        idx = self.table.get_selected_index()
        if idx is None:
            messagebox.showerror("Greška", "Odaberite pjesmu iz tabele za izmjenu!")
            return
        film = self.filmovi[idx]

        popup = tk.Toplevel(self.root)
        popup.title("Izmijeni pjesmu")
        popup.configure(bg=BG_DARK)
        popup.geometry("440x300")
        popup.minsize(380, 280)
        popup.transient(self.root)
        popup.grab_set()
        popup.columnconfigure(1, weight=1)

        tk.Label(popup, text="Izmijeni pjesmu", font=("Arial", 15, "bold"),
                 fg=TEAL, bg=BG_DARK).grid(row=0, column=0, columnspan=2, pady=(18, 12))

        labels = ["Naziv pjesme:", "Žanr:", "Godina:", "Ocjena (1-10):"]
        popup_entries = []
        for i, (text, val) in enumerate(zip(labels, film)):
            tk.Label(popup, text=text, fg="#bbbbbb", bg=BG_DARK,
                     font=("Arial", 10), anchor="w"
                     ).grid(row=i + 1, column=0, sticky="w", padx=20, pady=5)
            re = RoundedEntry(popup, width=220, height=30)
            re.grid(row=i + 1, column=1, padx=(5, 20), pady=5, sticky="ew")
            re.insert(0, val)
            popup_entries.append(re)

        def sacuvaj():
            naziv = popup_entries[0].get().strip()
            zanr = popup_entries[1].get().strip()
            godina = popup_entries[2].get().strip()
            ocjena = popup_entries[3].get().strip()
            if not self._validate(naziv, zanr, godina, ocjena, parent=popup):
                return
            self.filmovi[idx] = (naziv, zanr, godina, ocjena)
            self._save_csv()
            self._refresh_table()
            popup.destroy()

        btn_frame = tk.Frame(popup, bg=BG_DARK)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(15, 12))
        RoundedButton(btn_frame, text="Sačuvaj", width=120, height=34,
                      radius=12, bg_color="#4caf50", command=sacuvaj
                      ).pack(side="left", padx=10)
        RoundedButton(btn_frame, text="Otkaži", width=120, height=34,
                      radius=12, bg_color="#f44336", command=popup.destroy
                      ).pack(side="left", padx=10)

    def obrisi_film(self):
        idx = self.table.get_selected_index()
        if idx is None:
            messagebox.showerror("Greška", "Odaberite pjesme iz tabele za brisanje!")
            return
        naziv = self.filmovi[idx][0]
        if not messagebox.askyesno("Potvrda",
                                   f'Da li ste sigurni da želite obrisati pjesmu "{naziv}"?'):
            return
        self.filmovi.pop(idx)
        self._save_csv()
        self._refresh_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = Filmoteka(root)
    root.mainloop()

"""
hanoi_app.py - Aplikasi Tower of Hanoi (k tiang, n cakram) dengan 4 algoritma pencarian.

Memakai file algoritma yang sudah ada (harus berada di folder yang sama):
    bfs.py, dfs.py, astar.py, greedy.py, hanoi_common.py
GUI memakai Tkinter (sudah bawaan Python, tidak perlu install apa pun).

Jalankan:  python hanoi_app.py

Fitur:
  - Pilih jumlah tiang (3-5) dan cakram (1-7)
  - Jalankan satu algoritma atau bandingkan keempatnya
  - Animasi solusi (play / pause / step / lompat awal-akhir / atur kecepatan)
  - Cakram digambar dengan angka = ukuran cakram (1 terkecil)
  - Tabel perbandingan: langkah, optimal?, node expanded/generated, frontier, waktu
"""
import colorsys
import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

from astar import astar
from bfs import bfs
from dfs import dfs
from greedy import greedy
from hanoi_common import (MAX_DISKS, MAX_PEGS, MIN_DISKS, MIN_PEGS, describe_move,
                          frame_stewart, goal_state, initial_state, peg_name)

ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "A*": astar,
    "Greedy": greedy,
}


def solve_one(name, n, k):
    """Jalankan satu algoritma; kembalikan (hasil, waktu_detik)."""
    start = time.perf_counter()
    result = ALGORITHMS[name](initial_state(n), goal_state(n, k), k)
    return result, time.perf_counter() - start


class HanoiApp:
    def __init__(self, root):
        self.root = root
        root.title("Tower of Hanoi - BFS / DFS / A* / Greedy")
        root.geometry("1120x780")
        root.minsize(900, 650)

        self.n, self.k = 4, 4
        self.results = {}          # nama algoritma -> (hasil, waktu)
        self.path = []             # jalur yang sedang ditampilkan
        self.idx = 0
        self.playing = False
        self.jobs = queue.Queue()

        self._build_controls()
        self._build_main()
        self.draw()

    # ------------------------------------------------------------------ UI
    def _build_controls(self):
        panel = ttk.Frame(self.root, padding=10)
        panel.pack(side="left", fill="y")

        ttk.Label(panel, text=f"Jumlah tiang ({MIN_PEGS}-{MAX_PEGS})").pack(anchor="w")
        self.var_k = tk.IntVar(value=4)
        ttk.Spinbox(panel, from_=MIN_PEGS, to=MAX_PEGS, textvariable=self.var_k,
                    width=8, state="readonly").pack(anchor="w")

        ttk.Label(panel, text=f"Jumlah cakram ({MIN_DISKS}-{MAX_DISKS})").pack(anchor="w", pady=(10, 0))
        self.var_n = tk.IntVar(value=4)
        ttk.Spinbox(panel, from_=MIN_DISKS, to=MAX_DISKS, textvariable=self.var_n,
                    width=8, state="readonly").pack(anchor="w")

        ttk.Label(panel, text="Algoritma").pack(anchor="w", pady=(10, 0))
        self.var_algo = tk.StringVar(value="A*")
        ttk.Combobox(panel, values=list(ALGORITHMS), textvariable=self.var_algo,
                     state="readonly", width=10).pack(anchor="w")

        self.btn_solve = ttk.Button(panel, text="Solve (algoritma terpilih)",
                                    command=lambda: self.start([self.var_algo.get()]))
        self.btn_solve.pack(fill="x", pady=(14, 3))
        self.btn_all = ttk.Button(panel, text="Bandingkan semua algoritma",
                                  command=lambda: self.start(list(ALGORITHMS)))
        self.btn_all.pack(fill="x", pady=3)

        ttk.Separator(panel).pack(fill="x", pady=12)
        ttk.Label(panel, text="Animasi").pack(anchor="w")
        bar = ttk.Frame(panel)
        bar.pack(anchor="w", pady=4)
        for col, (txt, cmd) in enumerate([("⏮", self.go_start), ("◀", lambda: self.step(-1)),
                                           ("▶", self.toggle_play), ("▶|", lambda: self.step(1)),
                                           ("⏭", self.go_end)]):
            b = ttk.Button(bar, text=txt, width=3, command=cmd)
            b.grid(row=0, column=col, padx=1)
            if txt == "▶":
                self.btn_play = b

        ttk.Label(panel, text="Jeda antar langkah (ms)").pack(anchor="w", pady=(8, 0))
        self.var_speed = tk.IntVar(value=300)
        ttk.Scale(panel, from_=5, to=1000, variable=self.var_speed,
                  orient="horizontal", length=160).pack(anchor="w")

        self.lbl_info = ttk.Label(panel, text="", wraplength=190, justify="left")
        self.lbl_info.pack(anchor="w", pady=(14, 4))
        self.lbl_status = ttk.Label(panel, text="Pilih parameter lalu klik Solve.",
                                    wraplength=190, foreground="#666")
        self.lbl_status.pack(anchor="w")

    def _build_main(self):
        main = ttk.Frame(self.root, padding=(0, 10, 10, 10))
        main.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(main, bg="#fafafa", highlightthickness=1,
                                highlightbackground="#bbb")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw())

        cols = ("algo", "moves", "optimal", "expanded", "generated", "frontier", "time")
        heads = ("Algoritma", "Langkah", "Optimal?", "Expanded", "Generated",
                 "Max Frontier", "Waktu (detik)")
        self.tree = ttk.Treeview(main, columns=cols, show="headings", height=5)
        for c, h in zip(cols, heads):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=105, anchor="center")
        self.tree.pack(fill="x", pady=(10, 0))
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)
        ttk.Label(main, foreground="#777",
                  text="Klik baris tabel untuk memutar solusi algoritma tersebut.").pack(anchor="w")

    # -------------------------------------------------------------- solving
    def start(self, names):
        try:
            k, n = int(self.var_k.get()), int(self.var_n.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Input salah", "Jumlah tiang dan cakram harus bilangan bulat.")
            return
        if not (MIN_PEGS <= k <= MAX_PEGS and MIN_DISKS <= n <= MAX_DISKS):
            messagebox.showerror("Input salah",
                                 f"Tiang {MIN_PEGS}-{MAX_PEGS}, cakram {MIN_DISKS}-{MAX_DISKS}.")
            return

        self.pause()
        self.n, self.k = n, k
        self.results.clear()
        self.path, self.idx = [], 0
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.btn_solve.state(["disabled"])
        self.btn_all.state(["disabled"])
        self.lbl_info.config(text=f"{k} tiang, {n} cakram\nRuang state: {k ** n:,}\n"
                                  f"Langkah optimal (Frame-Stewart): {frame_stewart(n, k)}")
        self.lbl_status.config(text="Menghitung...")
        self.draw()

        def worker():
            for name in names:
                try:
                    self.jobs.put((name, *solve_one(name, n, k)))
                except Exception as exc:       # pragma: no cover
                    self.jobs.put((name, exc, 0.0))
            self.jobs.put(None)

        threading.Thread(target=worker, daemon=True).start()
        self.root.after(80, self.poll)

    def poll(self):
        try:
            while True:
                job = self.jobs.get_nowait()
                if job is None:
                    self.btn_solve.state(["!disabled"])
                    self.btn_all.state(["!disabled"])
                    self.lbl_status.config(text="Selesai. Tekan ▶ untuk animasi.")
                    return
                name, result, elapsed = job
                if isinstance(result, Exception):
                    messagebox.showerror("Error", f"{name}: {result}")
                    continue
                self.add_result(name, result, elapsed)
        except queue.Empty:
            pass
        self.root.after(80, self.poll)

    def add_result(self, name, result, elapsed):
        self.results[name] = (result, elapsed)
        moves = len(result["path"]) - 1
        optimal = "ya" if moves == frame_stewart(self.n, self.k) else "tidak"
        self.tree.insert("", "end", iid=name, values=(
            name, f"{moves:,}", optimal, f"{result['expanded']:,}",
            f"{result['generated']:,}", f"{result['max_frontier']:,}", f"{elapsed:.4f}"))
        if not self.path:
            self.tree.selection_set(name)      # memicu on_select_row -> memuat jalur

    def on_select_row(self, _event):
        sel = self.tree.selection()
        if sel and sel[0] in self.results:
            self.pause()
            self.path = self.results[sel[0]][0]["path"]
            self.idx = 0
            self.draw()

    # ------------------------------------------------------------ animation
    def pause(self):
        self.playing = False
        self.btn_play.config(text="▶")

    def toggle_play(self):
        if not self.path:
            return
        if self.playing:
            self.pause()
            return
        if self.idx >= len(self.path) - 1:
            self.idx = 0
        self.playing = True
        self.btn_play.config(text="⏸")
        self.tick()

    def tick(self):
        if not self.playing:
            return
        if self.idx >= len(self.path) - 1:
            self.pause()
            return
        self.idx += 1
        self.draw()
        self.root.after(int(self.var_speed.get()), self.tick)

    def step(self, delta):
        if self.path:
            self.pause()
            self.idx = max(0, min(len(self.path) - 1, self.idx + delta))
            self.draw()

    def go_start(self):
        if self.path:
            self.pause()
            self.idx = 0
            self.draw()

    def go_end(self):
        if self.path:
            self.pause()
            self.idx = len(self.path) - 1
            self.draw()

    # -------------------------------------------------------------- drawing
    def draw(self):
        c = self.canvas
        c.delete("all")
        width, height = max(c.winfo_width(), 300), max(c.winfo_height(), 200)
        n, k = self.n, self.k
        state = self.path[self.idx] if self.path else initial_state(n)

        base_y = height - 40
        slot = width / k
        disk_h = max(10, min(30, (height - 110) / (n + 1)))
        max_w = slot * 0.88
        min_w = min(30, max_w * 0.3)

        for p in range(k):
            cx = slot * (p + 0.5)
            c.create_rectangle(cx - slot * 0.45, base_y, cx + slot * 0.45, base_y + 8,
                               fill="#6b4f2a", outline="")
            c.create_rectangle(cx - 4, base_y - (n + 1) * disk_h, cx + 4, base_y,
                               fill="#8a6a3a", outline="")
            c.create_text(cx, base_y + 26, text=peg_name(p), font=("Arial", 12, "bold"))

            level = 0
            for d in range(n - 1, -1, -1):          # bawah -> atas = besar -> kecil
                if state[d] != p:
                    continue
                w = min_w + (max_w - min_w) * (d + 1) / n
                y = base_y - (level + 1) * disk_h
                r, g, b = colorsys.hsv_to_rgb(d / max(n, 1) * 0.8, 0.6, 0.95)
                color = "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))
                c.create_rectangle(cx - w / 2, y, cx + w / 2, y + disk_h - 2,
                                   fill=color, outline="#333")
                c.create_text(cx, y + (disk_h - 2) / 2, text=str(d + 1),
                              font=("Arial", 11, "bold"))
                level += 1

        if self.path:
            text = f"Langkah {self.idx:,} / {len(self.path) - 1:,}"
            if self.idx > 0:
                text += "   |   " + describe_move(self.path[self.idx - 1], self.path[self.idx])
        else:
            text = "Belum ada solusi"
        c.create_text(12, 10, anchor="nw", text=text, font=("Arial", 12))


def main():
    root = tk.Tk()
    HanoiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

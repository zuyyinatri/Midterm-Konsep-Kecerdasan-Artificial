"""
hanoi_app.py - Tower of Hanoi (3-5 tiang, 1-7 cakram) dengan BFS / DFS / A* / Greedy.

Versi mandiri: tidak butuh bfs.py, dfs.py, astar.py, greedy.py, hanoi_common.py.
Jalankan:  python hanoi_app.py          (hanya memakai Tkinter bawaan Python)

Model biaya satu langkah (memindah cakram ukuran d dari tiang a ke tiang b):
    unit : 1
    W1   : d              (ukuran cakram, 1 = terkecil)
    W2   : |a - b|        (jarak antar tiang, A=0, B=1, ...)

Heuristik tunggal h1 (batas bawah biaya menuju tiang terakhir G):
    unit : jumlah cakram yang belum di G
    W1   : jumlah ukuran cakram yang belum di G
    W2   : jumlah (G - posisi cakram)
Dipakai oleh A* (f = g + h1) dan Greedy (f = h1), sesuai model biaya yang dipilih.
BFS dan DFS tidak memakai biaya/heuristik, tetapi biaya W1 dan W2 jalurnya tetap dihitung.
"""
import colorsys
import heapq
import itertools
import queue
import threading
import time
import tkinter as tk
from functools import lru_cache
from tkinter import messagebox, ttk

MIN_PEGS, MAX_PEGS = 3, 5
MIN_DISKS, MAX_DISKS = 1, 7

# ----------------------------------------------------------------- domain
# State = tuple panjang n; state[d] = indeks tiang tempat cakram d (0 = terkecil).


def peg_name(p):
    return chr(ord("A") + p)


def initial_state(n):
    return (0,) * n


def goal_state(n, k):
    return (k - 1,) * n


def successors(state, k):
    """Hasilkan (cakram, dari, ke, state_baru)."""
    top = [None] * k                      # cakram terkecil (= teratas) di tiap tiang
    for d, p in enumerate(state):
        if top[p] is None:
            top[p] = d
    for a in range(k):
        d = top[a]
        if d is None:
            continue
        for b in range(k):
            if a != b and (top[b] is None or top[b] > d):
                s = list(state)
                s[d] = b
                yield d, a, b, tuple(s)


def move_cost(model, d, a, b):
    if model == "unit":
        return 1
    if model == "size":
        return d + 1
    return abs(a - b)


def diff_move(prev, cur):
    for d, (x, y) in enumerate(zip(prev, cur)):
        if x != y:
            return d, x, y
    return None


def path_cost(path, model):
    total = 0
    for prev, cur in zip(path, path[1:]):
        total += move_cost(model, *diff_move(prev, cur))
    return total


def describe_move(prev, cur):
    d, a, b = diff_move(prev, cur)
    return f"cakram {d + 1}: {peg_name(a)} → {peg_name(b)}"


def h1(state, model, k):
    g = k - 1
    if model == "unit":
        return sum(1 for p in state if p != g)
    if model == "size":
        return sum(d + 1 for d, p in enumerate(state) if p != g)
    return sum(g - p for p in state)


@lru_cache(None)
def frame_stewart(n, k):
    """Jumlah langkah minimum (unit) menurut Frame-Stewart."""
    if n == 0:
        return 0
    if n == 1:
        return 1
    if k == 3:
        return 2 ** n - 1
    return min(2 * frame_stewart(t, k) + frame_stewart(n - t, k - 1) for t in range(1, n))


# ------------------------------------------------------------ algoritma
def _rebuild(parent, s):
    path = [s]
    while parent[s] is not None:
        s = parent[s]
        path.append(s)
    return path[::-1]


def bfs(start, goal, k, model):
    q = [start]; head = 0
    parent = {start: None}
    gen, maxf = 1, 1
    while head < len(q):
        s = q[head]; head += 1
        if s == goal:
            return dict(path=_rebuild(parent, s), expanded=head, generated=gen, max_frontier=maxf)
        for *_, t in successors(s, k):
            if t not in parent:
                parent[t] = s; q.append(t); gen += 1
        maxf = max(maxf, len(q) - head)
    return None


def dfs(start, goal, k, model):
    stack = [(start, None)]
    parent, visited = {}, set()
    gen, maxf, exp = 1, 1, 0
    while stack:
        s, par = stack.pop()
        if s in visited:
            continue
        visited.add(s); parent[s] = par; exp += 1
        if s == goal:
            return dict(path=_rebuild(parent, s), expanded=exp, generated=gen, max_frontier=maxf)
        for *_, t in reversed(list(successors(s, k))):
            if t not in visited:
                stack.append((t, s)); gen += 1
        maxf = max(maxf, len(stack))
    return None


def astar(start, goal, k, model):
    cnt = itertools.count()
    h0 = h1(start, model, k)
    pq = [(h0, h0, next(cnt), start, 0)]
    best, parent = {start: 0}, {start: None}
    gen, maxf, exp = 1, 1, 0
    while pq:
        _, _, _, s, g = heapq.heappop(pq)
        if g > best[s]:
            continue                        # entri usang
        exp += 1
        if s == goal:
            return dict(path=_rebuild(parent, s), expanded=exp, generated=gen, max_frontier=maxf)
        for d, a, b, t in successors(s, k):
            g2 = g + move_cost(model, d, a, b)
            if g2 < best.get(t, float("inf")):
                best[t] = g2; parent[t] = s; gen += 1
                h = h1(t, model, k)
                heapq.heappush(pq, (g2 + h, h, next(cnt), t, g2))
        maxf = max(maxf, len(pq))
    return None


def greedy(start, goal, k, model):
    cnt = itertools.count()
    pq = [(h1(start, model, k), next(cnt), start)]
    parent, closed = {start: None}, set()
    gen, maxf, exp = 1, 1, 0
    while pq:
        _, _, s = heapq.heappop(pq)
        if s in closed:
            continue
        closed.add(s); exp += 1
        if s == goal:
            return dict(path=_rebuild(parent, s), expanded=exp, generated=gen, max_frontier=maxf)
        for *_, t in successors(s, k):
            if t not in parent:
                parent[t] = s; gen += 1
                heapq.heappush(pq, (h1(t, model, k), next(cnt), t))
        maxf = max(maxf, len(pq))
    return None


ALGORITHMS = {"BFS": bfs, "DFS": dfs, "A*": astar, "Greedy": greedy}
MODELS = {"Unit": "unit", "W1 (ukuran)": "size", "W2 (jarak)": "dist"}


def solve_one(name, n, k, model):
    t0 = time.perf_counter()
    result = ALGORITHMS[name](initial_state(n), goal_state(n, k), k, model)
    return result, time.perf_counter() - t0


# -------------------------------------------------------------------- GUI
class HanoiApp:
    def __init__(self, root):
        self.root = root
        root.title("Tower of Hanoi - BFS / DFS / A* / Greedy (biaya W1 & W2, h1)")
        root.geometry("1180x780")
        root.minsize(940, 650)

        self.n, self.k, self.model = 4, 4, "size"
        self.ref_cost = None
        self.results = {}
        self.path, self.cum1, self.cum2 = [], [0], [0]
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

        ttk.Label(panel, text="Model biaya (untuk A*/Greedy)").pack(anchor="w", pady=(10, 0))
        self.var_model = tk.StringVar(value="W1 (ukuran)")
        ttk.Combobox(panel, values=list(MODELS), textvariable=self.var_model,
                     state="readonly", width=14).pack(anchor="w")

        ttk.Label(panel, text="Algoritma").pack(anchor="w", pady=(10, 0))
        self.var_algo = tk.StringVar(value="A*")
        ttk.Combobox(panel, values=list(ALGORITHMS), textvariable=self.var_algo,
                     state="readonly", width=10).pack(anchor="w")
        ttk.Label(panel, text="Heuristik: h1", foreground="#666").pack(anchor="w", pady=(4, 0))

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

        cols = ("algo", "moves", "w1", "w2", "optimal", "expanded", "generated", "frontier", "time")
        heads = ("Algoritma", "Langkah", "Cost W1", "Cost W2", "Optimal?",
                 "Expanded", "Generated", "Max Frontier", "Waktu (s)")
        widths = (75, 80, 80, 80, 70, 90, 90, 95, 80)
        self.tree = ttk.Treeview(main, columns=cols, show="headings", height=5)
        for c, h, w in zip(cols, heads, widths):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="x", pady=(10, 0))
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)
        ttk.Label(main, foreground="#777", wraplength=800, justify="left",
                  text="Klik baris tabel untuk memutar solusinya. 'Optimal?' membandingkan biaya jalur "
                       "dengan biaya optimum pada model biaya yang dipilih.").pack(anchor="w")

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
        self.model = MODELS[self.var_model.get()]
        self.results.clear()
        self.ref_cost = None
        self.path, self.cum1, self.cum2, self.idx = [], [0], [0], 0
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.btn_solve.state(["disabled"])
        self.btn_all.state(["disabled"])
        self.lbl_info.config(text=f"{k} tiang, {n} cakram\nRuang state: {k ** n:,}\n"
                                  f"Langkah minimum (Frame-Stewart): {frame_stewart(n, k)}\n"
                                  f"Model biaya: {self.var_model.get()}")
        self.lbl_status.config(text="Menghitung...")
        self.draw()

        model = self.model

        def worker():
            try:                                   # biaya optimum sebagai pembanding
                ref, _ = solve_one("A*", n, k, model)
                self.jobs.put(("__ref__", path_cost(ref["path"], model), 0.0))
            except Exception as exc:               # pragma: no cover
                self.jobs.put(("__ref__", exc, 0.0))
            for name in names:
                try:
                    self.jobs.put((name, *solve_one(name, n, k, model)))
                except Exception as exc:           # pragma: no cover
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
                if name == "__ref__":
                    self.ref_cost = result
                    continue
                self.add_result(name, result, elapsed)
        except queue.Empty:
            pass
        self.root.after(80, self.poll)

    def add_result(self, name, result, elapsed):
        self.results[name] = (result, elapsed)
        path = result["path"]
        c1, c2 = path_cost(path, "size"), path_cost(path, "dist")
        mine = path_cost(path, self.model)
        optimal = "ya" if self.ref_cost is not None and mine == self.ref_cost else "tidak"
        self.tree.insert("", "end", iid=name, values=(
            name, f"{len(path) - 1:,}", f"{c1:,}", f"{c2:,}", optimal,
            f"{result['expanded']:,}", f"{result['generated']:,}",
            f"{result['max_frontier']:,}", f"{elapsed:.4f}"))
        if not self.path:
            self.tree.selection_set(name)

    def on_select_row(self, _event):
        sel = self.tree.selection()
        if sel and sel[0] in self.results:
            self.pause()
            self.path = self.results[sel[0]][0]["path"]
            self.cum1, self.cum2 = [0], [0]
            for prev, cur in zip(self.path, self.path[1:]):
                mv = diff_move(prev, cur)
                self.cum1.append(self.cum1[-1] + move_cost("size", *mv))
                self.cum2.append(self.cum2[-1] + move_cost("dist", *mv))
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
            text = (f"Langkah {self.idx:,} / {len(self.path) - 1:,}"
                    f"   |   Biaya berjalan W1={self.cum1[self.idx]:,}  W2={self.cum2[self.idx]:,}")
            if self.idx > 0:
                text += "\n" + describe_move(self.path[self.idx - 1], self.path[self.idx])
        else:
            text = "Belum ada solusi"
        c.create_text(12, 10, anchor="nw", text=text, font=("Arial", 12))


def main():
    root = tk.Tk()
    HanoiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
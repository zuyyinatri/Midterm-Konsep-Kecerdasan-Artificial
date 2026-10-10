"""
hanoi_common.py
Modul pendukung untuk semua algoritma (bfs.py, dfs.py, astar.py, greedy.py).

Isi:
  - Definisi masalah Tower of Hanoi dengan k tiang dan n cakram
  - Heuristik: jumlah cakram yang belum berada di tiang goal
  - Input parameter (batas: 3-5 tiang, 1-7 cakram)
  - Tampilan hasil dalam bentuk tabel (cakram = angka, makin besar angka makin besar cakram)

Representasi state:
  tuple dengan panjang n. state[i] = indeks tiang tempat cakram ke-i berada
  (i = 0 -> cakram "1" paling kecil, i = n-1 -> cakram "n" paling besar).
  Initial state : semua cakram di tiang A (indeks 0)
  Goal state    : semua cakram di tiang terakhir (indeks k-1)
"""
import argparse
import time

MIN_PEGS, MAX_PEGS = 3, 5
MIN_DISKS, MAX_DISKS = 1, 7


# --------------------------------------------------------------------------
# Definisi masalah
# --------------------------------------------------------------------------
def initial_state(n):
    return (0,) * n


def goal_state(n, k):
    return (k - 1,) * n


def successors(state, k):
    """Menghasilkan semua state baru dari satu langkah legal.

    Langkah legal: pindahkan cakram teratas suatu tiang ke tiang lain yang
    kosong atau yang cakram teratasnya lebih besar.
    """
    n = len(state)
    top = [n] * k                      # n = tiang kosong (dianggap lebih besar dari semua cakram)
    for d in range(n - 1, -1, -1):     # hasil akhir: top[p] = cakram terkecil di tiang p
        top[state[d]] = d
    for src in range(k):
        disk = top[src]
        if disk == n:                  # tiang kosong
            continue
        for dst in range(k):
            if dst != src and top[dst] > disk:
                yield state[:disk] + (dst,) + state[disk + 1:]


def misplaced_disks(state, k):
    """Heuristik h(n): jumlah cakram yang belum berada di tiang goal (k-1)."""
    return sum(1 for peg in state if peg != k - 1)


def build_path(parent, state):
    """Susun jalur dari initial state sampai state ini menggunakan dict parent."""
    path = []
    while state is not None:
        path.append(state)
        state = parent[state]
    return path[::-1]


def frame_stewart(n, k):
    """Jumlah langkah optimal referensi (Frame-Stewart), dipakai hanya sebagai pembanding."""
    memo = {}

    def fs(n, k):
        if n == 0:
            return 0
        if n == 1:
            return 1
        if k < 3:
            return float("inf")
        if k == 3:
            return 2 ** n - 1
        if (n, k) not in memo:
            memo[(n, k)] = min(2 * fs(m, k) + fs(n - m, k - 1) for m in range(1, n))
        return memo[(n, k)]

    return fs(n, k)


def peg_name(p):
    return chr(ord("A") + p)


# --------------------------------------------------------------------------
# Input parameter
# --------------------------------------------------------------------------
def _ask_int(prompt, lo, hi):
    while True:
        try:
            value = int(input(prompt))
            if lo <= value <= hi:
                return value
        except ValueError:
            pass
        print(f"  Masukkan bilangan bulat {lo}-{hi}.")


def get_parameters(description):
    """Ambil jumlah tiang, jumlah cakram, dan mode tampilan langkah.

    Bisa lewat argumen (-k, -n) atau diketik saat program berjalan.
    """
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("-k", "--pegs", type=int, help=f"jumlah tiang ({MIN_PEGS}-{MAX_PEGS})")
    ap.add_argument("-n", "--disks", type=int, help=f"jumlah cakram ({MIN_DISKS}-{MAX_DISKS})")
    ap.add_argument("--steps", choices=["auto", "all", "none"], default="auto",
                    help="tampilkan tabel tiap langkah: auto (semua jika <= 60 langkah), all, none")
    a = ap.parse_args()

    if a.pegs is None:
        a.pegs = _ask_int(f"Jumlah tiang ({MIN_PEGS}-{MAX_PEGS}): ", MIN_PEGS, MAX_PEGS)
    if a.disks is None:
        a.disks = _ask_int(f"Jumlah cakram ({MIN_DISKS}-{MAX_DISKS}): ", MIN_DISKS, MAX_DISKS)
    if not MIN_PEGS <= a.pegs <= MAX_PEGS:
        ap.error(f"jumlah tiang harus {MIN_PEGS}-{MAX_PEGS}")
    if not MIN_DISKS <= a.disks <= MAX_DISKS:
        ap.error(f"jumlah cakram harus {MIN_DISKS}-{MAX_DISKS}")
    return a.pegs, a.disks, a.steps


# --------------------------------------------------------------------------
# Tampilan tabel
# --------------------------------------------------------------------------
def format_state(state, k):
    """Gambar state sebagai tabel teks. Angka = ukuran cakram (1 terkecil, n terbesar)."""
    n = len(state)
    pegs = [[] for _ in range(k)]
    for d in range(n - 1, -1, -1):         # dari cakram terbesar -> terkecil (bawah -> atas)
        pegs[state[d]].append(d + 1)
    w = len(str(n)) + 2
    border = "+" + "+".join("-" * w for _ in range(k)) + "+"
    lines = [border]
    for level in range(n - 1, -1, -1):     # baris paling atas dulu
        cells = [(str(p[level]) if level < len(p) else ".").center(w) for p in pegs]
        lines.append("|" + "|".join(cells) + "|")
    lines.append(border)
    lines.append("|" + "|".join(peg_name(p).center(w) for p in range(k)) + "|")
    lines.append(border)
    return "\n".join(lines)


def describe_move(prev, cur):
    for disk, (a, b) in enumerate(zip(prev, cur)):
        if a != b:
            return f"pindahkan cakram {disk + 1} dari {peg_name(a)} ke {peg_name(b)}"
    return ""


def print_solution(name, k, n, result, elapsed, steps_mode):
    path = result["path"]
    moves = len(path) - 1
    show_all = steps_mode == "all" or (steps_mode == "auto" and moves <= 60)

    print(f"\n=== {name} | {k} tiang, {n} cakram ===")
    print("\nState awal:")
    print(format_state(path[0], k))

    if show_all and steps_mode != "none":
        for i in range(1, len(path)):
            print(f"\nLangkah {i}: {describe_move(path[i - 1], path[i])}")
            print(format_state(path[i], k))
    else:
        note = "(dimatikan)" if steps_mode == "none" else f"(solusi {moves} langkah, terlalu panjang; gunakan --steps all)"
        print(f"\nTabel langkah-langkah tidak ditampilkan {note}")
        print("\nState akhir:")
        print(format_state(path[-1], k))

    ref = frame_stewart(n, k)
    print("\n--- Ringkasan ---")
    print(f"Algoritma            : {name}")
    print(f"Jumlah langkah       : {moves}")
    print(f"Langkah optimal      : {ref} (Frame-Stewart)  -> {'OPTIMAL' if moves == ref else 'TIDAK optimal'}")
    print(f"Node di-expand       : {result['expanded']:,}")
    print(f"Node di-generate     : {result['generated']:,}")
    print(f"Ukuran frontier maks : {result['max_frontier']:,}")
    print(f"Waktu eksekusi       : {elapsed:.4f} detik")


def run(name, solver, description):
    """Alur utama dipakai semua file algoritma."""
    k, n, steps_mode = get_parameters(description)
    start = time.perf_counter()
    result = solver(initial_state(n), goal_state(n, k), k)
    elapsed = time.perf_counter() - start
    print_solution(name, k, n, result, elapsed, steps_mode)

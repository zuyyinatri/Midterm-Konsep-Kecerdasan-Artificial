"""
greedy.py - Greedy Best-First Search untuk Tower of Hanoi (k tiang, n cakram)

Hanya memakai heuristik: f(n) = h(n) = jumlah cakram yang belum berada di tiang goal.
Node dengan h terkecil selalu dieksplorasi lebih dulu (tanpa memperhitungkan g).
Biasanya cepat, tetapi solusi TIDAK dijamin optimal.

Jalankan:  python greedy.py            (input diketik)
           python greedy.py -k 4 -n 5
"""
import heapq
import itertools

from hanoi_common import build_path, run, successors, weighted_misplaced


def greedy(start, goal, k):
    stats = {"expanded": 0, "generated": 0, "max_frontier": 0}
    counter = itertools.count()     # penentu urutan bila h sama (FIFO)

    parent = {start: None}          # sekaligus berfungsi sebagai visited set
    frontier = [(weighted_misplaced(start, k), next(counter), start)]

    while frontier:
        _, _, state = heapq.heappop(frontier)

        if state == goal:
            return {"path": build_path(parent, state), **stats}
        stats["expanded"] += 1

        for nxt in successors(state, k):
            stats["generated"] += 1
            if nxt not in parent:
                parent[nxt] = state
                heapq.heappush(frontier, (weighted_misplaced(nxt, k), next(counter), nxt))

        stats["max_frontier"] = max(stats["max_frontier"], len(frontier))

    return {"path": [start], **stats}


if __name__ == "__main__":
    run("Greedy Best-First (h = cakram belum di goal)", greedy, "Tower of Hanoi - Greedy Best-First Search")

"""
astar.py - A* Search untuk Tower of Hanoi (k tiang, n cakram)

f(n) = g(n) + h(n)
  g(n) = total biaya (bobot) langkah dari state awal
  h(n) = jumlah BOBOT cakram yang BELUM berada di tiang goal

h admissible: setiap cakram yang belum di tiang goal butuh minimal 1 langkah,
sehingga h tidak pernah melebihi biaya sebenarnya -> A* menghasilkan solusi optimal.
(h juga consistent: satu langkah hanya mengubah status satu cakram.)

Jalankan:  python astar.py            (input diketik)
           python astar.py -k 4 -n 5
"""
import heapq
import itertools

from hanoi_common import build_path, run, successors_weighted, weighted_misplaced


def astar(start, goal, k):
    stats = {"expanded": 0, "generated": 0, "max_frontier": 0}
    counter = itertools.count()     # penentu urutan bila f dan g sama (agar tuple state tidak dibandingkan)

    g_cost = {start: 0}
    parent = {start: None}
    # elemen heap: (f, -g, urutan, state). -g -> bila f sama, pilih g lebih besar (lebih dekat ke goal)
    frontier = [(weighted_misplaced(start, k), 0, next(counter), start)]

    while frontier:
        _, _, _, state = heapq.heappop(frontier)

        if state == goal:           # goal test saat node diambil -> optimal
            return {"path": build_path(parent, state), **stats}
        stats["expanded"] += 1
        g = g_cost[state]

        for nxt, cost in successors_weighted(state, k):
            stats["generated"] += 1
            new_g = g + cost
            if nxt not in g_cost or new_g < g_cost[nxt]:
                g_cost[nxt] = new_g
                parent[nxt] = state
                f = new_g + weighted_misplaced(nxt, k)
                heapq.heappush(frontier, (f, -new_g, next(counter), nxt))

        stats["max_frontier"] = max(stats["max_frontier"], len(frontier))

    return {"path": [start], **stats}


if __name__ == "__main__":
    run("A* (h = cakram belum di goal)", astar, "Tower of Hanoi - A* Search")

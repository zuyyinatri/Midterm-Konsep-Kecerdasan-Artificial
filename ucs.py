"""
ucs.py - Uniform-Cost Search untuk Tower of Hanoi berbobot.

Pengganti BFS saat biaya langkah tidak seragam: node dengan g(n) terkecil
dieksplorasi lebih dulu, jadi solusi pertama yang ditemukan = biaya minimum.
"""
import heapq
import itertools

from hanoi_common import build_path, successors_weighted


def ucs(start, goal, k):
    stats = {"expanded": 0, "generated": 0, "max_frontier": 0}
    counter = itertools.count()

    g_cost = {start: 0}
    parent = {start: None}
    frontier = [(0, next(counter), start)]

    while frontier:
        g, _, state = heapq.heappop(frontier)
        if g > g_cost[state]:            # entri usang (sudah ada jalur lebih murah)
            continue
        if state == goal:
            return {"path": build_path(parent, state), **stats}
        stats["expanded"] += 1

        for nxt, cost in successors_weighted(state, k):
            stats["generated"] += 1
            new_g = g + cost
            if nxt not in g_cost or new_g < g_cost[nxt]:
                g_cost[nxt] = new_g
                parent[nxt] = state
                heapq.heappush(frontier, (new_g, next(counter), nxt))
        stats["max_frontier"] = max(stats["max_frontier"], len(frontier))

    return {"path": [start], **stats}


if __name__ == "__main__":
    from hanoi_common import run
    run("UCS", ucs, "Tower of Hanoi - Uniform-Cost Search")

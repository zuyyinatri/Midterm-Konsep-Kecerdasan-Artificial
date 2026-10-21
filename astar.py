import heapq
import itertools

from hanoi_common import build_path, run, successors_weighted, weighted_distance


def astar(start, goal, k):
    stats = {"expanded": 0, "generated": 0, "max_frontier": 0}
    counter = itertools.count()     # penentu urutan bila f dan g sama (agar tuple state tidak dibandingkan)

    g_cost = {start: 0}
    parent = {start: None}
    # elemen heap: (f, -g, urutan, state). -g -> bila f sama, pilih g lebih besar (lebih dekat ke goal)
    frontier = [(weighted_distance(start, k), 0, next(counter), start)]

    while frontier:
        _, neg_g, _, state = heapq.heappop(frontier)
        g = g_cost[state]
        if -neg_g > g:              # entri usang (sudah ada jalur lebih murah)
            continue

        if state == goal:           # goal test saat node diambil -> optimal
            return {"path": build_path(parent, state), **stats}
        stats["expanded"] += 1

        for nxt, cost in successors_weighted(state, k):
            stats["generated"] += 1
            new_g = g + cost
            if nxt not in g_cost or new_g < g_cost[nxt]:
                g_cost[nxt] = new_g
                parent[nxt] = state
                f = new_g + weighted_distance(nxt, k)
                heapq.heappush(frontier, (f, -new_g, next(counter), nxt))

        stats["max_frontier"] = max(stats["max_frontier"], len(frontier))

    return {"path": [start], **stats}


if __name__ == "__main__":
    run("A* (h = bobot x jarak ke goal)", astar, "Tower of Hanoi - A* Search")

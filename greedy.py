import heapq
import itertools

from hanoi_common import build_path, run, successors, weighted_distance


def greedy(start, goal, k):
    stats = {"expanded": 0, "generated": 0, "max_frontier": 0}
    counter = itertools.count()     # penentu urutan bila h sama (FIFO)

    parent = {start: None}          # sekaligus berfungsi sebagai visited set
    frontier = [(weighted_distance(start, k), next(counter), start)]

    while frontier:
        _, _, state = heapq.heappop(frontier)

        if state == goal:
            return {"path": build_path(parent, state), **stats}
        stats["expanded"] += 1

        for nxt in successors(state, k):
            stats["generated"] += 1
            if nxt not in parent:
                parent[nxt] = state
                heapq.heappush(frontier, (weighted_distance(nxt, k), next(counter), nxt))

        stats["max_frontier"] = max(stats["max_frontier"], len(frontier))

    return {"path": [start], **stats}


if __name__ == "__main__":
    run("Greedy Best-First (h = bobot x jarak ke goal)", greedy, "Tower of Hanoi - Greedy Best-First Search")

"""
bfs.py - Breadth-First Search untuk Tower of Hanoi (k tiang, n cakram)

Frontier: antrian FIFO. Node dieksplorasi level demi level sehingga solusi
pertama yang ditemukan adalah solusi dengan jumlah langkah paling sedikit
(optimal, karena setiap langkah berbiaya sama).

Jalankan:  python bfs.py            (input diketik)
           python bfs.py -k 4 -n 5
"""
from collections import deque

from hanoi_common import build_path, run, successors


def bfs(start, goal, k):
    stats = {"expanded": 0, "generated": 0, "max_frontier": 0}
    if start == goal:
        return {"path": [start], **stats}

    parent = {start: None}          # sekaligus berfungsi sebagai visited set
    frontier = deque([start])

    while frontier:
        state = frontier.popleft()
        stats["expanded"] += 1

        for nxt in successors(state, k):
            stats["generated"] += 1
            if nxt in parent:       # sudah pernah ditemukan
                continue
            parent[nxt] = state
            if nxt == goal:         # goal test saat generate -> langkah minimum
                return {"path": build_path(parent, nxt), **stats}
            frontier.append(nxt)

        stats["max_frontier"] = max(stats["max_frontier"], len(frontier))

    return {"path": [start], **stats}   # tidak tercapai untuk k >= 3


if __name__ == "__main__":
    run("BFS", bfs, "Tower of Hanoi - Breadth-First Search")

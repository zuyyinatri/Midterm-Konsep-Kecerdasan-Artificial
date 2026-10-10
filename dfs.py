"""
dfs.py - Depth-First Search untuk Tower of Hanoi (k tiang, n cakram)

Frontier: stack (LIFO). Pencarian masuk sedalam mungkin lebih dulu.
Memakai visited set (graph search) agar tidak berputar tanpa akhir.
Solusi pasti ditemukan, tetapi TIDAK dijamin optimal (jalur bisa sangat panjang).

Jalankan:  python dfs.py            (input diketik)
           python dfs.py -k 4 -n 5
"""
from hanoi_common import build_path, run, successors


def dfs(start, goal, k):
    stats = {"expanded": 0, "generated": 0, "max_frontier": 0}

    parent = {start: None}          # sekaligus berfungsi sebagai visited set
    frontier = [start]              # stack

    while frontier:
        state = frontier.pop()
        stats["expanded"] += 1

        if state == goal:
            return {"path": build_path(parent, state), **stats}

        for nxt in successors(state, k):
            stats["generated"] += 1
            if nxt not in parent:
                parent[nxt] = state
                frontier.append(nxt)

        stats["max_frontier"] = max(stats["max_frontier"], len(frontier))

    return {"path": [start], **stats}


if __name__ == "__main__":
    run("DFS", dfs, "Tower of Hanoi - Depth-First Search")

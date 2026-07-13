"""Graph analysis helpers: cycles, hotspots, dead nodes."""
from __future__ import annotations

from typing import Dict, List, Tuple


def find_cycles(adj: Dict[str, List[str]]) -> List[List[str]]:
    """Detect simple cycles using DFS (returns list of cycles as node lists)."""
    visited = set()
    stack = []
    cycles = []

    def dfs(node, path):
        if node in path:
            idx = path.index(node)
            cycles.append(path[idx:] + [node])
            return
        if node in visited:
            return
        path.append(node)
        for nbr in adj.get(node, []):
            dfs(nbr, path[:])
        visited.add(node)

    for n in adj:
        dfs(n, [])

    return cycles


def hotspots(adj: Dict[str, List[str]], top_n: int = 10) -> List[Tuple[str, int]]:
    """Return top_n nodes by out-degree + in-degree (simple hotspot heuristic)."""
    out_deg = {n: len(adj.get(n, [])) for n in adj}
    in_deg = {n: 0 for n in adj}
    for a, bs in adj.items():
        for b in bs:
            in_deg[b] = in_deg.get(b, 0) + 1

    score = {n: out_deg.get(n, 0) + in_deg.get(n, 0) for n in adj}
    ranked = sorted(score.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


def dead_nodes(adj: Dict[str, List[str]]) -> List[str]:
    """Nodes that have zero in-degree and zero out-degree (isolated) or only out-degree but never referenced."""
    in_deg = {n: 0 for n in adj}
    for a, bs in adj.items():
        for b in bs:
            in_deg[b] = in_deg.get(b, 0) + 1
    dead = [n for n, outs in adj.items() if len(outs) == 0 and in_deg.get(n, 0) == 0]
    return dead

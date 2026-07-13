"""Graph builder converts parser output into a graph data structure."""
from __future__ import annotations

from typing import Dict, List, Tuple


class GraphBuilder:
    """Builds a simple adjacency representation from nodes and edges."""

    def __init__(self):
        self.adj: Dict[str, List[str]] = {}

    def build_from_edges(self, nodes: List[str], edges: List[Tuple[str, str]]):
        for n in nodes:
            self.adj.setdefault(n, [])
        for a, b in edges:
            if a not in self.adj:
                self.adj[a] = []
            if b not in self.adj:
                self.adj[b] = []
            if b not in self.adj[a]:
                self.adj[a].append(b)

    def to_dict(self):
        return {"nodes": list(self.adj.keys()), "edges": [(a, b) for a, bs in self.adj.items() for b in bs], "adj": self.adj}

    def in_degrees(self) -> Dict[str, int]:
        deg = {n: 0 for n in self.adj}
        for a, bs in self.adj.items():
            for b in bs:
                deg[b] = deg.get(b, 0) + 1
        return deg

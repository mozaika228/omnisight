"""Simple graph metrics utilities."""
from __future__ import annotations

from typing import Dict, List


def degree_centrality(adj: Dict[str, List[str]]) -> Dict[str, float]:
    n = len(adj) if adj else 1
    scores = {node: (len(neigh) / (n - 1) if n > 1 else 0.0) for node, neigh in adj.items()}
    return scores

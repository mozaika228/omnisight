"""Simple Python repository parser.

Extracts modules and import relations to produce a module-level dependency graph.
This is intentionally lightweight and dependency-free — good for scaffolding.
"""
from __future__ import annotations

import ast
import os
from typing import Dict, List, Tuple


class PythonParser:
    """Parse Python files in a repository and return module import relations.

    Methods
    -------
    parse_repository(repo_path) -> (nodes, edges)
        nodes: list of module paths
        edges: list of (from_module, to_module)
    """

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def _iter_py_files(self) -> List[str]:
        files = []
        for root, _, filenames in os.walk(self.repo_path):
            # skip venv, .git and node_modules
            if any(p in root for p in (os.path.sep + "venv", os.path.sep + ".git", os.path.sep + "node_modules")):
                continue
            for fn in filenames:
                if fn.endswith(".py"):
                    files.append(os.path.join(root, fn))
        return files

    def _module_name_from_path(self, path: str) -> str:
        rel = os.path.relpath(path, self.repo_path)
        rel = rel.replace(os.path.sep, ".")
        if rel.endswith(".py"):
            rel = rel[: -3]
        # strip __init__ suffix
        if rel.endswith(".__init__"):
            rel = rel[: -9]
        return rel

    def parse_repository(self) -> Tuple[List[str], List[Tuple[str, str]]]:
        nodes: List[str] = []
        edges: List[Tuple[str, str]] = []

        files = self._iter_py_files()
        module_map: Dict[str, str] = {}
        for f in files:
            m = self._module_name_from_path(f)
            module_map[f] = m
            nodes.append(m)

        for f in files:
            m = module_map[f]
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    src = fh.read()
                tree = ast.parse(src)
            except Exception:
                # skip files we can't parse
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        edges.append((m, alias.name))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        edges.append((m, node.module))

        # normalize edges to known modules when possible
        norm_edges: List[Tuple[str, str]] = []
        known = set(nodes)
        for a, b in edges:
            # keep only top-level module name
            b_top = b.split(".")[0]
            # attempt to find matching known module
            matches = [n for n in nodes if n.startswith(b_top)]
            if matches:
                norm_edges.append((a, matches[0]))
            else:
                norm_edges.append((a, b_top))

        return nodes, norm_edges


if __name__ == "__main__":
    import sys
    p = PythonParser(sys.argv[1] if len(sys.argv) > 1 else ".")
    nodes, edges = p.parse_repository()
    print(f"Found {len(nodes)} modules and {len(edges)} edges")

"""Import Resolver scaffold.

Resolve module import paths to actual files/symbols in the `RepositoryIR`.
V1 provides heuristic/relative resolution and will be improved later to
handle tsconfig paths, package aliases, index files, and node resolution.
"""
from __future__ import annotations

import os
from typing import List

from ..ir import RepositoryIR, Symbol


class ImportResolver:
    def __init__(self, repo: RepositoryIR):
        self.repo = repo

    def resolve_module(self, from_path: str, module_spec: str) -> List[Symbol]:
        # Heuristic: handle relative paths './x' or '../y' by joining and
        # looking for a file with that path plus .ts/.tsx
        candidates: List[Symbol] = []
        if module_spec.startswith("."):
            base = os.path.dirname(from_path)
            candidate = os.path.normpath(os.path.join(base, module_spec))
            for ext in (".ts", ".tsx", ".d.ts"):
                p = candidate + ext
                if p in self.repo.files:
                    fr = self.repo.files[p]
                    # return all exported symbols from that file
                    for s in fr.symbols:
                        candidates.append(s)
        else:
            # non-relative: try to match module name to file basenames
            for p, fr in self.repo.files.items():
                if os.path.splitext(os.path.basename(p))[0] == module_spec:
                    candidates.extend(fr.symbols)
        return candidates

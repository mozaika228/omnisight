"""Symbol Resolver scaffold.

This module will contain logic to resolve symbol references across the
`RepositoryIR`: mapping call sites/imports/identifiers to canonical `Symbol`
entries. For now it's a minimal scaffold with a simple name-based resolver
that will be expanded to use scopes, imports, and type information.
"""
from __future__ import annotations

from typing import Dict, List

from ..ir import RepositoryIR, Symbol


class SymbolResolver:
    def __init__(self, repo: RepositoryIR):
        self.repo = repo
        self.index: Dict[str, Symbol] = repo.symbol_index()

    def resolve_by_name(self, name: str) -> List[Symbol]:
        # naive exact-name match across repository
        res: List[Symbol] = []
        for s in self.index.values():
            if s.name == name:
                res.append(s)
        return res

    def resolve_call(self, call_name: str):
        # Return best-effort resolution for call sites; to be improved
        return self.resolve_by_name(call_name)

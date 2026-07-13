"""Semantic Resolver scaffold.

Provides a language-agnostic interface `SemanticResolver` and a
TypeScript-specific starter `TypeScriptSemanticResolver` that composes
symbol/scope/import resolvers. This is the foundation for resolving
definitions and references across the `RepositoryIR`.
"""
from __future__ import annotations

from typing import List, Optional

from ..ir import RepositoryIR, Symbol
from .symbol_resolver import SymbolResolver


class SemanticResolver:
    def __init__(self, repo: RepositoryIR):
        self.repo = repo

    def resolve_symbols(self, name: str) -> List[Symbol]:
        raise NotImplementedError()

    def resolve_call(self, call_name: str) -> List[Symbol]:
        raise NotImplementedError()

    def resolve_import(self, source_path: str, import_target: str) -> List[Symbol]:
        raise NotImplementedError()


class TypeScriptSemanticResolver(SemanticResolver):
    def __init__(self, repo: RepositoryIR):
        super().__init__(repo)
        self.symbol_resolver = SymbolResolver(repo)

    def resolve_symbols(self, name: str) -> List[Symbol]:
        # delegate to symbol resolver for V1
        return self.symbol_resolver.resolve_by_name(name)

    def resolve_call(self, call_name: str) -> List[Symbol]:
        return self.symbol_resolver.resolve_call(call_name)

    def resolve_import(self, source_path: str, import_target: str) -> List[Symbol]:
        # TODO: implement module resolution (relative/absolute) and default export handling
        # V1: attempt to resolve by the imported module basename
        # e.g., './auth' -> look for symbols named like 'auth' or exported names
        return self.symbol_resolver.resolve_by_name(import_target)

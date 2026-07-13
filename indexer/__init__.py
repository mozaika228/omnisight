"""Indexer package: builds Repository IR from source files using language-specific parsers.

High-level responsibilities:
- load language parsers (tree-sitter)
- convert AST -> Repository IR (symbols, imports, calls)
- provide a uniform API for downstream graph builders
"""

from .ir import RepositoryIR

__all__ = ["RepositoryIR"]

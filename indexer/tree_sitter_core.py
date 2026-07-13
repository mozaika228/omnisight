"""Tree-sitter integration helpers (lightweight, import-guarded).

This module provides a small helper to load a tree-sitter language parser
and parse source code. It avoids hard dependency at import time.
"""
from __future__ import annotations

from typing import Optional


def parse_with_treesitter(source: str, language_name: str) -> Optional[object]:
    """Parse source with tree-sitter for given language.

    Returns the parse tree object or None if tree_sitter not available.
    """
    try:
        from tree_sitter import Language, Parser
    except Exception:
        # tree-sitter not installed in environment
        return None

    # Note: building Language requires compiled grammar .so/.dll files.
    # In production, prebuild grammars and load them here. This stub
    # assumes a `build/my-languages.so` exists and contains the languages.
    try:
        LANG_SO = "build/my-languages.so"
        lang = Language(LANG_SO, language_name)
        parser = Parser()
        parser.set_language(lang)
        tree = parser.parse(bytes(source, "utf8"))
        return tree
    except Exception:
        return None

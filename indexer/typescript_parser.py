"""TypeScript parser using tree-sitter (stub).

This module demonstrates how to convert a TypeScript AST (tree-sitter)
into the Repository IR. It is intentionally small and returns a minimal
FileIR when tree-sitter isn't available.
"""
from __future__ import annotations

from typing import Optional
from .tree_sitter_core import parse_with_treesitter
from .ir import RepositoryIR, FileIR, Symbol, ImportRelation, Location
import os


def parse_typescript_file(path: str) -> FileIR:
    src = ""
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()

    tree = parse_with_treesitter(src, "typescript")
    file_ir = FileIR(path=path)

    if tree is None:
        # Fallback: minimal import extraction by scanning lines
        for i, line in enumerate(src.splitlines(), start=1):
            line = line.strip()
            if line.startswith("import "):
                # crude extraction
                # import X from 'module'
                try:
                    parts = line.split("from")
                    target = parts[-1].strip().strip("'\";")
                    file_ir.imports.append(ImportRelation(source=path, target=target, location=Location(path, i, 1)))
                except Exception:
                    continue
        return file_ir

    # TODO: traverse tree and extract symbols/imports; placeholder for now
    return file_ir


def parse_repository_typescript(root_path: str) -> RepositoryIR:
    repo = RepositoryIR()
    for dirpath, _, files in os.walk(root_path):
        if dirpath.endswith("node_modules"):
            continue
        for fn in files:
            if fn.endswith(".ts") or fn.endswith(".tsx"):
                p = os.path.join(dirpath, fn)
                try:
                    fr = parse_typescript_file(p)
                    repo.add_file(fr)
                except Exception:
                    continue
    return repo

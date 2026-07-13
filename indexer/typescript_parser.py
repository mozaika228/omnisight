"""TypeScript parser using tree-sitter (with robust fallback).

Converts TypeScript source files into Repository IR (`FileIR`, `Symbol`,
`ImportRelation`, `FunctionIR`). If tree-sitter is available and grammars
are built, it will use the parsed tree for more accurate locations; otherwise
it falls back to a regex-based extractor to produce a usable IR for downstream
graph building and analysis.
"""
from __future__ import annotations

import os
import re
from typing import Optional

from .tree_sitter_core import parse_with_treesitter
from .ir import RepositoryIR, FileIR, Symbol, ImportRelation, Location, FunctionIR


_IMPORT_RE = re.compile(r"import\s+(?:[\w\s{},*]+)\s+from\s+['\"]([^'\"]+)['\"]")
_EXPORT_RE = re.compile(r"export\s+(?:default\s+)?(?:class|function|const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)")
_FUNC_RE = re.compile(r"function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)")
_CLASS_RE = re.compile(r"class\s+([A-Za-z_][A-Za-z0-9_]*)")
_CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def _make_location_from_point(path: str, point) -> Location:
    # tree-sitter point is (row, column) 0-based
    try:
        row, col = point
        return Location(file=path, line=row + 1, column=col + 1)
    except Exception:
        return Location(file=path, line=1, column=1)


def parse_typescript_file(path: str) -> FileIR:
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()

    file_ir = FileIR(path=path)
    tree = parse_with_treesitter(src, "typescript")

    if tree is not None:
        src_bytes = bytes(src, "utf8")

        def walk(node, class_context: Optional[str] = None):
            # node.type gives node kind like 'import_statement', 'function_declaration', etc.
            ntype = node.type
            text = src_bytes[node.start_byte:node.end_byte].decode("utf8", "replace")

            if "import" in ntype or ntype == "import_statement":
                m = _IMPORT_RE.search(text)
                if m:
                    target = m.group(1)
                    loc = _make_location_from_point(path, node.start_point)
                    file_ir.imports.append(ImportRelation(source=path, target=target, location=loc))

            if ntype in ("function_declaration", "method_definition") or text.strip().startswith("function "):
                m = _FUNC_RE.search(text)
                if m:
                    name = m.group(1)
                    params = [p.strip() for p in m.group(2).split(",") if p.strip()] if m.group(2) else []
                    loc = _make_location_from_point(path, node.start_point)
                    calls = [c.group(1) for c in _CALL_RE.finditer(text)]
                    file_ir.functions.append(FunctionIR(name=name, parameters=params, returns=None, calls=calls, location=loc))
                    file_ir.symbols.append(Symbol(id=f"{path}:{name}", name=name, kind="function", language="typescript", location=loc))

            if ntype == "class_declaration" or text.strip().startswith("class "):
                m = _CLASS_RE.search(text)
                if m:
                    name = m.group(1)
                    loc = _make_location_from_point(path, node.start_point)
                    file_ir.symbols.append(Symbol(id=f"{path}:{name}", name=name, kind="class", language="typescript", location=loc))

            # recurse
            for ch in node.children:
                walk(ch, class_context=class_context)

        walk(tree.root_node)
        return file_ir

    # Fallback: regex-based extraction
    # Extract imports
    for i, line in enumerate(src.splitlines(), start=1):
        im = _IMPORT_RE.search(line)
        if im:
            target = im.group(1)
            file_ir.imports.append(ImportRelation(source=path, target=target, location=Location(file=path, line=i, column=1)))

    # Extract exports, functions, classes and calls (crude but useful)
    for m in _EXPORT_RE.finditer(src):
        name = m.group(1)
        file_ir.symbols.append(Symbol(id=f"{path}:{name}", name=name, kind="export", language="typescript", location=Location(file=path, line=1, column=1)))

    for m in _FUNC_RE.finditer(src):
        name = m.group(1)
        params = [p.strip() for p in m.group(2).split(",") if p.strip()] if m.group(2) else []
        # crude line estimate
        start = src[: m.start()].count("\n") + 1
        calls = [c.group(1) for c in _CALL_RE.finditer(src[m.start(): m.end()])]
        file_ir.functions.append(FunctionIR(name=name, parameters=params, returns=None, calls=calls, location=Location(file=path, line=start, column=1)))
        file_ir.symbols.append(Symbol(id=f"{path}:{name}", name=name, kind="function", language="typescript", location=Location(file=path, line=start, column=1)))

    for m in _CLASS_RE.finditer(src):
        name = m.group(1)
        start = src[: m.start()].count("\n") + 1
        file_ir.symbols.append(Symbol(id=f"{path}:{name}", name=name, kind="class", language="typescript", location=Location(file=path, line=start, column=1)))

    # calls across file
    # Use simple heuristic: find call sites and attach to nearest function if any
    # For fallback this is coarse but usable.

    return file_ir


def parse_repository_typescript(root_path: str) -> RepositoryIR:
    repo = RepositoryIR()
    for dirpath, _, files in os.walk(root_path):
        if "node_modules" in dirpath:
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


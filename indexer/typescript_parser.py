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
_EXPORT_RE = re.compile(r"export\s+(?:default\s+)?(?:class|function|const|let|var|type|interface|enum)\s+([A-Za-z_][A-Za-z0-9_]*)")
_FUNC_RE = re.compile(r"function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)\s*(?::\s*([A-Za-z0-9_<>\[\]{}., ]+))?")
_CLASS_RE = re.compile(r"class\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s+extends\s+([A-Za-z0-9_.]+))?(?:\s+implements\s+([A-Za-z0-9_. ,<>]+))?")
_CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_INTERFACE_RE = re.compile(r"interface\s+([A-Za-z_][A-Za-z0-9_]*)")
_ENUM_RE = re.compile(r"enum\s+([A-Za-z_][A-Za-z0-9_]*)")
_TYPE_ALIAS_RE = re.compile(r"type\s+([A-Za-z_][A-Za-z0-9_]*)\s*=")
_VAR_RE = re.compile(r"(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)")
_DECORATOR_RE = re.compile(r"@([A-Za-z_][A-Za-z0-9_]*)")
_JSDOC_RE = re.compile(r"/\*\*([\s\S]*?)\*/", re.MULTILINE)


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
        # Use the TypeScriptVisitor when tree-sitter is available for robust AST traversal
        try:
            from .visitors.typescript_visitor import TypeScriptVisitor

            visitor = TypeScriptVisitor(src=src, src_bytes=src_bytes, path=path, file_ir=file_ir)
            visitor.visit(tree.root_node)
            return file_ir
        except Exception:
            # If visitor fails for any reason, fall back to the previous guarded walker
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
                    returns = m.group(3).strip() if m.group(3) else None
                    loc = _make_location_from_point(path, node.start_point)
                    calls = [c.group(1) for c in _CALL_RE.finditer(text)]
                    func_ir = FunctionIR(name=name, parameters=params, returns=returns, calls=calls, location=loc)
                    # detect decorators above (simple heuristic)
                    decs = _DECORATOR_RE.findall(text)
                    func_ir.decorators = decs
                    # parameters detail (name:type) approximate
                    params_detail = []
                    for p in params:
                        if ':' in p:
                            pn, pt = map(str.strip, p.split(':', 1))
                        else:
                            pn, pt = p, None
                        params_detail.append({"name": pn, "type": pt})
                    func_ir.parameters_detail = params_detail
                    file_ir.functions.append(func_ir)
                    stable_id = Symbol.make_stable_id(path, "function", name, loc.line)
                    file_ir.symbols.append(Symbol(id=stable_id, name=name, kind="function", language="typescript", location=loc))

            if ntype == "class_declaration" or text.strip().startswith("class "):
                m = _CLASS_RE.search(text)
                if m:
                    name = m.group(1)
                    extends = m.group(2)
                    implements = m.group(3)
                    loc = _make_location_from_point(path, node.start_point)
                    stable_id = Symbol.make_stable_id(path, "class", name, loc.line)
                    file_ir.symbols.append(Symbol(id=stable_id, name=name, kind="class", language="typescript", location=loc))
                    file_ir.classes.append({"name": name, "extends": extends, "implements": implements, "location": loc})
                    # capture JSDoc above class (heuristic)
                    prev = src_bytes[: node.start_byte].decode("utf8", "replace")
                    doc_matches = list(_JSDOC_RE.finditer(prev))
                    if doc_matches:
                        doc = doc_matches[-1].group(1).strip()
                        file_ir.docs.append({"target": name, "doc": doc, "location": loc})

            # interfaces, enums, type aliases
            if _INTERFACE_RE.search(text):
                m = _INTERFACE_RE.search(text)
                name = m.group(1)
                loc = _make_location_from_point(path, node.start_point)
                file_ir.interfaces.append({"name": name, "location": loc})
                file_ir.symbols.append(Symbol(id=Symbol.make_stable_id(path, "interface", name, loc.line), name=name, kind="interface", language="typescript", location=loc))

            if _ENUM_RE.search(text):
                m = _ENUM_RE.search(text)
                name = m.group(1)
                loc = _make_location_from_point(path, node.start_point)
                file_ir.enums.append({"name": name, "location": loc})
                file_ir.symbols.append(Symbol(id=Symbol.make_stable_id(path, "enum", name, loc.line), name=name, kind="enum", language="typescript", location=loc))

            if _TYPE_ALIAS_RE.search(text):
                m = _TYPE_ALIAS_RE.search(text)
                name = m.group(1)
                loc = _make_location_from_point(path, node.start_point)
                file_ir.type_aliases.append({"name": name, "location": loc})
                file_ir.symbols.append(Symbol(id=Symbol.make_stable_id(path, "type_alias", name, loc.line), name=name, kind="type_alias", language="typescript", location=loc))

            # variables
            for vm in _VAR_RE.finditer(text):
                vname = vm.group(1)
                loc = _make_location_from_point(path, node.start_point)
                file_ir.variables.append({"name": vname, "location": loc})
                file_ir.symbols.append(Symbol(id=Symbol.make_stable_id(path, "variable", vname, loc.line), name=vname, kind="variable", language="typescript", location=loc))

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


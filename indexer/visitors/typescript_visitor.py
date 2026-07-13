"""Visitor for TypeScript tree-sitter AST to populate FileIR.

This visitor focuses on extracting language constructs reliably from the
tree-sitter parse tree and avoids regex when tree-sitter is available.
"""
from __future__ import annotations

from typing import Optional

from ..ir import FileIR, ImportRelation, FunctionIR, Symbol, Location


class TypeScriptVisitor:
    def __init__(self, src: str, src_bytes: bytes, path: str, file_ir: FileIR):
        self.src = src
        self.src_bytes = src_bytes
        self.path = path
        self.file_ir = file_ir

    def _text(self, node) -> str:
        return self.src_bytes[node.start_byte:node.end_byte].decode("utf8", "replace")

    def _loc(self, node) -> Location:
        try:
            r, c = node.start_point
            return Location(file=self.path, line=r + 1, column=c + 1)
        except Exception:
            return Location(file=self.path, line=1, column=1)

    def visit(self, node, class_context: Optional[str] = None):
        t = node.type
        # dispatch based on node type
        if t in ("import_statement", "import_clause"):
            self.visit_import(node)
        elif t in ("export_statement", "export_clause"):
            self.visit_export(node)
        elif t in ("class_declaration",):
            self.visit_class(node)
        elif t in ("function_declaration",):
            self.visit_function(node)
        elif t in ("method_definition",):
            self.visit_method(node, class_context=class_context)
        elif t in ("call_expression",):
            self.visit_call(node)
        elif t in ("new_expression",):
            self.visit_new(node)
        elif t in ("lexical_declaration", "variable_statement", "variable_declaration"):
            self.visit_variable(node)
        elif t in ("interface_declaration",):
            self.visit_interface(node)
        elif t in ("enum_declaration",):
            self.visit_enum(node)
        elif t in ("type_alias_declaration",):
            self.visit_type_alias(node)
        elif t in ("decorator",):
            # decorators are attached to other nodes; capture when seen
            pass

        # descend into children; pass class context when inside class
        for ch in node.children:
            # if we are visiting class body, set context
            if node.type == "class_declaration":
                self.visit(ch, class_context=self._class_name(node))
            else:
                self.visit(ch, class_context=class_context)

    def _class_name(self, node) -> Optional[str]:
        # simple heuristic: find identifier child
        for ch in node.children:
            if ch.type == "identifier":
                return self._text(ch).strip()
        return None

    def visit_import(self, node):
        # find module string child
        text = self._text(node)
        # fallback simple extraction: look for quoted module text
        import_target = None
        for ch in node.children:
            if ch.type == "string":
                val = self._text(ch).strip()
                if val.startswith(('"', "'")) and val.endswith(('"', "'")):
                    import_target = val[1:-1]
                    break
        if import_target:
            self.file_ir.imports.append(ImportRelation(source=self.path, target=import_target, location=self._loc(node)))

    def visit_export(self, node):
        # capture exported identifier names when possible
        for ch in node.children:
            if ch.type == "identifier":
                name = self._text(ch).strip()
                self.file_ir.exports.append(name)
                self.file_ir.symbols.append(Symbol(id=f"{self.path}:{name}", name=name, kind="export", language="typescript", location=self._loc(ch)))

    def visit_class(self, node):
        name = self._class_name(node) or "<anon>"
        loc = self._loc(node)
        self.file_ir.symbols.append(Symbol(id=Symbol.make_stable_id(self.path, "class", name, loc.line), name=name, kind="class", language="typescript", location=loc))
        # capture heritage (extends / implements)
        extends = None
        implements = None
        for ch in node.children:
            if ch.type == "extends_clause":
                extends = self._text(ch).replace("extends", "").strip()
            if ch.type == "implements_clause":
                implements = self._text(ch).replace("implements", "").strip()
        self.file_ir.classes.append({"name": name, "extends": extends, "implements": implements, "location": loc})

    def visit_function(self, node):
        # name child may be identifier, or anonymous
        name = None
        params = []
        returns = None
        generics = []
        for ch in node.children:
            if ch.type == "identifier":
                name = self._text(ch).strip()
            if ch.type == "formal_parameters":
                # extract parameter identifiers
                for p in ch.named_children:
                    if p.type == "identifier":
                        params.append(self._text(p).strip())
                    elif p.type == "required_parameter":
                        # param might be a pattern with identifier child
                        for c in p.children:
                            if c.type == "identifier":
                                params.append(self._text(c).strip())
            if ch.type == "type_parameters":
                generics.append(self._text(ch).strip())
            if ch.type == "type_annotation":
                returns = self._text(ch).strip()

        if not name:
            name = "<anon>"
        loc = self._loc(node)
        func = FunctionIR(name=name, parameters=params, returns=returns, calls=[], location=loc)
        func.generics = generics
        # find call expressions inside function body
        calls = []
        stack = [node]
        while stack:
            cur = stack.pop()
            if cur.type == "call_expression":
                # function being called is often the first child
                if len(cur.children) > 0:
                    target = cur.children[0]
                    if target.type == "identifier":
                        calls.append(self._text(target).strip())
                    else:
                        # try to extract text
                        calls.append(self._text(target).split("(", 1)[0].strip())
            for c in cur.children:
                stack.append(c)

        func.calls = calls
        self.file_ir.functions.append(func)
        self.file_ir.symbols.append(Symbol(id=Symbol.make_stable_id(self.path, "function", name, loc.line), name=name, kind="function", language="typescript", location=loc))

    def visit_method(self, node, class_context: Optional[str] = None):
        # method definitions inside classes
        name = None
        params = []
        for ch in node.children:
            if ch.type == "property_identifier" or ch.type == "identifier":
                name = self._text(ch).strip()
            if ch.type == "formal_parameters":
                for p in ch.named_children:
                    if p.type == "identifier":
                        params.append(self._text(p).strip())
        if not name:
            name = "<anon_method>"
        fullname = f"{class_context}.{name}" if class_context else name
        loc = self._loc(node)
        func = FunctionIR(name=fullname, parameters=params, returns=None, calls=[], location=loc)
        self.file_ir.functions.append(func)
        self.file_ir.symbols.append(Symbol(id=Symbol.make_stable_id(self.path, "method", fullname, loc.line), name=fullname, kind="method", language="typescript", location=loc))

    def visit_call(self, node):
        # record call sites; best-effort extraction
        if len(node.children) > 0:
            target = node.children[0]
            if target.type == "identifier":
                name = self._text(target).strip()
                loc = self._loc(node)
                self.file_ir.functions.append(FunctionIR(name=f"__call__:{name}", parameters=[], returns=None, calls=[], location=loc))

    def visit_new(self, node):
        # new expressions indicate constructor usage; capture target
        if len(node.children) > 0:
            target = node.children[0]
            if target.type == "identifier":
                name = self._text(target).strip()
                loc = self._loc(node)
                self.file_ir.functions.append(FunctionIR(name=f"__new__:{name}", parameters=[], returns=None, calls=[], location=loc))

    def visit_variable(self, node):
        # capture declared identifiers
        for ch in node.named_children:
            if ch.type == "variable_declarator":
                for idn in ch.named_children:
                    if idn.type == "identifier":
                        v = self._text(idn).strip()
                        loc = self._loc(idn)
                        self.file_ir.variables.append({"name": v, "location": loc})
                        self.file_ir.symbols.append(Symbol(id=Symbol.make_stable_id(self.path, "variable", v, loc.line), name=v, kind="variable", language="typescript", location=loc))

    def visit_interface(self, node):
        name = None
        for ch in node.children:
            if ch.type == "identifier":
                name = self._text(ch).strip()
        if not name:
            name = "<anon_interface>"
        loc = self._loc(node)
        self.file_ir.interfaces.append({"name": name, "location": loc})
        self.file_ir.symbols.append(Symbol(id=Symbol.make_stable_id(self.path, "interface", name, loc.line), name=name, kind="interface", language="typescript", location=loc))

    def visit_enum(self, node):
        name = None
        for ch in node.children:
            if ch.type == "identifier":
                name = self._text(ch).strip()
        if not name:
            name = "<anon_enum>"
        loc = self._loc(node)
        self.file_ir.enums.append({"name": name, "location": loc})
        self.file_ir.symbols.append(Symbol(id=Symbol.make_stable_id(self.path, "enum", name, loc.line), name=name, kind="enum", language="typescript", location=loc))

    def visit_type_alias(self, node):
        name = None
        for ch in node.children:
            if ch.type == "type_identifier" or ch.type == "identifier":
                name = self._text(ch).strip()
        if not name:
            name = "<anon_type>"
        loc = self._loc(node)
        self.file_ir.type_aliases.append({"name": name, "location": loc})
        self.file_ir.symbols.append(Symbol(id=Symbol.make_stable_id(self.path, "type_alias", name, loc.line), name=name, kind="type_alias", language="typescript", location=loc))

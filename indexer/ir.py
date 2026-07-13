"""Repository Intermediate Representation (IR) types.

These are language-agnostic models used across OmniSight.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import hashlib


@dataclass
class Location:
    file: str
    line: int
    column: int


@dataclass
class Symbol:
    id: str
    name: str
    kind: str  # e.g., 'function', 'class', 'variable', 'interface'
    language: str
    location: Location
    meta: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def make_stable_id(path: str, kind: str, name: str, line: int) -> str:
        # stable id composed of path, kind, name and line hashed for compactness
        raw = f"{path}::{kind}::{name}::{line}"
        h = hashlib.sha1(raw.encode("utf8")).hexdigest()[:12]
        return f"{raw}::{h}"


@dataclass
class ImportRelation:
    source: str  # importing symbol or file
    target: str  # imported module or symbol
    location: Optional[Location] = None


@dataclass
class FunctionIR:
    name: str
    parameters: List[str]
    returns: Optional[str]
    calls: List[str] = field(default_factory=list)
    location: Optional[Location] = None
    decorators: List[str] = field(default_factory=list)
    generics: List[str] = field(default_factory=list)
    parameters_detail: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FileIR:
    path: str
    symbols: List[Symbol] = field(default_factory=list)
    imports: List[ImportRelation] = field(default_factory=list)
    functions: List[FunctionIR] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    interfaces: List[Dict[str, Any]] = field(default_factory=list)
    enums: List[Dict[str, Any]] = field(default_factory=list)
    type_aliases: List[Dict[str, Any]] = field(default_factory=list)
    variables: List[Dict[str, Any]] = field(default_factory=list)
    docs: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    modules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RepositoryIR:
    files: Dict[str, FileIR] = field(default_factory=dict)

    def add_file(self, file_ir: FileIR):
        self.files[file_ir.path] = file_ir

    def all_symbols(self) -> List[Symbol]:
        res: List[Symbol] = []
        for f in self.files.values():
            res.extend(f.symbols)
        return res

    def symbol_index(self) -> Dict[str, Symbol]:
        idx: Dict[str, Symbol] = {}
        for f in self.files.values():
            for s in f.symbols:
                idx[s.id] = s
        return idx

    def to_summary(self) -> Dict[str, int]:
        return {
            "files": len(self.files),
            "symbols": len(self.all_symbols()),
            "functions": sum(len(f.functions) for f in self.files.values()),
        }

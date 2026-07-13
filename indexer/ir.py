"""Repository Intermediate Representation (IR) types.

These are language-agnostic models used across OmniSight.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


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


@dataclass
class FileIR:
    path: str
    symbols: List[Symbol] = field(default_factory=list)
    imports: List[ImportRelation] = field(default_factory=list)
    functions: List[FunctionIR] = field(default_factory=list)


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

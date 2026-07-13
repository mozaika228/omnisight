"""FastAPI router for DevGraph analysis mode."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from parser.python import PythonParser
from graph.builder import GraphBuilder
from graph.analyzer import find_cycles, hotspots, dead_nodes

router = APIRouter()


class AnalyzeRequest(BaseModel):
    repo_path: str


class AnalyzeResponse(BaseModel):
    nodes: list
    edges: list
    cycles: list
    hotspots: list
    dead_nodes: list


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_repo(req: AnalyzeRequest):
    try:
        parser = PythonParser(req.repo_path)
        nodes, edges = parser.parse_repository()

        builder = GraphBuilder()
        builder.build_from_edges(nodes, edges)
        adj = builder.adj

        cycles = find_cycles(adj)
        hs = hotspots(adj, top_n=20)
        dead = dead_nodes(adj)

        return AnalyzeResponse(nodes=list(adj.keys()), edges=[(a, b) for a, bs in adj.items() for b in bs], cycles=cycles, hotspots=hs, dead_nodes=dead)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

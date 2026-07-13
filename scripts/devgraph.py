from __future__ import annotations

import os
import re
import json
import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "docs" / "devgraph-data.json"
OUTPUT_HTML = ROOT / "docs" / "devgraph.html"

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".next",
    ".turbo",
    "dist",
    "build",
    "coverage",
    "runs",
    "pytest-cache-files-0ciqops3",
    "pytest-cache-files-5zuar9kg",
}

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cs",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
}

IMPORT_PATTERNS = [
    ("py", re.compile(r"^\s*(?:from\s+([A-Za-z0-9_\.]+)\s+import|import\s+([A-Za-z0-9_\.]+))", re.M)),
    ("js", re.compile(r"(?:import|export)\s+(?:[^'\"]*?\s+from\s+)?['\"]([^'\"]+)['\"]|require\(\s*['\"]([^'\"]+)['\"]\s*\)")),
    ("java", re.compile(r"\bimport\s+([A-Za-z0-9_.$]+)\s*;")),
    ("cs", re.compile(r"\busing\s+([A-Za-z0-9_.$]+)\s*;")),
    ("rs", re.compile(r"\buse\s+([^;]+);")),
]


class GraphBuilder:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.nodes: List[Dict[str, object]] = []
        self.edges: List[Dict[str, object]] = []
        self.node_index: Dict[str, Dict[str, object]] = {}
        self.file_paths: List[Path] = []

    def collect_files(self) -> None:
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in IGNORE_DIRS for part in path.parts):
                continue
            if path.suffix.lower() in SOURCE_EXTENSIONS:
                self.file_paths.append(path)

    def add_node(self, rel_path: str, language: str) -> None:
        if rel_path in self.node_index:
            return
        node = {
            "id": rel_path,
            "label": rel_path.split("/")[-1],
            "path": rel_path,
            "language": language,
            "group": rel_path.split("/")[0] if "/" in rel_path else "root",
        }
        self.node_index[rel_path] = node
        self.nodes.append(node)

    def add_edge(self, source: str, target: str, import_name: str) -> None:
        if source == target:
            return
        if any(e["source"] == source and e["target"] == target for e in self.edges):
            return
        self.edges.append({
            "source": source,
            "target": target,
            "import": import_name,
        })

    def resolve_local_target(self, import_name: str, current_file: Path) -> Optional[str]:
        name = import_name.strip().strip('"\'')
        if not name or name.startswith("http") or name.startswith("#"):
            return None

        if name.startswith("."):
            base = current_file.parent / name
        else:
            base = self.root / name

        candidates: List[Path] = []
        raw = Path(name)
        if name.startswith(".") or name.startswith("/"):
            candidates.append(base)
        else:
            candidates.append(self.root / name)

        for ext in ["", ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cs", ".go", ".rs", ".cpp", ".c", ".h", ".hpp"]:
            candidates.append(Path(str(base) + ext))
            candidates.append(Path(str(base)) / f"index{ext}")
            candidates.append(Path(str(base)) / f"__init__{ext}")

        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                try:
                    return candidate.relative_to(self.root).as_posix()
                except ValueError:
                    return candidate.as_posix()

        if "." in name and "/" not in name:
            dotted = name.replace(".", "/")
            for ext in ["", ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cs", ".go", ".rs", ".cpp", ".c", ".h", ".hpp"]:
                candidate = self.root / f"{dotted}{ext}"
                if candidate.exists() and candidate.is_file():
                    return candidate.relative_to(self.root).as_posix()

        return None

    def parse_file(self, path: Path) -> None:
        rel_path = path.relative_to(self.root).as_posix()
        suffix = path.suffix.lower()
        language = "text"
        if suffix == ".py":
            language = "python"
        elif suffix in {".js", ".jsx"}:
            language = "javascript"
        elif suffix in {".ts", ".tsx"}:
            language = "typescript"
        elif suffix == ".java":
            language = "java"
        elif suffix == ".cs":
            language = "csharp"
        elif suffix == ".go":
            language = "go"
        elif suffix == ".rs":
            language = "rust"

        self.add_node(rel_path, language)

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return

        for kind, pattern in IMPORT_PATTERNS:
            for match in pattern.finditer(text):
                import_name = match.group(1) or match.group(2) or ""
                if not import_name:
                    continue
                if import_name.startswith("http") or import_name.startswith("#"):
                    continue
                target = self.resolve_local_target(import_name, path)
                if target:
                    self.add_node(target, language)
                    self.add_edge(rel_path, target, import_name)

    def build(self) -> Dict[str, object]:
        self.collect_files()
        for path in self.file_paths:
            self.parse_file(path)
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "stats": {
                "files": len(self.nodes),
                "links": len(self.edges),
            },
        }


def write_html(data: Dict[str, object]) -> None:
    html = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>DevGraph Prototype</title>
  <style>
    :root { color-scheme: dark; }
    body { margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #07111f; color: #e8eefc; }
    .layout { display: grid; grid-template-columns: 320px 1fr; height: 100vh; }
    .panel { padding: 16px; background: #0d1727; border-right: 1px solid #233046; overflow: auto; }
    .panel h1 { font-size: 20px; margin-top: 0; }
    .panel input { width: 100%; padding: 8px 10px; border-radius: 8px; border: 1px solid #334a66; background: #101d31; color: white; margin-top: 8px; }
    .panel .hint { font-size: 12px; color: #8fa6ca; margin-top: 8px; }
    .card { background: #101d31; border: 1px solid #233046; border-radius: 10px; padding: 10px; margin-top: 12px; }
    .card strong { display: block; margin-bottom: 6px; }
    .stats { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
    .chip { background: #12243d; border: 1px solid #2a4568; border-radius: 999px; padding: 4px 8px; font-size: 12px; }
    svg { width: 100%; height: 100%; display: block; background: radial-gradient(circle at top, #12223d, #07111f 65%); cursor: grab; }
    .node { cursor: pointer; }
    .node-label { font-size: 12px; fill: #f3f7ff; pointer-events: none; }
    .edge { stroke: rgba(125, 180, 255, 0.25); stroke-width: 1.2; }
    .edge.active { stroke: rgba(255, 255, 255, 0.8); }
    .node.active circle { stroke: #ffffff; stroke-width: 2.5; }
    .node.highlight circle { fill: #f7b731; }
    .node.dim circle { fill: #334a66; opacity: 0.7; }
  </style>
</head>
<body>
  <div class=\"layout\">
    <aside class=\"panel\">
      <h1>DevGraph Prototype</h1>
      <p>Interactive dependency map for a repository.</p>
      <input id=\"search\" placeholder=\"Search for auth, api, services...\" />
      <div class=\"hint\">Type a term to highlight relevant files and their neighbors.</div>
      <div class=\"card\" id=\"details\">Select a node to inspect impact.</div>
      <div class=\"stats\">
        <span class=\"chip\" id=\"fileCount\">Files: 0</span>
        <span class=\"chip\" id=\"linkCount\">Links: 0</span>
      </div>
      <div class=\"card\">
        <strong>What this prototype can do</strong>
        <ul>
          <li>Map import-based dependencies</li>
          <li>Highlight a file and its immediate impact</li>
          <li>Answer questions like “where does auth start?”</li>
        </ul>
      </div>
    </aside>
    <main>
      <svg id=\"graph\" viewBox=\"0 0 1200 900\"></svg>
    </main>
  </div>
  <script>
    const data = JSON.parse(document.currentScript.previousElementSibling.textContent || '{}');
  </script>
  <script>
    const svg = document.getElementById('graph');
    const searchInput = document.getElementById('search');
    const detailsBox = document.getElementById('details');
    const fileCountBox = document.getElementById('fileCount');
    const linkCountBox = document.getElementById('linkCount');

    const nodes = data.nodes || [];
    const edges = data.edges || [];
    const nodeById = new Map(nodes.map(n => [n.id, n]));
    const width = 1200;
    const height = 900;

    const state = {
      positions: new Map(),
      selected: null,
      query: '',
      transform: { x: 0, y: 0, k: 1 },
      dragging: false,
      panStart: null,
    };

    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    svg.appendChild(g);

    const edgeLayer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    const nodeLayer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.appendChild(edgeLayer);
    g.appendChild(nodeLayer);

    function initPositions() {
      const groups = new Map();
      for (const node of nodes) {
        const group = node.group || 'root';
        if (!groups.has(group)) groups.set(group, []);
        groups.get(group).push(node);
      }
      const groupNames = [...groups.keys()];
      const centerX = width / 2;
      const centerY = height / 2;
      groupNames.forEach((group, index) => {
        const items = groups.get(group);
        const angle = (index / Math.max(1, groupNames.length)) * Math.PI * 2;
        const radius = 180 + index * 40;
        items.forEach((node, i) => {
          const localAngle = angle + (i / Math.max(1, items.length)) * 0.8;
          state.positions.set(node.id, {
            x: centerX + Math.cos(localAngle) * radius,
            y: centerY + Math.sin(localAngle) * radius,
          });
        });
      });
    }

    function layout() {
      const iterations = 60;
      for (let step = 0; step < iterations; step += 1) {
        const forces = new Map();
        for (const node of nodes) {
          forces.set(node.id, { x: 0, y: 0 });
        }
        for (const node of nodes) {
          const pos = state.positions.get(node.id);
          if (!pos) continue;
          for (const other of nodes) {
            if (other.id === node.id) continue;
            const op = state.positions.get(other.id);
            if (!op) continue;
            const dx = pos.x - op.x;
            const dy = pos.y - op.y;
            const dist = Math.hypot(dx, dy) || 0.001;
            const force = 1800 / (dist * dist + 100);
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;
            const f = forces.get(node.id);
            f.x += fx;
            f.y += fy;
          }
        }
        for (const edge of edges) {
          const source = state.positions.get(edge.source);
          const target = state.positions.get(edge.target);
          if (!source || !target) continue;
          const dx = target.x - source.x;
          const dy = target.y - source.y;
          const dist = Math.hypot(dx, dy) || 0.001;
          const spring = 0.06;
          const fx = dx * spring;
          const fy = dy * spring;
          const sf = forces.get(edge.source);
          const tf = forces.get(edge.target);
          if (sf) { sf.x += fx; sf.y += fy; }
          if (tf) { tf.x -= fx; tf.y -= fy; }
        }
        for (const node of nodes) {
          const pos = state.positions.get(node.id);
          const f = forces.get(node.id);
          if (!pos || !f) continue;
          pos.x += f.x * 0.02;
          pos.y += f.y * 0.02;
          pos.x = Math.max(80, Math.min(width - 80, pos.x));
          pos.y = Math.max(80, Math.min(height - 80, pos.y));
        }
      }
    }

    function visibleNodes() {
      const query = state.query.trim().toLowerCase();
      const selected = state.selected;
      const selectedNeighbors = new Set();
      if (selected) {
        for (const edge of edges) {
          if (edge.source === selected.id) selectedNeighbors.add(edge.target);
          if (edge.target === selected.id) selectedNeighbors.add(edge.source);
        }
      }
      return nodes.filter(node => {
        if (!query) return true;
        const text = `${node.path} ${node.label}`.toLowerCase();
        return text.includes(query) || (selected && selectedNeighbors.has(node.id));
      });
    }

    function render() {
      const visibleSet = new Set(visibleNodes().map(n => n.id));
      edgeLayer.innerHTML = '';
      nodeLayer.innerHTML = '';
      const query = state.query.trim().toLowerCase();
      const selected = state.selected;
      const selectedNeighbors = new Set();
      if (selected) {
        for (const edge of edges) {
          if (edge.source === selected.id) selectedNeighbors.add(edge.target);
          if (edge.target === selected.id) selectedNeighbors.add(edge.source);
        }
      }

      edges.forEach(edge => {
        const source = state.positions.get(edge.source);
        const target = state.positions.get(edge.target);
        if (!source || !target) return;
        const visible = visibleSet.has(edge.source) && visibleSet.has(edge.target);
        if (!visible) return;
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', source.x);
        line.setAttribute('y1', source.y);
        line.setAttribute('x2', target.x);
        line.setAttribute('y2', target.y);
        line.setAttribute('class', 'edge' + ((selected && (edge.source === selected.id || edge.target === selected.id)) ? ' active' : ''));
        edgeLayer.appendChild(line);
      });

      nodes.forEach(node => {
        if (!visibleSet.has(node.id)) return;
        const pos = state.positions.get(node.id);
        if (!pos) return;
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('class', 'node' + (selected && selected.id === node.id ? ' active' : '') + (query && `${node.path} ${node.label}`.toLowerCase().includes(query) ? ' highlight' : '') + (selected && !selectedNeighbors.has(node.id) && selected.id !== node.id ? ' dim' : ''));
        group.setAttribute('transform', `translate(${pos.x}, ${pos.y})`);
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('r', selected && selected.id === node.id ? 13 : 8);
        circle.setAttribute('fill', node.language === 'python' ? '#5eead4' : node.language === 'javascript' || node.language === 'typescript' ? '#60a5fa' : '#f59e0b');
        circle.addEventListener('click', () => selectNode(node));
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', 12);
        label.setAttribute('y', 4);
        label.setAttribute('class', 'node-label');
        label.textContent = node.path.split('/').slice(-2).join('/');
        group.appendChild(circle);
        group.appendChild(label);
        nodeLayer.appendChild(group);
      });
    }

    function selectNode(node) {
      state.selected = node;
      detailsBox.innerHTML = `<strong>${node.path}</strong><div>Language: ${node.language}</div><div>Neighbors: ${edges.filter(e => e.source === node.id || e.target === node.id).length}</div>`;
      render();
    }

    function applySearch() {
      state.query = searchInput.value;
      render();
    }

    searchInput.addEventListener('input', applySearch);

    initPositions();
    layout();
    render();

    fileCountBox.textContent = `Files: ${nodes.length}`;
    linkCountBox.textContent = `Links: ${edges.length}`;

    let isPanning = false;
    svg.addEventListener('pointerdown', (event) => {
      if (event.target.tagName === 'svg') {
        isPanning = true;
        state.panStart = { x: event.clientX, y: event.clientY, tx: state.transform.x, ty: state.transform.y };
        svg.style.cursor = 'grabbing';
      }
    });
    window.addEventListener('pointermove', (event) => {
      if (!isPanning || !state.panStart) return;
      const dx = event.clientX - state.panStart.x;
      const dy = event.clientY - state.panStart.y;
      state.transform.x = state.panStart.tx + dx;
      state.transform.y = state.panStart.ty + dy;
      g.setAttribute('transform', `translate(${state.transform.x} ${state.transform.y}) scale(${state.transform.k})`);
    });
    window.addEventListener('pointerup', () => {
      isPanning = false;
      svg.style.cursor = 'grab';
      state.panStart = null;
    });
    svg.addEventListener('wheel', (event) => {
      event.preventDefault();
      const delta = event.deltaY > 0 ? 0.9 : 1.1;
      state.transform.k = Math.max(0.6, Math.min(2.2, state.transform.k * delta));
      g.setAttribute('transform', `translate(${state.transform.x} ${state.transform.y}) scale(${state.transform.k})`);
    }, { passive: false });
  </script>
</body>
</html>
"""
    OUTPUT_HTML.write_text(html.replace("const data = JSON.parse(document.currentScript.previousElementSibling.textContent || '{}');", "const data = " + json.dumps(data, indent=2) + ";"), encoding="utf-8")


def main() -> None:
    builder = GraphBuilder(ROOT)
    graph = builder.build()
    OUTPUT_JSON.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    write_html(graph)
    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_HTML}")
    print(f"Files: {graph['stats']['files']}, Links: {graph['stats']['links']}")


if __name__ == "__main__":
    main()

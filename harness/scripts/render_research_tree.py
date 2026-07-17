#!/usr/bin/env python3
"""Render a research tree JSON file as a self-contained interactive HTML page.

Input format:
{
  "title": "Research Tree",
  "nodes": [
    {
      "id": "N001",
      "parent": null,
      "title": "Initial hypothesis",
      "status": "active",
      "time": "2026-07-17 / commit abc123",
      "motivation": "...",
      "action": "What changed or was tested",
      "conclusion": "...",
      "issues": ["..."],
      "invalidation": "What would invalidate this node"
    }
  ]
}
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


STATUS_COLORS = {
    "active": "#2563eb",
    "pruned": "#dc2626",
    "noisy": "#d97706",
    "superseded": "#7c3aed",
    "partially reusable": "#059669",
    "unknown": "#64748b",
}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def load_tree(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        data = {"title": "Research Tree", "nodes": data}
    if not isinstance(data, dict) or "nodes" not in data:
        raise SystemExit("Input must be a JSON object with a 'nodes' list, or a bare node list.")
    nodes = data["nodes"]
    if not isinstance(nodes, list):
        raise SystemExit("'nodes' must be a list.")
    seen: set[str] = set()
    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            raise SystemExit(f"Node {i} is not an object.")
        node_id = str(node.get("id", "")).strip()
        if not node_id:
            raise SystemExit(f"Node {i} is missing a non-empty 'id'.")
        if node_id in seen:
            raise SystemExit(f"Duplicate node id: {node_id}")
        seen.add(node_id)
    return data


def build_children(nodes: list[dict[str, Any]]) -> dict[str | None, list[dict[str, Any]]]:
    children: dict[str | None, list[dict[str, Any]]] = {}
    ids = {str(n["id"]) for n in nodes}
    for node in nodes:
        parent_raw = node.get("parent")
        parent = None if parent_raw in (None, "", "null") else str(parent_raw)
        if parent is not None and parent not in ids:
            node["_missing_parent"] = parent
            parent = None
        children.setdefault(parent, []).append(node)
    return children


def render_node(node: dict[str, Any], children: dict[str | None, list[dict[str, Any]]]) -> str:
    node_id = str(node["id"])
    status = str(node.get("status", "unknown")).lower()
    color = STATUS_COLORS.get(status, STATUS_COLORS["unknown"])
    kids = children.get(node_id, [])
    issue_items = "".join(f"<li>{_esc(x)}</li>" for x in _as_list(node.get("issues")))
    missing_parent = ""
    if node.get("_missing_parent"):
        missing_parent = f"<p class='warn'>Missing parent: {_esc(node['_missing_parent'])}</p>"
    child_html = "".join(render_node(child, children) for child in kids)
    collapsed = "" if kids else " leaf"
    return f"""
<li>
  <details open class="node{collapsed}">
    <summary>
      <span class="status" style="background:{color}"></span>
      <span class="node-id">{_esc(node_id)}</span>
      <span class="title">{_esc(node.get("title", node_id))}</span>
      <span class="badge">{_esc(status)}</span>
    </summary>
    <div class="body">
      {missing_parent}
      <p><b>Time:</b> {_esc(node.get("time", ""))}</p>
      <p><b>Motivation:</b> {_esc(node.get("motivation", ""))}</p>
      <p><b>Action:</b> {_esc(node.get("action", node.get("what", "")))}</p>
      <p><b>Conclusion:</b> {_esc(node.get("conclusion", ""))}</p>
      <p><b>Invalidation:</b> {_esc(node.get("invalidation", ""))}</p>
      <ul class="issues">{issue_items}</ul>
    </div>
    <ul>{child_html}</ul>
  </details>
</li>"""


def render_html(data: dict[str, Any]) -> str:
    title = str(data.get("title", "Research Tree"))
    nodes = data["nodes"]
    children = build_children(nodes)
    roots = children.get(None, [])
    root_html = "".join(render_node(node, children) for node in roots)
    total = len(nodes)
    status_counts: dict[str, int] = {}
    for node in nodes:
        status = str(node.get("status", "unknown")).lower()
        status_counts[status] = status_counts.get(status, 0) + 1
    counts = " ".join(
        f"<span class='count'><span class='status' style='background:{STATUS_COLORS.get(k, STATUS_COLORS['unknown'])}'></span>{_esc(k)}: {v}</span>"
        for k, v in sorted(status_counts.items())
    )
    payload = json.dumps(data, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<style>
body {{ font-family: Inter, Segoe UI, Arial, sans-serif; margin: 0; color: #0f172a; background: #f8fafc; }}
header {{ position: sticky; top: 0; z-index: 2; background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 14px 18px; }}
h1 {{ margin: 0 0 8px; font-size: 20px; }}
.toolbar {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }}
button, input {{ border: 1px solid #cbd5e1; background: #fff; border-radius: 6px; padding: 7px 10px; font-size: 14px; }}
button {{ cursor: pointer; }}
main {{ padding: 16px 20px 40px; }}
ul {{ list-style: none; padding-left: 24px; margin: 0; border-left: 1px solid #e2e8f0; }}
li {{ margin: 8px 0; }}
details {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 10px; box-shadow: 0 1px 2px rgba(15, 23, 42, .04); }}
summary {{ cursor: pointer; display: flex; gap: 8px; align-items: center; }}
.status {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; flex: 0 0 auto; }}
.node-id {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; color: #475569; }}
.title {{ font-weight: 650; }}
.badge, .count {{ margin-left: auto; font-size: 12px; color: #475569; background: #f1f5f9; border-radius: 999px; padding: 2px 7px; }}
.count {{ margin-left: 0; display: inline-flex; gap: 5px; align-items: center; }}
.body {{ margin: 8px 0 4px 22px; color: #334155; line-height: 1.35; }}
.body p {{ margin: 5px 0; }}
.issues {{ list-style: disc; border-left: 0; padding-left: 18px; }}
.warn {{ color: #b91c1c; font-weight: 600; }}
.hidden {{ display: none; }}
</style>
</head>
<body>
<header>
  <h1>{_esc(title)} <span class="count">nodes: {total}</span></h1>
  <div class="toolbar">
    <button onclick="setAll(true)">Expand all</button>
    <button onclick="setAll(false)">Collapse all</button>
    <input id="q" placeholder="Filter text / id / status" oninput="filterTree()">
    {counts}
  </div>
</header>
<main>
  <ul id="tree">{root_html}</ul>
</main>
<script id="tree-data" type="application/json">{html.escape(payload)}</script>
<script>
function setAll(open) {{
  document.querySelectorAll('details').forEach(d => d.open = open);
}}
function textOf(el) {{ return el.innerText.toLowerCase(); }}
function filterTree() {{
  const q = document.getElementById('q').value.trim().toLowerCase();
  document.querySelectorAll('#tree li').forEach(li => li.classList.remove('hidden'));
  if (!q) return;
  document.querySelectorAll('#tree li').forEach(li => {{
    const match = textOf(li).includes(q);
    if (!match) li.classList.add('hidden');
  }});
  document.querySelectorAll('#tree li:not(.hidden)').forEach(li => {{
    let p = li.parentElement;
    while (p && p.id !== 'tree') {{
      if (p.tagName === 'DETAILS') p.open = true;
      if (p.tagName === 'LI') p.classList.remove('hidden');
      p = p.parentElement;
    }}
  }});
}}
</script>
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_html", type=Path)
    args = parser.parse_args()
    data = load_tree(args.input_json)
    args.output_html.write_text(render_html(data), encoding="utf-8")
    print(f"Wrote {args.output_html}")


if __name__ == "__main__":
    main()

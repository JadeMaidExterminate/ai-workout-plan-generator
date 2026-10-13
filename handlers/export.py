"""Export handler — writes plans to PDF-ready HTML, Markdown, or JSON.

Path safety: we resolve the destination and re-check it's under an allowed
root before writing. Symlinks are followed once, then re-checked.
"""
from __future__ import annotations

import json
from pathlib import Path

from models.plan import Plan

_ALLOWED_SUFFIXES = {".json", ".md", ".html"}


def _resolve_safe(path: Path, allowed_root: Path) -> Path:
    resolved = path.expanduser().resolve()
    root = allowed_root.expanduser().resolve()
    if root not in resolved.parents and resolved != root:
        raise PermissionError(f"export path {resolved} escapes allowed root {root}")
    if resolved.suffix.lower() not in _ALLOWED_SUFFIXES:
        raise ValueError(f"unsupported export suffix: {resolved.suffix}")
    return resolved


def export_plan(plan: Plan, destination: Path, allowed_root: Path) -> Path:
    target = _resolve_safe(destination, allowed_root)
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.suffix == ".json":
        target.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    elif target.suffix == ".md":
        target.write_text(_to_markdown(plan), encoding="utf-8")
    else:
        target.write_text(_to_html(plan), encoding="utf-8")
    return target


def _to_markdown(plan: Plan) -> str:
    lines = [
        f"# Workout Plan — {plan.split.replace('_', ' ').title()}",
        "",
        f"**Generated:** {plan.generated_on.isoformat()}  ",
        f"**Goal:** {plan.goal}  ",
        f"**Sessions:** {plan.total_sessions}",
        "",
        f"> {plan.rationale}",
        "",
    ]
    for week in plan.weeks:
        header = f"## Week {week.index}" + (" (deload)" if week.deload else "")
        lines.append(header)
        lines.append("")
        for session in week.sessions:
            lines.append(f"### {session.day_label} — {session.focus} (~{session.estimated_minutes}m)")
            lines.append("")
            lines.append("| Movement | Sets | Reps | RPE | Rest |")
            lines.append("| --- | --- | --- | --- | --- |")
            for p in session.prescriptions:
                lines.append(f"| {p.movement} | {p.sets} | {p.reps} | {p.rpe:.1f} | {p.rest_seconds}s |")
            lines.append("")
    return "\n".join(lines)


def _to_html(plan: Plan) -> str:
    body = _to_markdown(plan)
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>Workout Plan — {plan.split}</title>"
        "<style>body{font-family:system-ui;max-width:860px;margin:2rem auto;padding:0 1rem}"
        "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:4px 8px}</style>"
        "</head><body><pre style='white-space:pre-wrap'>"
        + json.dumps(body)[1:-1].replace("\\n", "\n").replace('\\"', '"')
        + "</pre></body></html>"
    )
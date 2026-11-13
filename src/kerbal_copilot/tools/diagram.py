"""Render an evaluated build as a standalone SVG stack diagram. No model calls."""
import math
from html import escape

from ..models import Build, BuildReport

WIDTH = {"size0": 24, "size1": 36, "size1p5": 46, "size2": 56, "size3": 76, "size4": 96}
FILL = {
    "tank": ("#E1F5EE", "#0F6E56"),
    "engine": ("#FAECE7", "#993C1D"),
    "other": ("#F1EFE8", "#5F5E5A"),
}
CX, LABEL_X, TOP = 170, 320, 30


def _role(part) -> str:
    for role in ("command", "engine", "decoupler", "tank"):
        if role in part.roles:
            return role
    return "other"


def _height(part, role: str) -> float:
    if role == "tank":
        return max(18.0, min(110.0, 3 * math.sqrt(sum(part.resources.values()) or 1)))
    return {"engine": 18.0, "command": 30.0, "decoupler": 5.0}.get(role, 14.0)


def _shape(role: str, x: float, y: float, w: float, h: float) -> str:
    fill, stroke = FILL.get(role, FILL["other"])
    style = f'fill="{fill}" stroke="{stroke}" stroke-width="0.8"'
    if role == "engine":
        pts = (f"{x + w * 0.2:.1f},{y:.1f} {x + w * 0.8:.1f},{y:.1f} "
               f"{x + w:.1f},{y + h:.1f} {x:.1f},{y + h:.1f}")
        return f'<polygon points="{pts}" {style}/>'
    if role == "command":
        pts = f"{x + w / 2:.1f},{y:.1f} {x + w:.1f},{y + h:.1f} {x:.1f},{y + h:.1f}"
        return f'<polygon points="{pts}" {style}/>'
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2" {style}/>'


def _subtitle(result) -> str:
    if result is None:
        return "Not evaluated"
    return f"{result.dv_vac:,.0f} m/s · TWR {result.twr_start:.2f}"


def render_svg(build: Build, report: BuildReport | None, db) -> str:
    shapes: list[str] = []
    labels: list[str] = []
    results = {r.label: r for r in (report.stages if report else [])}
    y = float(TOP)
    last_label_y = -100.0

    def add_label(title: str, subtitle: str, top: float, bottom: float, edge: float) -> None:
        nonlocal last_label_y
        mid = (top + bottom) / 2
        ly = max(mid, last_label_y + 38)
        last_label_y = ly
        labels.append(
            f'<path d="M{edge + 8:.1f} {mid:.1f} L{LABEL_X - 8} {ly:.1f}" fill="none" '
            f'stroke="#888780" stroke-width="0.6" stroke-dasharray="3 3"/>'
            f'<text x="{LABEL_X}" y="{ly - 4:.1f}" font-size="14" font-weight="500" '
            f'fill="#2C2C2A">{escape(title)}</text>'
            f'<text x="{LABEL_X}" y="{ly + 13:.1f}" font-size="12" fill="#5F5E5A">'
            f"{escape(subtitle)}</text>"
        )

    def draw_group(refs, title: str, subtitle: str) -> None:
        nonlocal y
        stack = [r for r in refs if r.placement == "stack"]
        radial = [r for r in refs if r.placement == "radial"]
        core_w = max((WIDTH.get(db.get(r.name).size or "", 36) for r in stack), default=36)
        top = y
        for ref in stack:
            part = db.get(ref.name)
            role = _role(part)
            w, h = WIDTH.get(part.size or "", 36), _height(part, role)
            for _ in range(ref.qty):
                shapes.append(_shape(role, CX - w / 2, y, w, h))
                y += h + 1
        ry, edge = top, CX + core_w / 2
        for ref in radial:
            part = db.get(ref.name)
            role = _role(part)
            w, h = WIDTH.get(part.size or "", 24), _height(part, role)
            for side in (-1, 1):
                shapes.append(_shape(role, CX + side * (core_w / 2 + 4 + w / 2) - w / 2, ry, w, h))
            ry += h + 1
            edge = max(edge, CX + core_w / 2 + 4 + w)
        if radial and max(r.qty for r in radial) > 2:
            count = max(r.qty for r in radial)
            shapes.append(f'<text x="{edge + 4:.1f}" y="{top + 12:.1f}" font-size="12" '
                          f'fill="#5F5E5A">x{count}</text>')
        y = max(y, ry) + 6
        add_label(title, subtitle, top, y - 6, edge)

    if build.payload:
        draw_group(build.payload, "Payload", "Not staged")

    stages = build.stages
    merged: set[int] = set()  # booster stages whose radial parts were drawn beside the next stage
    for k in range(len(stages) - 1, -1, -1):
        stage = stages[k]
        refs = [r for r in stage.parts if not (k in merged and r.placement == "radial")]
        title, sub = stage.label, _subtitle(results.get(stage.label))
        if k > 0 and stages[k - 1].fires_with_next:
            boost = stages[k - 1]
            refs += [r for r in boost.parts if r.placement == "radial"]
            merged.add(k - 1)
            rb, rc = results.get(boost.label), results.get(stage.label)
            title = f"{boost.label} + {stage.label}"
            if rb and rc:
                sub = f"{rb.dv_vac:,.0f} + {rc.dv_vac:,.0f} m/s · TWR {rb.twr_start:.2f}"
        if refs:
            draw_group(refs, title, sub)

    height = max(y, last_label_y + 30) + 40
    ly = height - 18
    legend = "".join(
        f'<rect x="{x}" y="{ly - 10:.0f}" width="12" height="12" rx="2" fill="{f}" '
        f'stroke="{s}" stroke-width="0.8"/>'
        f'<text x="{x + 18}" y="{ly:.0f}" font-size="12" fill="#5F5E5A">{t}</text>'
        for x, t, (f, s) in ((40, "Fuel tanks", FILL["tank"]), (150, "Engines", FILL["engine"]),
                             (250, "Pods, decouplers, other", FILL["other"]))
    )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 {height:.0f}" '
            f'width="100%" font-family="sans-serif">'
            f'<rect width="680" height="{height:.0f}" fill="#FFFFFF"/>'
            + "".join(shapes) + "".join(labels) + legend + "</svg>")


def render_state(state: dict | None, db) -> str:
    if not state:
        return ""
    build = Build.model_validate(state["build"])
    report = BuildReport.model_validate(state["report"]) if state.get("report") else None
    try:
        return render_svg(build, report, db)
    except Exception as exc:  # a drawing problem must never break the chat
        return f"<p>Can't draw this build: {escape(str(exc))}</p>"

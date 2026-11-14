"""Render an evaluated build as a standalone SVG stack diagram. No model calls."""
import math
from html import escape

from ..models import Build, BuildReport

WIDTH = {"size0": 24, "size1": 36, "size1p5": 46, "size2": 56, "size3": 76, "size4": 96}
# Translucent fills read well on both light and dark pages
FILL = {
    "tank": ("#10b981", "#059669"),
    "engine": ("#f97316", "#ea580c"),
    "other": ("#94a3b8", "#64748b"),
}
VIEW_W, CX, TOP = 860, 380, 30
STAGE_X, PART_X = 24, 560  # stage summaries on the left, part names on the right
LINE_H, MAX_LABEL = 17, 46
STYLE = (
    "<style>.t{fill:var(--body-text-color,#1f2937)}.m{fill:var(--body-text-color-subdued,#6b7280)}"
    ".k{stroke:var(--body-text-color-subdued,#9ca3af)}</style>"
)


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
    style = f'fill="{fill}" fill-opacity="0.22" stroke="{stroke}" stroke-width="1.2"'
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


def _part_text(part, qty: int) -> str:
    """'2x Title' in the main colour, then the internal name dimmed, cut to fit."""
    title = part.title or part.name
    plain = (f"{qty}x " if qty > 1 else "") + title
    if len(plain) > MAX_LABEL:
        return escape(plain[:MAX_LABEL - 1]) + "…"
    room = MAX_LABEL - len(plain) - 1
    if part.title and part.title != part.name and room >= 6:
        name = part.name if len(part.name) <= room else part.name[:room - 1] + "…"
        return f'{escape(plain)} <tspan class="m" font-size="11">{escape(name)}</tspan>'
    return escape(plain)


def render_svg(build: Build, report: BuildReport | None, db) -> str:
    shapes: list[str] = []
    labels: list[str] = []
    results = {r.label: r for r in (report.stages if report else [])}
    y = float(TOP)
    last_stage_y = -100.0
    last_part_y = -100.0

    def add_stage_label(title: str, subtitle: str, top: float, bottom: float, left: float) -> None:
        nonlocal last_stage_y
        mid = (top + bottom) / 2
        ly = max(mid, last_stage_y + 38)
        last_stage_y = ly
        bx = left - 14
        labels.append(
            f'<path d="M{bx + 4:.1f} {top:.1f} H{bx:.1f} V{bottom:.1f} H{bx + 4:.1f}" fill="none" '
            f'class="k" stroke-width="1"/>'
            f'<text x="{bx - 8:.1f}" y="{ly - 3:.1f}" text-anchor="end" font-size="14" '
            f'font-weight="600" class="t">{escape(title)}</text>'
            f'<text x="{bx - 8:.1f}" y="{ly + 13:.1f}" text-anchor="end" font-size="12" '
            f'class="m">{escape(subtitle)}</text>'
        )

    def add_part_labels(items: list[tuple[float, float, str]]) -> None:
        """items: (y of the part, x of its right edge, label). Spread so none overlap."""
        nonlocal last_part_y
        for target, edge, text in sorted(items):
            ly = max(target, last_part_y + LINE_H)
            last_part_y = ly
            labels.append(
                f'<path d="M{edge + 3:.1f} {target:.1f} L{PART_X - 8} {ly:.1f}" fill="none" '
                f'class="k" stroke-width="0.7" stroke-dasharray="2 3"/>'
                f'<text x="{PART_X}" y="{ly + 4:.1f}" font-size="13" class="t">{text}</text>'
            )

    def draw_group(refs, title: str, subtitle: str) -> None:
        nonlocal y
        stack = [r for r in refs if r.placement == "stack"]
        radial = [r for r in refs if r.placement == "radial"]
        core_w = max((WIDTH.get(db.get(r.name).size or "", 36) for r in stack), default=36)
        top = y
        items: list[tuple[float, float, str]] = []
        for ref in stack:
            part = db.get(ref.name)
            role = _role(part)
            w, h = WIDTH.get(part.size or "", 36), _height(part, role)
            block_top = y
            for _ in range(ref.qty):
                shapes.append(f"<g><title>{escape(part.title or part.name)} "
                              f"({escape(part.name)})</title>"
                              f"{_shape(role, CX - w / 2, y, w, h)}</g>")
                y += h + 1
            items.append(((block_top + y - 1) / 2, CX + w / 2, _part_text(part, ref.qty)))
        ry, edge = top, CX + core_w / 2
        for ref in radial:
            part = db.get(ref.name)
            role = _role(part)
            w, h = WIDTH.get(part.size or "", 24), _height(part, role)
            for side in (-1, 1):
                x = CX + side * (core_w / 2 + 4 + w / 2) - w / 2
                shapes.append(f"<g><title>{escape(part.title or part.name)} "
                              f"({escape(part.name)})</title>{_shape(role, x, ry, w, h)}</g>")
            right = CX + core_w / 2 + 4 + w
            items.append((ry + h / 2, right, _part_text(part, ref.qty)))
            ry += h + 1
            edge = max(edge, right)
        y = max(y, ry) + 8
        add_part_labels(items)
        add_stage_label(title, subtitle, top, y - 8, CX - (edge - CX))

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

    height = max(y, last_stage_y + 30, last_part_y + 20) + 40
    ly = height - 18
    legend = "".join(
        f'<rect x="{x}" y="{ly - 10:.0f}" width="12" height="12" rx="3" fill="{f}" '
        f'fill-opacity="0.22" stroke="{s}" stroke-width="1.2"/>'
        f'<text x="{x + 18}" y="{ly:.0f}" font-size="12" class="m">{t}</text>'
        for x, t, (f, s) in ((STAGE_X, "Fuel tanks", FILL["tank"]),
                             (STAGE_X + 100, "Engines", FILL["engine"]),
                             (STAGE_X + 190, "Pods, decouplers, other", FILL["other"]))
    )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {height:.0f}" '
            f'width="100%" font-family="Inter, system-ui, sans-serif">{STYLE}'
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

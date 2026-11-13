"""Row formatters for the Gradio dataframes."""
STAGE_HEADERS = ["Stage", "Δv vac (m/s)", "Δv ASL (m/s)", "TWR at start", "Burn (s)"]
BUILD_HEADERS = ["Id", "Name", "Mission", "Δv vac", "Status", "Outcome", "Created"]
PART_HEADERS = ["Name", "Title", "Mod", "Size", "Mass (t)", "Thrust (kN)", "Isp vac", "Tech"]
MOD_HEADERS = ["Mod", "Installed", "Latest (CKAN)", "Max KSP"]


def stage_rows(state) -> list[list]:
    if not state or not state.get("report"):
        return []
    return [[s["label"], round(s["dv_vac"]), round(s["dv_asl"]), round(s["twr_start"], 2),
             round(s["burn_time_s"])] for s in state["report"]["stages"]]


def build_rows(builds) -> list[list]:
    return [[b["id"], b["name"], b["mission"],
             round(b["total_dv"]) if b["total_dv"] else "", b["status"], b["outcome"] or "",
             b["created_at"]] for b in builds]


def part_rows(parts) -> list[list]:
    return [[p["name"], p["title"], p["mod"], p.get("size") or "", p["mass_t"],
             p.get("thrust_kn", ""), p.get("isp_vac", ""), p.get("tech") or ""] for p in parts]


def mod_rows(mods) -> list[list]:
    return [[m["identifier"], m.get("version") or "", m.get("latest") or "",
             m.get("ksp_max") or ""] for m in mods]


def summary_md(state) -> str:
    """Totals and checker warnings shown above the stage table."""
    if not state or not state.get("report"):
        return ""
    report = state["report"]
    line = (f"**Total Δv (vac):** {report['total_dv_vac']:,.0f} m/s · "
            f"**Launch TWR:** {report['launch_twr']:.2f}")
    warnings = report.get("warnings") or []
    if warnings:
        line += "\n\n" + "\n".join(f"- ⚠️ {w}" for w in warnings)
    return line

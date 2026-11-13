"""Deterministic rocket maths. The model never does arithmetic; it calls these."""
import difflib
import math
from pathlib import Path

from ..config import settings
from ..knowledge import load_delta_v
from ..models import Build, BuildReport, StageResult

G0 = 9.80665
# Surface gravity in m/s^2 (KSP wiki values; verify before relying on them)
SURFACE_G = {
    "Kerbin": 9.81, "Mun": 1.63, "Minmus": 0.491, "Duna": 2.94, "Ike": 1.10,
    "Eve": 16.7, "Gilly": 0.049, "Moho": 2.70, "Dres": 1.13, "Laythe": 7.85,
    "Vall": 2.31, "Tylo": 7.85, "Bop": 0.589, "Pol": 0.373, "Eeloo": 1.69,
}


def _mdot(engines) -> float:
    """Propellant mass flow in t/s (thrust in kN, so kN / (s * m/s^2) = t/s)."""
    return sum(e.max_thrust_kn / (e.isp_vac * G0) for e in engines if e.isp_vac > 0)


def _wet(part, db) -> float:
    return part.mass_t + sum(amount * db.density(res) for res, amount in part.resources.items())


def evaluate(build: Build, db) -> BuildReport:
    propellants: set[str] = set()
    for stage in build.stages:
        for ref in stage.parts:
            part = db.get(ref.name)  # unknown part -> KeyError, which the model sees
            if part.engine:
                propellants |= set(part.engine.propellants)

    groups = []
    for stage in build.stages:
        dry = fuel = 0.0
        engines = []
        for ref in stage.parts:
            part = db.get(ref.name)
            prop = sum(a * db.density(r) for r, a in part.resources.items() if r in propellants)
            dry += (_wet(part, db) - prop) * ref.qty
            fuel += prop * ref.qty
            if part.engine:
                engines += [part.engine] * ref.qty
        groups.append({"stage": stage, "dry": dry, "fuel": fuel, "engines": engines})

    payload = sum(_wet(db.get(ref.name), db) * ref.qty for ref in build.payload)

    results: list[StageResult] = []
    warnings: list[str] = []
    burning: set[int] = set()
    for i, group in enumerate(groups):
        label = group["stage"].label
        k = i
        burning.add(k)
        while k < len(groups) - 1 and groups[k]["stage"].fires_with_next:
            k += 1
            burning.add(k)  # boosters and asparagus chains ignite together
        engines = [e for j in sorted(burning) for e in groups[j]["engines"]]
        if not engines or group["fuel"] <= 0:
            reason = "no active engines" if not engines else "no propellant"
            warnings.append(f"{label}: {reason}")
            burning.discard(i)
            continue

        m0 = payload + sum(g["dry"] + g["fuel"] for g in groups[i:])
        own = _mdot(group["engines"])
        total = _mdot(engines)
        t = group["fuel"] / (own or total)  # stage lasts until its own tanks run dry
        if own:  # drop tanks (no own engines) are drained first, so others don't burn then
            for j in burning - {i}:
                drain = t * _mdot(groups[j]["engines"])
                if drain > groups[j]["fuel"] + 1e-9:
                    warnings.append(f"{groups[j]['stage'].label} runs dry before {label} "
                                    "separates")
                groups[j]["fuel"] = max(0.0, groups[j]["fuel"] - drain)
        m1 = max(m0 - total * t, 1e-6)
        f_vac = sum(e.max_thrust_kn for e in engines)
        f_asl = sum(e.max_thrust_kn * e.isp_asl / e.isp_vac for e in engines if e.isp_vac > 0)
        log_ratio = math.log(m0 / m1)
        body = group["stage"].twr_body or build.body
        thrust = f_asl if (i == 0 and body == "Kerbin") else f_vac
        results.append(StageResult(
            label=label,
            wet_mass_t=round(m0, 3),
            end_mass_t=round(m1, 3),
            dv_vac=round(f_vac / total * log_ratio, 1),
            dv_asl=round(f_asl / total * log_ratio, 1),
            twr_start=round(thrust / (m0 * SURFACE_G.get(body, 9.81)), 2),
            burn_time_s=round(t, 1),
        ))
        group["fuel"] = 0.0
        burning.discard(i)

    return BuildReport(
        stages=results,
        total_dv_vac=round(sum(r.dv_vac for r in results), 1),
        launch_twr=results[0].twr_start if results else 0.0,
        warnings=warnings,
    )


def check_build(build: Build, report: BuildReport, required_dv: float | None = None):
    problems = list(report.warnings)
    if build.body == "Kerbin" and report.stages and report.launch_twr < 1.2:
        problems.append(f"Launch TWR is {report.launch_twr:.2f}; it should be at least 1.2.")
    if required_dv and report.total_dv_vac < required_dv * 1.05:
        problems.append(f"Total vacuum delta-v is {report.total_dv_vac:,.0f} m/s but the mission "
                        f"needs about {required_dv:,.0f} m/s plus margin.")
    return problems


def mission_budget(mission: str, folder: Path | None = None) -> dict:
    legs, missions = load_delta_v(folder or settings.knowledge_dir)
    key = (mission or "").lower().strip()
    if key not in missions:
        match = difflib.get_close_matches(key, list(missions), n=1, cutoff=0.4)
        if not match:
            return {"error": f"Unknown mission. Known missions: {sorted(missions)}"}
        key = match[0]
    rows = [{"leg": legs[leg][0], "dv": legs[leg][1]} for leg in missions[key] if leg in legs]
    total = sum(r["dv"] for r in rows)
    return {"mission": key, "legs": rows, "total_dv": total, "with_margin_dv": round(total * 1.1)}

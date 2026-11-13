"""Command line: kerbal-copilot ingest | pull-data | search | ask | eval"""
import argparse
import json
import sys
from pathlib import Path

from .config import settings


def cmd_ingest(args) -> None:
    from .parts.cfg_parser import parse_file
    from .parts.db import PartsDB
    from .parts.extract import extract, extract_from_gamedata
    from .tools.mods import build_ckan_index, read_installed_ckan

    ksp = Path(args.ksp)
    gamedata = ksp / "GameData"
    if not gamedata.is_dir():
        sys.exit(f"No GameData folder in {ksp}. Pass the folder that contains GameData.")
    cache = Path(args.cache) if args.cache else gamedata / "ModuleManager.ConfigCache"
    if cache.exists():
        newest = max(
            (p.stat().st_mtime for p in gamedata.rglob("*") if p.suffix in (".cfg", ".dll")),
            default=0,
        )
        if newest > cache.stat().st_mtime:
            print("WARNING: GameData changed after the ConfigCache was written. "
                  "Launch KSP once, then re-run ingest.")
        print(f"Parsing {cache} (this can take a minute with many mods) ...")
        parts, densities, tech = extract(parse_file(cache), gamedata=gamedata)
    else:
        print("No ModuleManager.ConfigCache found; parsing raw .cfg files "
              "(ModuleManager patches are NOT applied).")
        parts, densities, tech = extract_from_gamedata(gamedata)

    installed = read_installed_ckan(ksp)
    if installed and not args.no_ckan:
        print(f"Indexing {len(installed)} installed mods from CKAN-meta ...")
        mods = build_ckan_index(installed)
    else:
        mods = [{"identifier": k, "name": k, "version": v, "installed": 1}
                for k, v in installed.items()]

    if not parts:
        sys.exit("No parts found. Check the --ksp path and that KSP has been launched once.")
    out = Path(args.out)
    PartsDB.build(out, parts, densities, tech, mods,
                  meta={"source": str(cache), "parts": len(parts)})
    print(f"Wrote {out}: {len(parts)} parts, {len(densities)} resources, "
          f"{len(tech)} tech nodes, {len(mods)} mods")

    if args.upload:
        from huggingface_hub import HfApi

        api = HfApi(token=settings.hf_token)
        api.create_repo(settings.hf_data_repo, repo_type="dataset", private=True, exist_ok=True)
        api.upload_file(path_or_fileobj=str(out), path_in_repo="parts.db",
                        repo_id=settings.hf_data_repo, repo_type="dataset")
        print(f"Uploaded to {settings.hf_data_repo}")


def cmd_pull(_args) -> None:
    from .parts.db import PartsDB, ensure_parts_db

    path = ensure_parts_db(force_download=True)
    meta = PartsDB(path).meta()
    print(f"Downloaded {path} ({meta.get('parts', '?')} parts)")


def cmd_search(args) -> None:
    from .parts.db import PartsDB, ensure_parts_db

    db = PartsDB(ensure_parts_db())
    rows = db.search(args.query, role=args.role, limit=args.limit)
    if not rows:
        print("No parts found.")
    for p in rows:
        engine = ""
        if "thrust_kn" in p:
            engine = f"  {p['thrust_kn']} kN, Isp {p['isp_asl']}/{p['isp_vac']} s"
        print(f"{p['name']:<32} {p['title'][:40]:<40} {p['mod']:<18} {p['size'] or '':<7}"
              f"{p['mass_t']:>6} t{engine}")


def cmd_ask(args) -> None:
    from .agent import Agent

    agent = Agent.from_env()
    text, build, report = agent.run(args.prompt, [])
    print(text)
    if report:
        print("\n--- evaluated by Python ---")
        for s in report.stages:
            print(f"{s.label:<28} {s.dv_vac:>8,.0f} m/s vac   TWR {s.twr_start:>5.2f}   "
                  f"{s.burn_time_s:>6.0f} s")
        print(f"Total {report.total_dv_vac:,.0f} m/s, launch TWR {report.launch_twr:.2f}")
        for warning in report.warnings:
            print("WARNING:", warning)
    print(agent.quota_text())


def cmd_eval(args) -> None:
    from .agent import Agent

    agent = Agent.from_env()
    cases = json.loads(Path(args.file).read_text(encoding="utf-8"))
    failed = 0
    for case in cases:
        _text, build, report = agent.run(case["prompt"], [])
        checks = {
            "has_build": build is not None,
            "evaluates": report is not None,
            "launch_twr": bool(report) and report.launch_twr >= case.get("min_launch_twr", 1.2),
            "delta_v": bool(report) and report.total_dv_vac >= case.get("min_dv", 0),
        }
        ok = all(checks.values())
        failed += not ok
        print("PASS" if ok else "FAIL", case["prompt"][:60], checks)
    sys.exit(1 if failed else 0)


def main() -> None:
    parser = argparse.ArgumentParser(prog="kerbal-copilot")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="Build parts.db from a KSP install (run on the PC)")
    ingest.add_argument("--ksp", required=True, help="KSP folder (the one containing GameData)")
    ingest.add_argument("--cache", help="Path to ModuleManager.ConfigCache, if not in GameData")
    ingest.add_argument("--out", default=str(settings.data_dir / "parts.db"))
    ingest.add_argument("--upload", action="store_true", help="Upload to the private HF dataset")
    ingest.add_argument("--no-ckan", action="store_true", help="Skip the CKAN-meta download")
    ingest.set_defaults(func=cmd_ingest)

    pull = sub.add_parser("pull-data", help="Download parts.db from the private HF dataset")
    pull.set_defaults(func=cmd_pull)

    search = sub.add_parser("search", help="Search parts.db (checks the data pipeline)")
    search.add_argument("query")
    search.add_argument("--role", help="engine, tank, command, decoupler, ...")
    search.add_argument("--limit", type=int, default=15)
    search.set_defaults(func=cmd_search)

    ask = sub.add_parser("ask", help="Ask the agent one question in the terminal")
    ask.add_argument("prompt")
    ask.set_defaults(func=cmd_ask)

    ev = sub.add_parser("eval", help="Run agent evals (spends model quota)")
    ev.add_argument("--file", default="tests/evals/basic.json")
    ev.set_defaults(func=cmd_eval)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

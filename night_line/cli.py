"""night-line CLI: reproduce published lines from cited inputs."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from night_line.model import ROOT, evaluate, load_box, packaged_boxes
from night_line.verify import verify_box

OUT_DEFAULT = ROOT / "out"


def _fmt(v: Any, digits: int | None = None) -> str:
    if v is None:
        return "OPEN"
    if isinstance(v, float):
        if digits is not None:
            return f"{v:.{digits}f}"
        return f"{v:.6g}"
    return str(v)


def _label_line(rec: dict[str, Any]) -> str:
    return str(rec["label_display"])


def write_line_md(rec: dict[str, Any], dest: Path) -> None:
    h_night = float(rec["H_night_h"])
    label = _label_line(rec)
    box = rec["box"]
    if rec["label"] == "LINE_OPEN_TWO_KNOBS":
        table = rec.get("identity_table") or []
        lines = [
            f"# {box} Night Line — 2026-09-17",
            "",
            f"**Label: {label}**",
            "",
            f"`{rec.get('identity') or 'usable_Wh / H_night_h = hibernation load W'}` "
            f"({h_night:g} h). Both store Wh and hibernation load W are OPEN.",
            "no store is chosen",
            "",
            "| nameplate kWh | nameplate Wh | usable Wh | max avg hibernation load W | reserve |",
            "|---|---|---|---|---|",
        ]
        for row in table:
            lines.append(
                f"| {row['nameplate_kWh']:g} | {row['nameplate_Wh']:.0f} | "
                f"{row['usable_Wh']:.0f} | {row['max_avg_hibernation_load_W']:.2f} | "
                f"ASSUMED |"
            )
        lines.extend(
            [
                "",
                "30% nameplate reserve on every row is **ASSUMED**, not printed. "
                "no store is chosen",
                "",
                "The label is not a claim that the box will live. "
                "The human who can lose the box signs. No measurement by us; all values printed "
                "by the team or NIST.",
                "",
            ]
        )
        dest.write_text("\n".join(lines), encoding="utf-8")
        return
    hi = rec["hi"]
    lo = rec["lo"]
    label = _label_line(rec)
    box = rec["box"]
    lines: list[str] = [
        f"# {box} Night Line — 2026-09-17",
        "",
    ]
    if rec["label"] == "LIVE":
        lines.extend(
            [
                f"**Label: {label}** — worst declared corner "
                f"{hi['E_night_Wh']:.2f} Wh / {hi['hours_lived']:.2f} h of {h_night:g} / "
                f"{hi['margin_Wh']:+.2f} Wh.",
                "",
            ]
        )
    else:
        lines.extend([f"**Label: {label}**", ""])
    if rec.get("ladder"):
        chain = " → ".join(f"{float(r['P_W']):.2f} W ({r['rung']})" for r in rec["ladder"])
        lines.append(f"Ladder: {chain}.")
        if rec.get("ladder_soc8"):
            last8 = rec["ladder_soc8"][-1]
            lines.append(
                f"{float(last8['P_W']):.2f} W at the printed 8 % minimum SOC."
            )
        lines.append("")
    brk = {b["knob"]: b for b in rec.get("breaks") or []}
    a = brk.get("A_rad_m2")
    g = brk.get("G_path_W_per_K")
    pe = brk.get("P_electronics_W")
    if a and g and pe and rec["label"] == "LIVE":
        lines.append(
            f"BREAK at exactly {h_night:g} h: radiator {_fmt(a.get('value'), 3)} m², "
            f"conductance {_fmt(g.get('value'), 5)} W/K, electronics "
            f"{_fmt(pe.get('value'), 3)} W."
        )
        lines.append("")
    lines.extend(
        [
            "`P_elec = max(P_electronics, P_leak)`. Heat that leaves is the leak. "
            "Electronics dissipation is already part of that heat.",
            "",
            "| corner | T_env K | P_elec W | E_night Wh | hours | margin Wh |",
            "|---|---|---|---|---|---|",
        ]
    )
    for c in rec.get("corners") or [lo, hi]:
        lines.append(
            f"| {c['name']} | {c['T_env_K']} | {c['P_elec_W']:.3f} | "
            f"{c['E_night_Wh']:.2f} | {c['hours_lived']:.2f} | {c['margin_Wh']:+.2f} |"
        )
    lines.extend(
        [
            "",
            f"Store: **{rec['store_Wh']:g} Wh**. Night hours: **{h_night:g} h**.",
            "",
            "The label is on declared corners only; it is not a claim that the box will live. "
            "The human who can lose the box signs. No measurement by us; all values printed "
            "by the team or NIST.",
            "",
        ]
    )
    dest.write_text("\n".join(lines), encoding="utf-8")


def write_inputs_csv(fix: dict[str, Any], rec: dict[str, Any], dest: Path) -> None:
    with dest.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=("input", "value", "unit", "cite"))
        w.writeheader()
        for name, spec in (fix.get("fields") or {}).items():
            if not isinstance(spec, dict):
                continue
            val = spec.get("value")
            if spec.get("tier") == "OPEN" or val is None:
                value = "OPEN"
                cite = "OPEN"
            elif spec.get("tier") == "derived":
                value = val if not isinstance(val, list) else json.dumps(val)
                cite = f"derived_from {spec.get('derived_from')}; {spec.get('cite')}"
            else:
                value = val if not isinstance(val, list) else json.dumps(val)
                cite = str(spec.get("cite") or "")
            w.writerow(
                {
                    "input": name,
                    "value": value,
                    "unit": spec.get("unit") or "",
                    "cite": cite,
                }
            )
            if name == "T_env_K" and spec.get("tier") == "OPEN":
                lo_b = spec.get("bracket_lo") or {}
                hi_b = spec.get("bracket_hi") or {}
                if lo_b:
                    w.writerow(
                        {
                            "input": "T_env_K_bracket_lo",
                            "value": lo_b.get("printed") or lo_b.get("value"),
                            "unit": "K",
                            "cite": str(lo_b.get("cite") or ""),
                        }
                    )
                if hi_b:
                    w.writerow(
                        {
                            "input": "T_env_K_bracket_hi",
                            "value": hi_b.get("printed") or hi_b.get("value"),
                            "unit": hi_b.get("unit") or "K",
                            "cite": str(hi_b.get("cite") or ""),
                        }
                    )
        w.writerow(
            {
                "input": "label",
                "value": rec["label"],
                "unit": "",
                "cite": "declared corners only; not a claim that the box will live",
            }
        )
        w.writerow(
            {
                "input": "edge",
                "value": "true" if rec.get("edge") else "false",
                "unit": "",
                "cite": "true when label LIVE and worst-corner margin ≤ 2% of store",
            }
        )
        if rec.get("worst_corner_margin_Wh") is not None:
            w.writerow(
                {
                    "input": "worst_corner_margin_Wh",
                    "value": f"{float(rec['worst_corner_margin_Wh']):.2f}",
                    "unit": "Wh",
                    "cite": "store minus E_night at the worst declared corner",
                }
            )
        if rec.get("p_night_threshold_W") is not None:
            w.writerow(
                {
                    "input": "p_night_threshold_W",
                    "value": f"{float(rec['p_night_threshold_W']):.6g}",
                    "unit": "W",
                    "cite": "usable × discharge / (1 + load uncertainty)",
                }
            )
        for r in rec.get("ladder") or []:
            w.writerow(
                {
                    "input": f"ladder_{r['rung']}_W",
                    "value": f"{float(r['P_W']):.6g}",
                    "unit": "W",
                    "cite": r["cite"],
                }
            )
        for r in rec.get("ladder_soc8") or []:
            w.writerow(
                {
                    "input": f"ladder_soc8_{r['rung']}_W",
                    "value": f"{float(r['P_W']):.6g}",
                    "unit": "W",
                    "cite": r["cite"],
                }
            )
        brk = rec.get("breaks") or []
        for b in brk:
            w.writerow(
                {
                    "input": f"BREAK_{b['knob']}",
                    "value": _fmt(b.get("value")),
                    "unit": b.get("unit") or "",
                    "cite": f"hours={_fmt(b.get('hours'))}; {b.get('held')}",
                }
            )
        if rec.get("label") == "LINE_OPEN_TWO_KNOBS":
            w.writerow(
                {
                    "input": "identity_line",
                    "value": rec.get("identity") or "",
                    "unit": "",
                    "cite": f"H_night {rec['H_night_h']:g} h; no store is chosen",
                }
            )
            for row in rec.get("identity_table") or []:
                kwh = row["nameplate_kWh"]
                w.writerow(
                    {
                        "input": f"assumed_nameplate_{kwh:g}kWh_usable_Wh",
                        "value": f"{row['usable_Wh']:.6g}",
                        "unit": "Wh",
                        "cite": row["reserve_label"],
                    }
                )
                w.writerow(
                    {
                        "input": f"assumed_nameplate_{kwh:g}kWh_max_hibernation_W",
                        "value": f"{row['max_avg_hibernation_load_W']:.6g}",
                        "unit": "W",
                        "cite": row["reserve_label"],
                    }
                )


def write_receipt(rec: dict[str, Any], report: dict[str, Any], dest: Path) -> None:
    h_night = float(rec["H_night_h"])
    rows = [
        "NIGHT LINE RECEIPT",
        f"box {rec['box_id']}",
        f"label {rec['label_display']}",
    ]
    if rec.get("label") == "LINE_OPEN_TWO_KNOBS":
        rows.append(str(rec.get("identity_line") or rec.get("identity") or ""))
        rows.append("no store is chosen")
        for row in rec.get("identity_table") or []:
            rows.append(
                f"ASSUMED {row['nameplate_kWh']:g} kWh  usable {row['usable_Wh']:.2f} Wh  "
                f"load {row['max_avg_hibernation_load_W']:.2f} W"
            )
    else:
        hi = rec["hi"]
        brk = {b["knob"]: b for b in rec.get("breaks") or []}
        rows.append(
            f"worst_corner {hi['E_night_Wh']:.2f} Wh / {hi['hours_lived']:.2f} h "
            f"of {h_night:g} / {hi['margin_Wh']:+.2f} Wh"
        )
        if rec.get("ladder"):
            rows.append(
                "ladder "
                + " ".join(f"{r['rung']}={float(r['P_W']):.2f}W" for r in rec["ladder"])
            )
        if rec.get("p_night_threshold_soc8_W") is not None:
            rows.append(f"soc8_line {float(rec['p_night_threshold_soc8_W']):.2f} W")
        a = brk.get("A_rad_m2")
        g = brk.get("G_path_W_per_K")
        pe = brk.get("P_electronics_W")
        if a:
            rows.append(
                f"BREAK A_rad {_fmt(a.get('value'), 3)} m2 hours={_fmt(a.get('hours'))}"
            )
        if g:
            rows.append(
                f"BREAK G {_fmt(g.get('value'), 5)} W/K hours={_fmt(g.get('hours'))}"
            )
        if pe:
            rows.append(
                f"BREAK P_electronics {_fmt(pe.get('value'), 3)} W hours={_fmt(pe.get('hours'))}"
            )
    rows.append(f"sources_sha256 {'PASS' if report.get('sources_sha256_ok') else 'FAIL'}")
    rows.append(f"ladder_recompute {'PASS' if report.get('ladder_recompute_ok') else 'FAIL'}")
    for u in report.get("url_status") or []:
        rows.append(f"url {u.get('url')} status={u.get('status')} live={u.get('live')}")
    rows.append("command night-line --all")
    rows.append("no measurement by us; all values printed by the team or NIST")
    rows.append("")
    dest.write_text("\n".join(rows), encoding="utf-8")


def run_one(path: Path, out_root: Path) -> dict[str, Any]:
    fix = load_box(path)
    rec = evaluate(fix)
    box_id = str(rec["box_id"])
    dest = out_root / box_id
    dest.mkdir(parents=True, exist_ok=True)
    report = verify_box(fix, rec, root=ROOT)
    write_line_md(rec, dest / "LINE.md")
    write_inputs_csv(fix, rec, dest / "INPUTS.csv")
    write_receipt(rec, report, dest / "RECEIPT.txt")
    rec["out_dir"] = str(dest)
    rec["verify"] = report
    return rec


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(prog="night-line")
    p.add_argument("box", nargs="?", help="path to a box JSON (default: packaged boxes)")
    p.add_argument("--all", action="store_true", help="run every packaged box")
    p.add_argument("--out", type=Path, default=OUT_DEFAULT)
    args = p.parse_args(argv)
    if args.all or args.box is None:
        paths = packaged_boxes()
        if args.box is not None:
            paths = [Path(args.box)]
    else:
        paths = [Path(args.box)]
    if args.all:
        paths = packaged_boxes()
    if not paths:
        print("no boxes", file=sys.stderr)
        return 2
    for path in paths:
        rec = run_one(path, args.out)
        if rec.get("label") == "LINE_OPEN_TWO_KNOBS":
            print(rec["box_id"], rec["label_display"])
            continue
        print(
            rec["box_id"],
            rec["label_display"],
            "worst",
            round(float(rec["hi"]["E_night_Wh"]), 2),
            round(float(rec["hi"]["hours_lived"]), 2),
            f"{float(rec['hi']['margin_Wh']):+.2f}",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""night-line CLI: reproduce published lines from cited inputs."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from night_line.model import (
    BONUS_DURATION_LINE,
    IDENTITY_DURATION_LINE,
    IDENTITY_HEAT_LINE,
    IDENTITY_STORE_LINE,
    CLAIM_VS_WITNESS,
    HEAT_VS_BONUS,
    LINE_OPEN_TWO_KNOBS,
    LIVE_IF_STORE_ABOVE,
    ROOT,
    evaluate,
    load_box,
    packaged_boxes,
)
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
    label = _label_line(rec)
    box = rec["box"]
    if rec["label"] == HEAT_VS_BONUS:
        p_th = rec.get("P_thermal_W")
        hq = rec.get("heat_quotes") or {}
        bq = rec.get("bonus_quotes") or {}
        lines = [
            f"# {box} Night Line — 2026-09-17",
            "",
            f"**Label: {label}**",
            "",
            str(rec.get("identity_line") or rec.get("identity") or IDENTITY_HEAT_LINE),
            "",
            rec.get("live_if_electrical")
            or (
                "LIVE_IF a printed electrical keep-alive W is covered through a "
                "printed full-night duration by a printed store — not 5 Wt × 354 h."
            ),
            "",
            "## Heat identity (5 Wt is heat)",
            "",
            f"P_thermal_W **{p_th:g} Wt**. Kind: heat. Not electrical bus watts.",
            f'"{hq.get("thermal") or ""}"',
            f'"{hq.get("rhu") or ""}"',
            "Electrical keep-alive **OPEN**. Store **OPEN**. Do not treat 5 Wt as P_elec.",
            "",
            "## NASA CS-8 bonus (duration + transmit, not Wh)",
            "",
            rec.get("bonus_duration_line") or BONUS_DURATION_LINE,
            f'"{bq.get("cs8") or ""}"',
            "Bonus hours **not printed**. Cataldo/Mason 354 h is duration identity only. "
            "Do not compute 5 Wt × 354 h as electrical watt-hours.",
            "",
            "## NET as printed",
            "",
            f"launch_NET **{rec.get('launch_NET')}**. Firefly PR does not print CS-8. "
            "CS-8 is the NASA Ignition paid bonus.",
            "",
            "BGM1 ~5 h after sunset is a different mission. It is not this box's after_sunset. "
            "Do not put Blue Ghost >400 W bus on this package.",
            "",
            "The label is not a claim that the box will live. "
            "The human who can lose the box signs. No measurement by us; all values printed "
            "by the team or NIST.",
            "",
        ]
        dest.write_text("\n".join(lines), encoding="utf-8")
        return
    if rec["label"] == CLAIM_VS_WITNESS:
        after = rec.get("after_sunset_h")
        cataldo = rec.get("cataldo_mason_night_h")
        gap = rec.get("duration_gap_h")
        pq = rec.get("product_quotes") or {}
        fq = rec.get("flown_quotes") or {}
        lines = [
            f"# {box} Night Line — 2026-09-17",
            "",
            f"**Label: {label}**",
            "",
            str(rec.get("identity_line") or rec.get("identity") or IDENTITY_DURATION_LINE),
            "",
            "Flown cited night against the public product sentence. "
            "Store Wh OPEN. energy_wh null. Do not invent watt-hours. "
            "Not a DIE on invented Wh.",
            "",
            "## Public product language",
            "",
            f'Surface Operations: "{pq.get("surface_ops") or rec.get("product_surface_ops")}"',
            f'Power: "{pq.get("power") or rec.get("payload_power_quote")}"',
            "The product page does not print 354 h. Peak vs night keep-alive: OPEN.",
            "",
            "## Flown record",
            "",
            f"after_sunset_h **{after:g} h**. designed_for_night **false**. "
            "woke_after_night **false**.",
            f'"{fq.get("after_sunset") or ""}"',
            f'"{fq.get("not_designed") or ""}"',
            "",
            "## Duration gap (not Wh)",
            "",
            f"`{rec.get('identity') or IDENTITY_DURATION_LINE}`",
            f"Flown **{after:g} h** after sunset vs **{cataldo:g} h** Cataldo/Mason "
            f"= **{gap:g} h** duration gap. Not a DIE on invented Wh.",
            "",
            "store_Wh **OPEN**. energy_wh **null**. Do not multiply >400 W × 354 h.",
            "",
            "The label is not a claim that the box will live. "
            "The human who can lose the box signs. No measurement by us; all values printed "
            "by the team or NIST.",
            "",
        ]
        dest.write_text("\n".join(lines), encoding="utf-8")
        return
    h_night = float(rec["H_night_h"])
    if rec["label"] == LINE_OPEN_TWO_KNOBS:
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
    if rec["label"] == LIVE_IF_STORE_ABOVE:
        table = rec.get("identity_table") or []
        p_load = rec.get("P_keepalive_W")
        nameplate = rec.get("nameplate_line_Wh")
        lines = [
            f"# {box} Night Line — 2026-09-17",
            "",
            f"**Label: {label}**",
            "",
            f"Lives iff night store > {float(nameplate):.0f} Wh "
            f"(printed ~{p_load:g} W × {h_night:g} h). "
            "Reserve OPEN — SOC/efficiency not printed. "
            "~19 kg battery is mass, not watt-hours.",
            "",
            f"`{rec.get('identity') or IDENTITY_STORE_LINE}`",
            f"Printed overnight electronics **{p_load:g} W** × H_night **{h_night:g} h** "
            f"(Cataldo/Mason) = **{float(nameplate):.0f} Wh** nameplate. "
            "Store **OPEN**. Reserve **OPEN**.",
            "",
            "SOC/efficiency not printed. Nameplate 1770 Wh stands. "
            "The 30% ConOps row is **ASSUMED** — usable line is a higher store, "
            "not a picked Wh.",
            "",
            "| reserve | nameplate store Wh | usable Wh | label |",
            "|---|---|---|---|",
        ]
        for row in table:
            frac = float(row["reserve_frac"])
            lines.append(
                f"| {frac:.0%} | {float(row['nameplate_line_Wh']):.2f} | "
                f"{float(row['usable_Wh']):.2f} | {row['reserve_label']} |"
            )
        lines.extend(
            [
                "",
                "Do not convert 19 kg to Wh. Do not pick the ASSUMED nameplate.",
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
        if rec.get("label") == LINE_OPEN_TWO_KNOBS:
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
        if rec.get("label") == LIVE_IF_STORE_ABOVE:
            w.writerow(
                {
                    "input": "identity_line",
                    "value": rec.get("identity") or IDENTITY_STORE_LINE,
                    "unit": "",
                    "cite": rec.get("identity_line") or "",
                }
            )
            w.writerow(
                {
                    "input": "nameplate_line_Wh",
                    "value": f"{float(rec['nameplate_line_Wh']):.6g}",
                    "unit": "Wh",
                    "cite": "printed load × H_night; store OPEN",
                }
            )
            for i, row in enumerate(rec.get("identity_table") or []):
                w.writerow(
                    {
                        "input": f"store_line_{i}_nameplate_Wh",
                        "value": f"{float(row['nameplate_line_Wh']):.6g}",
                        "unit": "Wh",
                        "cite": row["reserve_label"],
                    }
                )
        if rec.get("label") == CLAIM_VS_WITNESS:
            w.writerow(
                {
                    "input": "identity_line",
                    "value": rec.get("identity") or IDENTITY_DURATION_LINE,
                    "unit": "",
                    "cite": rec.get("identity_line") or "",
                }
            )
            w.writerow(
                {
                    "input": "after_sunset_h",
                    "value": f"{float(rec['after_sunset_h']):g}",
                    "unit": "h",
                    "cite": "flown; Firefly wrap-up / LPSC 1958",
                }
            )
            w.writerow(
                {
                    "input": "energy_wh",
                    "value": "null",
                    "unit": "Wh",
                    "cite": "OPEN — do not invent watt-hours",
                }
            )
            w.writerow(
                {
                    "input": "duration_gap_h",
                    "value": f"{float(rec['duration_gap_h']):g}",
                    "unit": "h",
                    "cite": "Cataldo/Mason 354 h minus flown after_sunset_h",
                }
            )
        if rec.get("label") == HEAT_VS_BONUS:
            w.writerow(
                {
                    "input": "identity_line",
                    "value": rec.get("identity") or IDENTITY_HEAT_LINE,
                    "unit": "",
                    "cite": rec.get("identity_line") or "",
                }
            )
            w.writerow(
                {
                    "input": "P_thermal_W",
                    "value": f"{float(rec['P_thermal_W']):g}",
                    "unit": "Wt",
                    "cite": "heat, not electrical bus watts",
                }
            )
            w.writerow(
                {
                    "input": "after_sunset_h",
                    "value": "null",
                    "unit": "h",
                    "cite": "not this box; BGM1 5 h is another mission",
                }
            )
            w.writerow(
                {
                    "input": "bonus_duration_line",
                    "value": rec.get("bonus_duration_line") or BONUS_DURATION_LINE,
                    "unit": "",
                    "cite": "NASA CS-8 STN bonus",
                }
            )


def write_receipt(rec: dict[str, Any], report: dict[str, Any], dest: Path) -> None:
    rows = [
        "NIGHT LINE RECEIPT",
        f"box {rec['box_id']}",
        f"label {rec['label_display']}",
    ]
    if rec.get("label") == HEAT_VS_BONUS:
        rows.append(str(rec.get("identity_line") or rec.get("identity") or ""))
        rows.append(f"P_thermal_W {float(rec['P_thermal_W']):g} Wt heat")
        rows.append("P_keepalive OPEN; store OPEN")
        rows.append("after_sunset_h null; not BGM1 5 h")
        rows.append(str(rec.get("bonus_duration_line") or BONUS_DURATION_LINE))
        rows.append("do not mint watt-hours from 5 Wt x 354 h")
    elif rec.get("label") == CLAIM_VS_WITNESS:
        rows.append(str(rec.get("identity_line") or rec.get("identity") or ""))
        rows.append(f"after_sunset_h {float(rec['after_sunset_h']):g}")
        rows.append("energy_wh null")
        rows.append(f"duration_gap_h {float(rec['duration_gap_h']):g}")
        rows.append("store OPEN; not DIE on invented Wh")
    elif rec.get("label") == LINE_OPEN_TWO_KNOBS:
        rows.append(str(rec.get("identity_line") or rec.get("identity") or ""))
        rows.append("no store is chosen")
        for row in rec.get("identity_table") or []:
            rows.append(
                f"ASSUMED {row['nameplate_kWh']:g} kWh  usable {row['usable_Wh']:.2f} Wh  "
                f"load {row['max_avg_hibernation_load_W']:.2f} W"
            )
    elif rec.get("label") == LIVE_IF_STORE_ABOVE:
        h_night = float(rec["H_night_h"])
        rows.append(str(rec.get("identity_line") or rec.get("identity") or ""))
        rows.append(
            f"nameplate {float(rec['nameplate_line_Wh']):.2f} Wh  "
            f"load {rec['P_keepalive_W']:g} W × {h_night:g} h"
        )
        for row in rec.get("identity_table") or []:
            tag = "ASSUMED" if "ASSUMED" in str(row.get("reserve_label") or "") else "OPEN"
            rows.append(
                f"{tag} nameplate {float(row['nameplate_line_Wh']):.2f} Wh  "
                f"usable {float(row['usable_Wh']):.2f} Wh"
            )
    else:
        h_night = float(rec["H_night_h"])
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
        if rec.get("label") in (
            LINE_OPEN_TWO_KNOBS,
            LIVE_IF_STORE_ABOVE,
            CLAIM_VS_WITNESS,
            HEAT_VS_BONUS,
        ):
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

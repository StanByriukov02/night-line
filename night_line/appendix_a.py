"""Dump a payload Appendix A Night Line table locally. Does not mint watts. Does not write LINES.md."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from night_line.model import ROOT

INPUTS: tuple[str, ...] = (
    "named_box",
    "host",
    "surface_conops",
    "payload_ops_window",
    "store_Wh",
    "reserve_soc_pct",
    "charge_discharge_eta",
    "load_uncertainty",
    "night_hours_darkness",
    "average_night_electrical_load_W",
    "electronics_dissipation_W",
    "heater_W",
    "T_box",
    "T_env_bounds",
    "radiator_area_m2",
    "e_star",
    "G_or_strut_AL_named_alloy",
    "signer",
    "public_row",
)

LAW = (
    "Survive-the-Night as a task-order name is not a watt-hour. "
    "A lunar-day ops window is not Cataldo night unless the page labels darkness. "
    "OPEN stays OPEN. Fill status cited / team_provided / OPEN. "
    "Every number needs a URL and a page or figure. "
    "A hostile reviewer who read the TO briefing cannot kill OPEN knobs you named. "
    "They can kill a store you invented from the TO name."
)

WHY = (
    "The other suite sizes night from the Survive-the-Night task-order name. "
    "You freeze Appendix A from this table: cited numbers or OPEN cells. "
    "Faster than mixing a TO name into a store. "
    "More precise: a lunar-day ops window is not darkness hours. "
    "More reliable: a stranger can recompute from the URL in url_page. "
    "A hostile reviewer cannot kill OPEN knobs you named. "
    "They can kill a store you invented from the TO name."
)


def _quote_map(ride: dict[str, Any]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for q in ride.get("quotes") or []:
        if not isinstance(q, dict):
            continue
        text = str(q.get("text") or "")
        meta = {
            "url": str(q.get("url") or ""),
            "page_or_figure": str(q.get("page_or_figure") or ""),
            "text": text,
        }
        if "single lunar day" in text:
            out["surface_conops"] = meta
        if "280 hour payload operations window" in text:
            out["payload_ops_window"] = meta
        if "Survive the Night (Future TO CP-32)" in text:
            out["stn_to_name"] = meta
        if "no night operations supported" in text:
            out["threshold_no_night_ops"] = meta
        if "Appendix A" in text and "power" in text:
            out["appendix_a_status"] = meta
    return out


def rows_for_ride(ride: dict[str, Any] | None) -> list[dict[str, str]]:
    quotes = _quote_map(ride or {})
    cited = (ride or {}).get("cited") or {}
    named = str((ride or {}).get("named_box") or "")
    host = str((ride or {}).get("host") or "")
    rows: list[dict[str, str]] = []
    for name in INPUTS:
        status = "OPEN"
        value = ""
        url_page = ""
        notes = ""
        if name == "named_box" and named:
            status = "cited"
            value = named
        elif name == "host" and host:
            status = "cited"
            value = host
        elif name == "surface_conops" and "surface_conops" in quotes:
            status = "cited"
            value = quotes["surface_conops"]["text"]
            url_page = (
                quotes["surface_conops"]["url"]
                + " "
                + quotes["surface_conops"]["page_or_figure"]
            )
            notes = "Do not treat this as darkness hours."
        elif name == "payload_ops_window" and "payload_ops_window" in quotes:
            status = "cited"
            value = quotes["payload_ops_window"]["text"]
            url_page = (
                quotes["payload_ops_window"]["url"]
                + " "
                + quotes["payload_ops_window"]["page_or_figure"]
            )
            notes = "Do not treat this as night store hours."
        elif name == "store_Wh" and cited.get("store_Wh_printed") is False:
            status = "OPEN"
            notes = "Nameplate Wh, or OPEN. Do not mint from kg."
        elif name == "average_night_electrical_load_W" and cited.get(
            "night_W_printed"
        ) is False:
            status = "OPEN"
            notes = "Night keep-alive W, or OPEN. TO Survive-the-Night is not this cell."
        elif name == "night_hours_darkness":
            status = "OPEN"
            notes = "Darkness hours if a store is claimed. Cataldo 354 h is a reference, not this payload's print."
        elif name == "public_row":
            status = "OPEN"
            notes = "allow a dated public row, or keep LINE private"
        rows.append(
            {
                "input": name,
                "status": status,
                "value": value,
                "url_page": url_page.strip(),
                "notes": notes,
            }
        )
    extra = []
    if "stn_to_name" in quotes:
        extra.append(
            {
                "input": "stn_to_name",
                "status": "cited",
                "value": quotes["stn_to_name"]["text"],
                "url_page": (
                    quotes["stn_to_name"]["url"]
                    + " "
                    + quotes["stn_to_name"]["page_or_figure"]
                ).strip(),
                "notes": "Not a watt-hour. NL-A1.",
            }
        )
    if "threshold_no_night_ops" in quotes:
        extra.append(
            {
                "input": "threshold_no_night_ops",
                "status": "cited",
                "value": quotes["threshold_no_night_ops"]["text"],
                "url_page": (
                    quotes["threshold_no_night_ops"]["url"]
                    + " "
                    + quotes["threshold_no_night_ops"]["page_or_figure"]
                ).strip(),
                "notes": "CONOPS bound, not a keep-alive W. NL-A3.",
            }
        )
    if "appendix_a_status" in quotes:
        extra.append(
            {
                "input": "appendix_a_status",
                "status": "cited",
                "value": quotes["appendix_a_status"]["text"],
                "url_page": (
                    quotes["appendix_a_status"]["url"]
                    + " "
                    + quotes["appendix_a_status"]["page_or_figure"]
                ).strip(),
                "notes": "Fill store/W before freezing power.",
            }
        )
    return extra + rows


def write_dump(dest: Path, rows: list[dict[str, str]]) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    csv_path = dest / "APPENDIX_A_INPUTS.csv"
    with csv_path.open("w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=("input", "status", "value", "url_page", "notes"),
            lineterminator="\n",
        )
        w.writeheader()
        for row in rows:
            w.writerow(row)
    (dest / "LAW.txt").write_text(LAW + "\n", encoding="utf-8", newline="\n")
    (dest / "WHY.txt").write_text(WHY + "\n", encoding="utf-8", newline="\n")


def load_ride(ride_id: str) -> dict[str, Any]:
    path = ROOT / "night_line" / "rides" / f"{ride_id}.json"
    if not path.is_file():
        # packaged next to this module
        path = Path(__file__).resolve().parent / "rides" / f"{ride_id}.json"
    if not path.is_file():
        raise FileNotFoundError(ride_id)
    return json.loads(path.read_text(encoding="utf-8"))


def appendix_a_main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="night-line appendix-a")
    p.add_argument(
        "--ride",
        default="",
        help=(
            "optional ride_id to prefill cited CONOPS (example: dimple_cp32). "
            "Writes the Appendix A table a competing suite does not have. Does not mint W."
        ),
    )
    p.add_argument("--out", type=Path, default=ROOT / "out")
    args = p.parse_args(argv)
    ride = load_ride(args.ride) if args.ride else None
    dest = args.out / "appendix_a" / (args.ride or "blank")
    write_dump(dest, rows_for_ride(ride))
    print(dest / "APPENDIX_A_INPUTS.csv")
    return 0

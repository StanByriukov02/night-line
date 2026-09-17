"""Witness map: named box on named host — can this ride witness a lunar night?

Not a seventh energy line. Not a closed CLPS tracker.
MANIFEST_CLOSED is always false. Unnamed task orders are absent, not CANNOT.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from night_line.model import BOXES
from night_line.verify import independent_full_night_possible, independent_ride_label

RIDES = Path(__file__).resolve().parent / "rides"

# Host row vs payload row on the same landing. A lab may not take one as the other.
INHERIT_PAIRS = (
    (
        "griffin1_lander",
        "flip_griffin1",
        "Griffin PUG excludes lunar night. That is not FLIP’s survive-the-night sentence. FLIP’s sentence is not a Griffin night-store.",
    ),
    (
        "bgm2_lander",
        "lusee_night",
        "Blue Ghost Mission 2 powers off before nightfall. That is not LuSEE’s store. LuSEE’s store is not a Blue Ghost night-store.",
    ),
)


def inherit_forbidden(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by = {str(r["ride_id"]): r for r in rows}
    out: list[dict[str, Any]] = []
    for host_id, payload_id, why in INHERIT_PAIRS:
        if host_id in by and payload_id in by:
            out.append(
                {
                    "host_ride_id": host_id,
                    "payload_ride_id": payload_id,
                    "allowed": False,
                    "why": why,
                }
            )
    return out


def packaged_rides() -> list[Path]:
    return sorted(RIDES.glob("*.json"))


def load_ride(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("ride file is not an object")
    if raw.get("schema") != "night_line_ride_v1":
        raise ValueError("ride schema")
    return raw


def full_night_possible(label: str) -> str:
    return independent_full_night_possible(label)


def evaluate_ride(fix: dict[str, Any]) -> dict[str, Any]:
    cited = dict(fix.get("cited") or {})
    label = independent_ride_label(cited)
    store = cited.get("store_Wh_printed")
    return {
        "ride_id": fix["ride_id"],
        "named_box": fix["named_box"],
        "host": fix["host"],
        "window": fix["window"],
        "label": label,
        "full_night_possible": full_night_possible(label),
        "store_Wh_printed": bool(store),
        "lab_use": str(fix.get("lab_use") or ""),
        "quotes": list(fix.get("quotes") or []),
        "sources_dir": str(fix.get("sources_dir") or ""),
        "landing_date": cited.get("landing_date") or "OPEN",
        "launch_net_is_not_sunset": True,
        "manifest_closed": False,
        "adds_energy_box": False,
        "measured": False,
    }


def evaluate_map(paths: list[Path] | None = None) -> dict[str, Any]:
    rows = []
    for path in paths or packaged_rides():
        rows.append(evaluate_ride(load_ride(path)))
    rows.sort(key=lambda r: str(r["ride_id"]))
    return {
        "schema": "night_line_witness_map_v1",
        "dated": "2026-09-17",
        "manifest_closed": False,
        "measured": False,
        "set_note": (
            "This set is not closed. Unpublished NASA Lunar Payload Database, "
            "unnamed CLPS task orders, and hosts without a saved public print "
            "are absent — not CANNOT."
        ),
        "rows": rows,
        "inherit_forbidden": inherit_forbidden(rows),
        "n_packaged_energy_boxes": len(list(BOXES.glob("*.json"))),
    }


def write_map_md(doc: dict[str, Any], dest: Path) -> None:
    lines = [
        "# Witness map — named box on named host",
        "",
        f"Dated **{doc['dated']}**. **MEASURED=false**. **MANIFEST_CLOSED=false**.",
        "",
        str(doc["set_note"]),
        "",
        "A landing name is not a row. Blue Ghost Mission 2 the lander, and LuSEE-Night "
        "the payload, are two rows. Griffin-1 the lander, and FLIP the rover, are two rows. "
        "Launch NET is not a sunset.",
        "",
        "| named box | host | window | label | full night? | store Wh printed | what a lab does with this |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in doc["rows"]:
        store = "yes" if r["store_Wh_printed"] else "no"
        lab = str(r["lab_use"]).replace("|", "/")
        lines.append(
            f"| {r['named_box']} | {r['host']} | {r['window']} | {r['label']} | "
            f"{r['full_night_possible']} | {store} | {lab} |"
        )
    lines.extend(
        [
            "",
            "## Do not inherit (host ≠ payload)",
            "",
        ]
    )
    for pair in doc.get("inherit_forbidden") or []:
        lines.append(
            f"- `{pair['host_ride_id']}` ↛ `{pair['payload_ride_id']}`: {pair['why']}"
        )
        lines.append("")
    lines.extend(
        [
            "## Quotes (cited)",
            "",
        ]
    )
    for r in doc["rows"]:
        lines.append(f"### {r['named_box']} on {r['host']}")
        lines.append("")
        for q in r["quotes"]:
            text = str(q.get("text") or "")
            url = str(q.get("url") or "")
            page = str(q.get("page_or_figure") or "")
            lines.append(f"- “{text}” — {page} — {url}")
        lines.append("")
    lines.extend(
        [
            "Reproduce: `night-line witness-map`. Energy lines stay on `LINES.md` "
            f"({doc['n_packaged_energy_boxes']} packaged boxes). This map does not add a box.",
            "",
        ]
    )
    dest.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_map_csv(doc: dict[str, Any], dest: Path) -> None:
    import csv

    fields = [
        "ride_id",
        "named_box",
        "host",
        "window",
        "label",
        "full_night_possible",
        "store_Wh_printed",
        "landing_date",
        "lab_use",
    ]
    with dest.open("w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in doc["rows"]:
            w.writerow({k: r.get(k) for k in fields})

"""Overlay one team_provided input (URL + page required). Does not write LINES.md."""
from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from datetime import date
from pathlib import Path
from typing import Any

from night_line.model import BOXES, ROOT, evaluate, load_box, packaged_boxes
from night_line.verify import verify_box

LINES_MD = ROOT / "LINES.md"


class CloseError(ValueError):
    """REFUSE a close: missing page/URL, bad value, or unknown input."""


def resolve_box_path(box: str) -> Path:
    raw = Path(box)
    if raw.is_file():
        return raw.resolve()
    name = raw.name
    stem = raw.stem if name.endswith(".json") else name
    unders = stem.replace("-", "_")
    for cand in (
        BOXES / name,
        BOXES / f"{stem}.json",
        BOXES / f"{unders}.json",
    ):
        if cand.is_file():
            return cand
    want = {stem, unders, stem.replace("_", "-")}
    for path in packaged_boxes():
        if path.stem in want or path.name in want:
            return path
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        bid = str(data.get("box_id") or "")
        if bid in want or bid.replace("_", "-") in want:
            return path
    raise FileNotFoundError(box)


def overlay_team_provided(
    fix: dict[str, Any],
    *,
    input_name: str,
    value: float,
    url: str,
    page: str,
) -> dict[str, Any]:
    url_s = str(url).strip()
    page_s = str(page).strip()
    if not url_s:
        raise CloseError("REFUSE: --url is required")
    if not page_s:
        raise CloseError("REFUSE: --page is required (page or figure)")
    if not math.isfinite(float(value)):
        raise CloseError("REFUSE: --value is not a finite float")
    overlay = copy.deepcopy(fix)
    fields = overlay.get("fields")
    if not isinstance(fields, dict) or input_name not in fields:
        raise CloseError(f"REFUSE: unknown input {input_name}")
    prev = fields[input_name]
    if not isinstance(prev, dict):
        raise CloseError(f"REFUSE: unknown input {input_name}")
    val = float(value)
    fields[input_name] = {
        "value": val,
        "unit": prev.get("unit") or "",
        "tier": "team_provided",
        "cite": f"team_provided {url_s} ({page_s})",
        "url": url_s,
        "source_slug": None,
        "numbers_used": f"{input_name}={val}",
        "page_or_figure": page_s,
    }
    br = overlay.get("geometry_bracket")
    if isinstance(br, dict) and input_name in br and isinstance(br[input_name], dict):
        slot = br[input_name]
        if "lo" in slot and "hi" in slot:
            slot["lo"] = val
            slot["hi"] = val
        if "value" in slot:
            slot["value"] = val
        slot["tier"] = "team_provided"
        slot["cite"] = f"team_provided {url_s} ({page_s})"
    return overlay


def _is_synthetic(url: str, page: str) -> bool:
    blob = f"{url} {page}".lower()
    return "example.invalid" in blob or "synthetic" in blob


def append_close_overlay_md(dest: Path, rec: dict[str, Any]) -> None:
    ov = rec.get("close_overlay")
    if not isinstance(ov, dict):
        return
    extra = [
        "",
        "## team_provided overlay",
        "",
        f"`{ov.get('input')}` **{ov.get('value')}** {ov.get('unit') or ''} — tier team_provided.",
        f"URL: {ov.get('url')}",
        f"Page or figure: {ov.get('page_or_figure')}",
        "This command does not write LINES.md.",
    ]
    if ov.get("synthetic"):
        extra.append(
            "SYNTHETIC fixture. Not a published LEMS-A3 (Benna) number. "
            "Public LINES.md is unchanged."
        )
    text = dest.read_text(encoding="utf-8").rstrip() + "\n" + "\n".join(extra) + "\n"
    dest.write_text(text, encoding="utf-8", newline="\n")


def run_close(
    *,
    box: str,
    input_name: str,
    value: float,
    url: str,
    page: str,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    from night_line.cli import write_inputs_csv, write_line_md, write_receipt

    path = resolve_box_path(box)
    fix = load_box(path)
    overlay = overlay_team_provided(
        fix,
        input_name=input_name,
        value=value,
        url=url,
        page=page,
    )
    rec = evaluate(overlay)
    box_id = str(rec.get("box_id") or overlay.get("box_id") or "box")
    dest = Path(out_dir) if out_dir is not None else (ROOT / "out" / f"close_{box_id}_{input_name}")
    dest = dest.resolve()
    if dest == LINES_MD.resolve() or dest.name == "LINES.md":
        raise CloseError("REFUSE: will not write LINES.md")
    dest.mkdir(parents=True, exist_ok=True)
    rec["date_named"] = date.today().isoformat()
    rec["command"] = (
        f"night-line close --box {box} --input {input_name} "
        f"--value {value} --url {url} --page {page}"
    )
    rec["close_overlay"] = {
        "input": input_name,
        "value": float(value),
        "unit": ((overlay.get("fields") or {}).get(input_name) or {}).get("unit") or "",
        "url": str(url).strip(),
        "page_or_figure": str(page).strip(),
        "synthetic": _is_synthetic(url, page),
    }
    report = verify_box(overlay, rec, root=ROOT)
    write_line_md(rec, dest / "LINE.md")
    append_close_overlay_md(dest / "LINE.md", rec)
    write_inputs_csv(overlay, rec, dest / "INPUTS.csv")
    write_receipt(rec, report, dest / "RECEIPT.txt")
    recpt = dest / "RECEIPT.txt"
    extra = "LINES.md not written\n"
    if "night-line close" not in recpt.read_text(encoding="utf-8"):
        extra = extra + str(rec.get("command") or "night-line close") + "\n"
    recpt.write_text(recpt.read_text(encoding="utf-8").rstrip() + "\n" + extra, encoding="utf-8", newline="\n")
    for name in ("LINE.md", "INPUTS.csv", "RECEIPT.txt"):
        p = dest / name
        p.write_bytes(p.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n"))
    rec["out_dir"] = str(dest)
    rec["verify"] = report
    rec["overlay"] = overlay
    return rec


def close_main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="night-line close",
        description=(
            "Overlay one team_provided input with URL + page or figure. "
            "Writes LINE.md / INPUTS.csv / RECEIPT.txt. Does not write LINES.md."
        ),
    )
    p.add_argument("--box", required=True, help="packaged box id or path (e.g. lems-a3)")
    p.add_argument("--input", required=True, dest="input_name", help="field name, e.g. A_rad_m2")
    p.add_argument("--value", required=True, help="float value for that input")
    p.add_argument("--url", required=True, help="URL of the page or figure")
    p.add_argument("--page", required=True, help="page or figure label, e.g. Fig. 3")
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output directory (default: out/close_<box>_<input>/)",
    )
    try:
        args = p.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 2
        return int(code)
    url = str(args.url or "").strip()
    page = str(args.page or "").strip()
    if not url:
        print("REFUSE: --url is required", file=sys.stderr)
        return 2
    if not page:
        print("REFUSE: --page is required (page or figure)", file=sys.stderr)
        return 2
    try:
        value = float(args.value)
    except ValueError:
        print("REFUSE: --value is not a float", file=sys.stderr)
        return 2
    try:
        rec = run_close(
            box=str(args.box),
            input_name=str(args.input_name),
            value=value,
            url=url,
            page=page,
            out_dir=args.out,
        )
    except CloseError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"REFUSE: box not found {exc}", file=sys.stderr)
        return 2
    print(rec.get("box_id"), rec.get("label_display"), rec.get("out_dir"))
    return 0

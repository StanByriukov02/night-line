"""Close one team_provided input. Public LINES.md is not a write target."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from night_line.cli import main
from night_line.close import CloseError, overlay_team_provided
from night_line.model import evaluate, load_box

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "night_line"
FIX = Path(__file__).resolve().parent / "fixtures" / "synthetic_lems_a_rad.json"
LINES = ROOT / "LINES.md"
BENNA_BREAK_A_RAD = 0.828


def _fixture() -> dict:
    rec = json.loads(FIX.read_text(encoding="utf-8"))
    assert rec["label"] == "SYNTHETIC"
    assert rec["url"] == "https://example.invalid/synthetic-lems-a-rad"
    assert abs(float(rec["value"]) - BENNA_BREAK_A_RAD) > 0.01
    return rec


def test_close_without_page_fails(tmp_path: Path) -> None:
    fx = _fixture()
    rc = main(
        [
            "close",
            "--box",
            fx["box"],
            "--input",
            fx["input"],
            "--value",
            str(fx["value"]),
            "--url",
            fx["url"],
            "--out",
            str(tmp_path),
        ]
    )
    assert rc != 0
    fix = load_box(PKG / "boxes" / "lems_a3.json")
    try:
        overlay_team_provided(
            fix,
            input_name=fx["input"],
            value=float(fx["value"]),
            url=fx["url"],
            page="",
        )
        raise AssertionError("expected REFUSE without page")
    except CloseError as exc:
        assert "page" in str(exc).lower()
    assert not (tmp_path / "LINE.md").exists()
    assert not (tmp_path / "INPUTS.csv").exists()


def test_close_with_page_writes_team_provided(tmp_path: Path) -> None:
    fx = _fixture()
    before = LINES.read_bytes()
    rc = main(
        [
            "close",
            "--box",
            fx["box"],
            "--input",
            fx["input"],
            "--value",
            str(fx["value"]),
            "--url",
            fx["url"],
            "--page",
            fx["page_or_figure"],
            "--out",
            str(tmp_path),
        ]
    )
    assert rc == 0
    line = (tmp_path / "LINE.md").read_text(encoding="utf-8")
    inputs = (tmp_path / "INPUTS.csv").read_text(encoding="utf-8")
    assert (tmp_path / "RECEIPT.txt").is_file()
    assert "team_provided" in line
    assert "SYNTHETIC" in line
    assert "Benna" in line
    found = None
    with (tmp_path / "INPUTS.csv").open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["input"] == "A_rad_m2":
                found = row
                break
    assert found is not None
    assert "team_provided" in found["cite"]
    assert "team_provided" in inputs
    assert abs(float(found["value"]) - float(fx["value"])) < 1e-12
    assert found["value"] != "OPEN"
    assert LINES.read_bytes() == before
    rec = evaluate(load_box(PKG / "boxes" / "lems_a3.json"))
    assert rec["label"] == "LIVE"
    assert rec["edge"] is True
    packed = json.loads((PKG / "boxes" / "lems_a3.json").read_text(encoding="utf-8"))
    assert packed["fields"]["A_rad_m2"]["tier"] == "OPEN"
    assert packed["fields"]["A_rad_m2"]["value"] is None


def test_close_does_not_write_public_lines(tmp_path: Path) -> None:
    fx = _fixture()
    before = LINES.read_bytes()
    rc = main(
        [
            "close",
            "--box",
            fx["box"],
            "--input",
            fx["input"],
            "--value",
            str(fx["value"]),
            "--url",
            fx["url"],
            "--page",
            fx["page_or_figure"],
            "--out",
            str(tmp_path),
        ]
    )
    assert rc == 0
    assert LINES.read_bytes() == before
    assert b"SYNTHETIC" not in before
    assert "example.invalid" not in LINES.read_text(encoding="utf-8")
    receipt = (tmp_path / "RECEIPT.txt").read_text(encoding="utf-8")
    assert "LINES.md not written" in receipt
    assert "night-line close" in receipt


def test_close_unknown_input_and_bad_value(tmp_path: Path) -> None:
    fx = _fixture()
    rc_unknown = main(
        [
            "close",
            "--box",
            fx["box"],
            "--input",
            "not_a_real_field",
            "--value",
            str(fx["value"]),
            "--url",
            fx["url"],
            "--page",
            fx["page_or_figure"],
            "--out",
            str(tmp_path),
        ]
    )
    assert rc_unknown != 0
    rc_bad = main(
        [
            "close",
            "--box",
            fx["box"],
            "--input",
            fx["input"],
            "--value",
            "not-a-float",
            "--url",
            fx["url"],
            "--page",
            fx["page_or_figure"],
            "--out",
            str(tmp_path),
        ]
    )
    assert rc_bad != 0
    rc_record = main(
        [
            "close",
            "--box",
            fx["box"],
            "--input",
            fx["input"],
            "--value",
            str(fx["value"]),
            "--url",
            fx["url"],
            "--page",
            fx["page_or_figure"],
            "--record",
            "--out",
            str(tmp_path),
        ]
    )
    assert rc_record != 0


def test_synthetic_fixture_has_no_kitchen_keys() -> None:
    raw = json.loads(FIX.read_text(encoding="utf-8"))
    blob = json.dumps(raw).lower()
    for bad in ("dual", "leftover", "yard", "garage", "product_works", "starship"):
        assert bad not in blob

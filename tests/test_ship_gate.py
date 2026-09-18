"""Public-ship gate: class + cabin. Does not push."""
from __future__ import annotations

from pathlib import Path

from night_line.ship_gate import classify_name, inspect_root, scan_cabin

ROOT = Path(__file__).resolve().parents[1]


def test_allowlist_classes() -> None:
    assert classify_name("LINES.md") == "record"
    assert classify_name("NIGHT_LINE_SPEC_V1.md") == "record"
    assert classify_name("PUG_NIGHT_LINE_INPUTS_V1.md") == "method"
    assert classify_name("PUG_SHALL_V1.md") == "method"
    assert classify_name("PO_SCOPE_V1.md") == "offer"
    assert classify_name("TO_NIGHT_APPENDIX_V1.md") == "offer"
    assert classify_name("EXPORT_AP_MEMO_V1.md") == "offer"
    assert classify_name("TWO_COURTS_LUSEE_V1.md") == "honesty"
    assert classify_name("TWO_COURTS_LEMS_V1.md") == "honesty"
    assert classify_name("BREAK_SURFACE_LEMS_V1.md") == "method"
    assert classify_name("MEASURE_LEMS_V1.md") == "method"
    assert classify_name("WITNESS_MAP_V1.md") == "method"
    assert classify_name("APPENDIX_A_NIGHT_INPUTS_V1.md") == "method"
    assert classify_name("FOR_A_LAB_V1.md") == "method"
    assert classify_name("RANDOM_F_PAGE.md") == "unknown"


def test_cabin_tokens() -> None:
    hits = scan_cabin("A Dual-hostile leftover of −8218.54 Wh exists.\n")
    assert hits
    assert not scan_cabin("A Night Line is one number on the team's printed store.\n")


def test_unknown_root_file_fails(tmp_path: Path) -> None:
    (tmp_path / "SLOP.md").write_text("# slop\n", encoding="utf-8")
    (tmp_path / "LINES.md").write_text("# record\n", encoding="utf-8")
    doc = inspect_root(tmp_path, go_offer=False)
    assert doc["ok"] is False
    assert any(r["file"] == "SLOP.md" and r["class"] == "unknown" for r in doc["files"])


def test_offer_refused_without_go(tmp_path: Path) -> None:
    (tmp_path / "PO_SCOPE_V1.md").write_text(
        "I provide IRS Form W-8BEN. Seller: X\n", encoding="utf-8"
    )
    doc = inspect_root(tmp_path, go_offer=False)
    assert doc["ok"] is False
    assert any("OFFER" in f for f in doc["fail"])
    doc2 = inspect_root(tmp_path, go_offer=True)
    offer = next(r for r in doc2["files"] if r["file"] == "PO_SCOPE_V1.md")
    assert offer["class"] == "offer"
    assert offer["ok"] is True


def test_live_tree_offer_and_honesty_are_visible() -> None:
    """Inventory: do not auto-PASS the live tree while offer/cabin pages sit at root."""
    doc = inspect_root(ROOT, go_offer=False)
    names = {r["file"]: r for r in doc["files"]}
    if "PO_SCOPE_V1.md" in names:
        assert names["PO_SCOPE_V1.md"]["class"] == "offer"
        assert names["PO_SCOPE_V1.md"]["ok"] is False
    if "TO_NIGHT_APPENDIX_V1.md" in names:
        assert names["TO_NIGHT_APPENDIX_V1.md"]["class"] == "offer"
        assert names["TO_NIGHT_APPENDIX_V1.md"]["ok"] is False
    if "EXPORT_AP_MEMO_V1.md" in names:
        assert names["EXPORT_AP_MEMO_V1.md"]["class"] == "offer"
        assert names["EXPORT_AP_MEMO_V1.md"]["ok"] is False
    spec = names.get("NIGHT_LINE_SPEC_V1.md")
    assert spec is not None
    assert spec["class"] == "record"
    assert spec["ok"] is True
    lab = names.get("FOR_A_LAB_V1.md")
    assert lab is not None
    assert lab["class"] == "method"
    assert lab["ok"] is True
    if "PUG_SHALL_V1.md" in names:
        assert names["PUG_SHALL_V1.md"]["class"] == "method"
        assert names["PUG_SHALL_V1.md"]["ok"] is True
    if "TWO_COURTS_LEMS_V1.md" in names:
        assert names["TWO_COURTS_LEMS_V1.md"]["class"] == "honesty"
        assert names["TWO_COURTS_LEMS_V1.md"]["ok"] is True
    assert doc["ok"] is False

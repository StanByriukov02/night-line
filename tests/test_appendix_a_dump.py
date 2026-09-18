"""Local Appendix A table dump: no GitHub, no mint, no LINES.md."""
from __future__ import annotations

from pathlib import Path

from night_line.appendix_a import appendix_a_main
from night_line.ship_gate import scan_cabin

ROOT = Path(__file__).resolve().parents[1]
LINES = ROOT / "LINES.md"


def test_dimple_dump_prefills_day_and_leaves_store_open(tmp_path: Path) -> None:
    before = LINES.read_text(encoding="utf-8") if LINES.is_file() else ""
    assert appendix_a_main(["--ride", "dimple_cp32", "--out", str(tmp_path)]) == 0
    csv_path = tmp_path / "appendix_a" / "dimple_cp32" / "APPENDIX_A_INPUTS.csv"
    law = tmp_path / "appendix_a" / "dimple_cp32" / "LAW.txt"
    text = csv_path.read_text(encoding="utf-8")
    assert not scan_cabin(text)
    assert not scan_cabin(law.read_text(encoding="utf-8"))
    assert "single lunar day of ~348 hours" in text
    assert "280 hour payload operations window" in text
    assert "Survive the Night (Future TO CP-32)" in text
    assert "no night operations supported in the threshold mission" in text
    assert "store_Wh,OPEN" in text.replace(" ", "") or "store_Wh,OPEN," in text
    assert "average_night_electrical_load_W,OPEN" in text.replace(" ", "") or (
        "average_night_electrical_load_W,OPEN," in text
    )
    assert "Not a watt-hour" in text
    assert "Do not treat this as darkness hours" in text
    why = tmp_path / "appendix_a" / "dimple_cp32" / "WHY.txt"
    why_text = why.read_text(encoding="utf-8")
    law_text = law.read_text(encoding="utf-8")
    assert not scan_cabin(why_text)
    assert "other suite" in why_text
    assert "hostile reviewer" in why_text
    assert "hostile reviewer" in law_text
    assert LINES.read_text(encoding="utf-8") == before if LINES.is_file() else True


def test_blank_dump_is_all_open(tmp_path: Path) -> None:
    assert appendix_a_main(["--out", str(tmp_path)]) == 0
    text = (tmp_path / "appendix_a" / "blank" / "APPENDIX_A_INPUTS.csv").read_text(
        encoding="utf-8"
    )
    assert "named_box,OPEN" in text or "named_box,OPEN," in text
    assert "store_Wh,OPEN" in text or "store_Wh,OPEN," in text
    assert "Survive-the-Night" in (tmp_path / "appendix_a" / "blank" / "LAW.txt").read_text(
        encoding="utf-8"
    )
    assert "other suite" in (tmp_path / "appendix_a" / "blank" / "WHY.txt").read_text(
        encoding="utf-8"
    )

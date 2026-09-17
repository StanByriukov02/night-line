"""ICES 2026 490 is a TVAC plan, not an A3 leak. No surface import."""
from pathlib import Path

from night_line.model import evaluate, load_box
from night_line.ship_gate import classify_name, scan_cabin

ROOT = Path(__file__).resolve().parents[1]
ICES = ROOT / "TWO_COURTS_LEMS_V1.md"
MEASURE = ROOT / "MEASURE_LEMS_V1.md"
SRC = ROOT / "sources" / "lems-a3" / "ices-2026-490-tvac-plan" / "page.txt"
BOX = ROOT / "night_line" / "boxes" / "lems_a3.json"


def test_court_p_quotes_and_store_untouched() -> None:
    text = ICES.read_text(encoding="utf-8")
    assert classify_name(ICES.name) == "honesty"
    assert not scan_cabin(text)
    assert "940.8" in text
    assert "849.5" in text
    assert "2.5 W" in text
    assert "will measure" in text
    assert "wrong object" in text
    src = SRC.read_text(encoding="utf-8")
    assert "2.5 Watts of heat" in src
    assert "940.8 Wh" in src
    assert "849.5 Wh" in src
    rec = evaluate(load_box(BOX))
    assert abs(float(rec["store_Wh"]) - 640.0) < 1e-9
    measure = MEASURE.read_text(encoding="utf-8")
    assert "940.8" in measure
    assert classify_name(MEASURE.name) == "method"
    assert not scan_cabin(measure)

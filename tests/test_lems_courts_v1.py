"""LEMS courts: measured TRL-6 leak vs CDR analysis vs Fourier. BREAK surface."""
from __future__ import annotations

from pathlib import Path

from night_line.cli import run_one, surface_main
from night_line.model import break_surface, evaluate, load_box
from night_line.ship_gate import classify_name, scan_cabin, scan_offer_body

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "night_line"
OUT = ROOT / "out"
ICES = ROOT / "TWO_COURTS_LEMS_V1.md"
SURFACE = ROOT / "BREAK_SURFACE_LEMS_V1.md"
MEASURE = ROOT / "MEASURE_LEMS_V1.md"


def test_trl6_measured_identity() -> None:
    measured_Wh = 1407.3
    hours = 354.0
    paper_W = 3.98
    store = 640.0
    assert abs(measured_Wh / hours - paper_W) < 0.005
    assert paper_W * hours > store
    assert abs(store / paper_W - 160.8) < 0.05
    text = ICES.read_text(encoding="utf-8")
    assert "1407.3" in text
    assert "3.98" in text
    assert "wrong box" in text
    assert "MEASURED=true" in text


def test_cdr_fig14_identity() -> None:
    assert abs(1.528 * 354.0 - 541.0) < 0.1
    assert abs(640.0 - 541.0 - 99.0) < 0.1
    text = ICES.read_text(encoding="utf-8")
    assert "1.528" in text
    assert "0.474" in text
    assert "does **not** print strut A/L" in text


def test_implied_g_is_derived_not_al() -> None:
    dT = (-29.2) - (-129.4)
    assert abs(dT - 100.2) < 1e-9
    g = 0.474 / dT
    assert abs(g - 0.00473) < 5e-6
    assert g > 0.002
    text = ICES.read_text(encoding="utf-8")
    assert "4.73 mW/K" in text
    assert "derived" in text.lower()


def test_night_line_not_overwritten_by_trl6() -> None:
    rec = evaluate(load_box(PKG / "boxes" / "lems_a3.json"))
    assert rec["label_display"] == "LIVE (edge)"
    assert abs(float(rec["P_electronics_W"]) - 1.231) < 1e-9
    assert abs(float(rec["hi"]["P_leak_W"]) - 3.98) > 1.0


def test_break_surface_roles_and_plateau() -> None:
    doc = break_surface(load_box(PKG / "boxes" / "lems_a3.json"))
    assert doc["their_print"] is False
    assert doc["MEASURED"] is False
    by = {round(float(r["value"]), 3): r for r in doc["A_rad_m2"]}
    lo = by[0.05]
    assert lo["role"] == "declared_lo"
    assert lo["their_print"] is False
    brk = next(r for r in doc["A_rad_m2"] if r["role"] == "BREAK")
    assert abs(float(brk["value"]) - 0.828) < 0.001
    assert abs(float(brk["hours_lived"]) - 354.0) < 0.05
    assert abs(float(brk["margin_Wh"])) < 0.2
    hi = next(r for r in doc["A_rad_m2"] if r["role"] == "declared_hi")
    assert abs(float(hi["margin_Wh"]) - 5.76) < 0.05
    assert hi["regime"] == "leak_bound"
    g_print = next(r for r in doc["G_path_W_per_K"] if r["role"] == "printed_G_bound")
    assert g_print["regime"] == "electronics_bound"
    hours_e = float(doc["electronics_bound_hours"])
    assert abs(hours_e - 640.0 / 1.231) < 0.05
    assert abs(float(g_print["hours_lived"]) - hours_e) < 0.2


def test_surface_cli_writes_csv(tmp_path: Path) -> None:
    rc = surface_main(["--out", str(tmp_path)])
    assert rc == 0
    a = (tmp_path / "lems_a3" / "BREAK_SURFACE_A_RAD.csv").read_text(encoding="utf-8")
    assert "declared_lo" in a
    assert "BREAK" in a
    assert "False" in a


def test_public_pages_are_method_or_honesty_and_clean() -> None:
    assert classify_name(ICES.name) == "honesty"
    assert classify_name(SURFACE.name) == "method"
    assert classify_name(MEASURE.name) == "method"
    for path in (ICES, SURFACE, MEASURE):
        text = path.read_text(encoding="utf-8")
        assert not scan_cabin(text)
        assert not scan_offer_body(text)
        assert "C-103" not in text or path == MEASURE
    measure = MEASURE.read_text(encoding="utf-8")
    assert "Do not buy C-103" in measure
    assert "ULTEM 1000" in measure
    assert "A3" in measure and "TVAC" in measure
    written = run_one(PKG / "boxes" / "lems_a3.json", OUT)
    assert written["label_display"] == "LIVE (edge)"


def test_ices_2026_tvac_plan_is_not_a_leak() -> None:
    text = ICES.read_text(encoding="utf-8")
    assert "940.8" in text
    assert "849.5" in text
    assert "2.5 W" in text
    assert "will measure" in text
    assert "wrong object" in text
    assert "wrong kind" in text
    src = (
        ROOT / "sources" / "lems-a3" / "ices-2026-490-tvac-plan" / "page.txt"
    ).read_text(encoding="utf-8")
    assert "2.5 Watts of heat" in src
    assert "940.8 Wh" in src
    assert "849.5 Wh" in src
    assert "will measure the nighttime heat leaks" in src
    rec = evaluate(load_box(PKG / "boxes" / "lems_a3.json"))
    assert abs(float(rec["store_Wh"]) - 640.0) < 1e-9
    measure = MEASURE.read_text(encoding="utf-8")
    assert "plan" in measure.lower()
    assert "940.8" in measure

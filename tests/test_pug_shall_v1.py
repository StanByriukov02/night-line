"""PUG/ICD shall block: stealable, no cabin, no pitch."""
from __future__ import annotations

from pathlib import Path

from night_line.ship_gate import classify_name, scan_cabin, scan_offer_body

ROOT = Path(__file__).resolve().parents[1]
SHALL = ROOT / "PUG_SHALL_V1.md"


def test_shall_is_method_and_present() -> None:
    assert SHALL.is_file()
    assert classify_name(SHALL.name) == "method"


def test_shall_has_eight_nl_lines() -> None:
    text = SHALL.read_text(encoding="utf-8")
    for n in range(1, 9):
        assert f"NL-{n}" in text
    assert "shall" in text.lower()


def test_shall_forbids_the_usual_lies() -> None:
    text = SHALL.read_text(encoding="utf-8")
    assert "day thermal envelope shall not be used as night T_env" in text
    assert "shall not be used as the" in text and "night store Wh" in text
    assert "Flown hours after sunset shall not be used as a PUG night-store offer" in text
    assert "shall not be used as electrical bus watts" in text
    assert "shall stay OPEN" in text
    assert "does not sign" in text


def test_shall_is_not_cabin_or_offer() -> None:
    text = SHALL.read_text(encoding="utf-8")
    assert not scan_cabin(text)
    assert not scan_offer_body(text)
    assert "W-8BEN" not in text
    assert "I'm writing because" not in text
    assert "Not selling you" not in text

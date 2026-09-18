"""Appendix A night-inputs sheet: method a PI can paste, not a seventh box."""
from __future__ import annotations

from pathlib import Path

from night_line.ship_gate import classify_name, scan_cabin

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "APPENDIX_A_NIGHT_INPUTS_V1.md"
ISSUE = ROOT / ".github" / "ISSUE_TEMPLATE" / "night_line_inputs.yml"


def test_sheet_is_method_not_cabin() -> None:
    assert PAGE.is_file()
    assert classify_name(PAGE.name) == "method"
    text = PAGE.read_text(encoding="utf-8")
    assert not scan_cabin(text)
    assert "seventh" in text.lower() or "not a seventh" in text.lower()
    assert "Survive-the-Night" in text
    assert "not a watt-hour" in text
    assert "NL-A1" in text
    assert "Appendix A" in text
    assert "FOR_A_LAB_V1.md" in text
    assert "other suite" in text
    assert "hostile reviewer" in text
    assert "CONOPS, power" in text
    assert "single lunar day of ~348 hours" in text
    assert "280 hour payload operations window" in text
    assert "Survive the Night (Future TO CP-32)" in text
    assert "no night operations supported in the threshold mission" in text
    assert "80NSSC24M0001" in text
    assert "$50 million" in text
    assert "Do not mint W" in text
    assert "Do not letter" in text
    assert "Cataldo" in text


def test_issue_template_starts_reconstruction_without_a_letter() -> None:
    assert ISSUE.is_file()
    text = ISSUE.read_text(encoding="utf-8")
    assert not scan_cabin(text)
    assert "named_box" in text
    assert "Night hours (darkness)" in text
    assert "Average night electrical load W" in text
    assert "Survive-the-Night" in text
    assert "PO_SCOPE_V1.md" in text
    assert "FOR_A_LAB_V1.md" in text
    assert "hostile reviewer" in text

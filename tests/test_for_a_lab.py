"""Lab job page: win the grant / beat the other suite — method, not cabin."""
from __future__ import annotations

from pathlib import Path

from night_line.ship_gate import classify_name, scan_cabin, scan_offer_body

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "FOR_A_LAB_V1.md"
README = ROOT / "README.md"
SPEC = ROOT / "NIGHT_LINE_SPEC_V1.md"


def test_for_a_lab_is_method_not_cabin_not_offer() -> None:
    assert PAGE.is_file()
    assert classify_name(PAGE.name) == "method"
    text = PAGE.read_text(encoding="utf-8")
    assert not scan_cabin(text)
    assert not scan_offer_body(text)
    assert "seventh energy line" in text
    assert "other suite" in text
    assert "hostile reviewer" in text
    assert "Appendix A" in text
    assert "Survive-the-Night" in text
    assert "watt-hour" in text
    assert "Faster" in text
    assert "More precise" in text
    assert "More reliable" in text
    assert "win the grant" in text.lower() or "You win the grant" in text
    assert "PO_SCOPE_V1.md" in text
    assert "Do not letter" in text
    assert "MEASURED=false" in text
    assert "Thermal Desktop" in text


def test_readme_leads_with_the_lab_job() -> None:
    text = README.read_text(encoding="utf-8")
    assert not scan_cabin(text)
    assert text.index("other suite") < text.index("git clone")
    assert "FOR_A_LAB_V1.md" in text
    assert "hostile reviewer" in text
    assert "Win the grant" in text


def test_spec_names_the_pi_job() -> None:
    text = SPEC.read_text(encoding="utf-8")
    assert not scan_cabin(text)
    assert "What a PI uses this for" in text
    assert "FOR_A_LAB_V1.md" in text
    assert "Survive-the-Night" in text

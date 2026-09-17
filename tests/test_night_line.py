"""Published Night Line numbers. Stdlib-only package; no kitchen imports."""
from __future__ import annotations

import ast
from pathlib import Path

from night_line.cli import run_one
from night_line.model import ROOT, evaluate, load_box, packaged_boxes, public_label

PKG = Path(__file__).resolve().parents[1] / "night_line"
OUT = Path(__file__).resolve().parents[1] / "out"


def test_no_kitchen_imports() -> None:
    for p in PKG.rglob("*.py"):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("dogfood_platform")
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith("dogfood_platform")
        text = p.read_text(encoding="utf-8")
        assert "dogfood_platform" not in text


def test_no_kitchen_keys_in_boxes() -> None:
    bad = ("dual", "leftover", "yard", "garage", "product_works", "starship")
    for path in packaged_boxes():
        import json

        raw = json.loads(path.read_text(encoding="utf-8"))

        def walk(o: object) -> None:
            if isinstance(o, dict):
                for k, v in o.items():
                    lk = str(k).lower()
                    for b in bad:
                        assert b not in lk, f"{path.name} key {k}"
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(raw)


def test_public_labels() -> None:
    disagree = public_label(
        [
            {"verdict": "LIVE", "margin_Wh": 204.23},
            {"verdict": "DIE", "margin_Wh": -20.0},
        ],
        store_Wh=640.0,
    )
    assert disagree["label"] == "BRACKET"
    assert disagree["edge"] is False
    all_live_edge = public_label(
        [
            {"verdict": "LIVE", "margin_Wh": 5.76},
            {"verdict": "LIVE", "margin_Wh": 204.23},
        ],
        store_Wh=640.0,
    )
    assert all_live_edge["label"] == "LIVE"
    assert all_live_edge["edge"] is True
    all_die = public_label(
        [
            {"verdict": "DIE", "margin_Wh": -10.0},
            {"verdict": "DIE", "margin_Wh": -80.0},
        ],
        store_Wh=640.0,
    )
    assert all_die["label"] == "DIE"
    iff = public_label(
        [{"verdict": "LIVE", "margin_Wh": 5.76}],
        store_Wh=640.0,
        open_upward_knob="P_NIGHT",
    )
    assert iff["label"] == "LIVE_IF_P_NIGHT_BELOW"
    assert iff["edge"] is False


def test_lems_a3_published_line() -> None:
    rec = evaluate(load_box(PKG / "boxes" / "lems_a3.json"))
    hi = rec["hi"]
    assert rec["label"] == "LIVE"
    assert rec["edge"] is True
    assert rec["label_display"] == "LIVE (edge)"
    assert abs(float(hi["E_night_Wh"]) - 634.24) < 0.01
    assert abs(float(hi["hours_lived"]) - 357.22) < 0.01
    assert abs(float(hi["margin_Wh"]) - 5.76) < 0.05
    assert abs(float(rec["worst_corner_margin_Wh"]) - 5.76) < 0.05
    brk = {b["knob"]: b for b in rec["breaks"]}
    assert abs(float(brk["A_rad_m2"]["value"]) - 0.828) < 0.001
    assert abs(float(brk["G_path_W_per_K"]["value"]) - 0.00607) < 5e-5
    assert abs(float(brk["P_electronics_W"]["value"]) - 1.808) < 0.001
    for b in rec["breaks"]:
        assert abs(float(b["hours"]) - 354.0) < 0.01
    assert hi["P_elec_W"] == max(hi["P_electronics_W"], hi["P_leak_W"])
    if hi.get("P_cond_integral_check_W") is not None:
        assert abs(float(hi["P_cond_integral_check_W"]) - float(hi["P_cond_W"])) < 1e-6
    written = run_one(PKG / "boxes" / "lems_a3.json", OUT)
    text = (OUT / "lems_a3" / "LINE.md").read_text(encoding="utf-8")
    assert "LIVE (edge)" in text
    assert "634.24 Wh" in text
    assert "357.22 h" in text
    assert "+5.76 Wh" in text
    assert "0.828 m²" in text or "0.828 m2" in text
    receipt = (OUT / "lems_a3" / "RECEIPT.txt").read_text(encoding="utf-8")
    assert "LIVE (edge)" in receipt
    assert written["verify"]["ok"] is True
    assert written["verify"]["ladder_recompute_ok"] is True


def test_lusee_night_published_ladder() -> None:
    rec = evaluate(load_box(PKG / "boxes" / "lusee_night.json"))
    assert rec["label"] == "LIVE_IF_P_NIGHT_BELOW"
    assert rec["edge"] is False
    by = {r["rung"]: float(r["P_W"]) for r in rec["ladder"]}
    assert abs(by["nameplate"] - 21.83) < 0.01
    assert abs(by["usable"] - 15.28) < 0.01
    assert abs(by["derated_discharge"] - 14.52) < 0.01
    assert abs(by["derated"] - 13.20) < 0.01
    assert abs(float(rec["p_night_threshold_W"]) - 13.20) < 0.01
    assert abs(float(rec["p_night_threshold_soc8_W"]) - 17.34) < 0.01
    written = run_one(PKG / "boxes" / "lusee_night.json", OUT)
    text = (OUT / "lusee_night" / "LINE.md").read_text(encoding="utf-8")
    assert "LIVE_IF_P_NIGHT_BELOW" in text
    assert "13.20" in text
    assert "14.52" in text
    assert "21.83" in text
    assert "15.28" in text
    assert "17.34" in text
    assert written["verify"]["ok"] is True
    assert written["verify"]["independent_ladder"]["derated"]
    assert abs(written["verify"]["independent_ladder"]["derated"] - 13.20) < 0.01
    assert abs(written["verify"]["independent_ladder"]["soc8"] - 17.34) < 0.01

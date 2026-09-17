"""Published Night Line numbers. Stdlib-only package; no kitchen imports."""
from __future__ import annotations

import ast
from pathlib import Path

from night_line.cli import run_one
from night_line.model import (
    BONUS_DURATION_LINE,
    IDENTITY_DURATION_LINE,
    IDENTITY_HEAT_LINE,
    IDENTITY_LINE,
    IDENTITY_STORE_LINE,
    CLAIM_VS_WITNESS,
    HEAT_VS_BONUS,
    LINE_OPEN_TWO_KNOBS,
    LIVE_IF_STORE_ABOVE,
    ROOT,
    evaluate,
    identity_hibernation_table,
    identity_store_table,
    load_box,
    packaged_boxes,
    public_label,
)

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
    two = public_label([], two_knobs_open=True)
    assert two["label"] == LINE_OPEN_TWO_KNOBS
    assert two["edge"] is False
    assert two["worst_corner_margin_Wh"] is None
    store_open = public_label([], store_open_load_printed=True)
    assert store_open["label"] == LIVE_IF_STORE_ABOVE
    assert store_open["edge"] is False
    assert store_open["worst_corner_margin_Wh"] is None
    claim = public_label([], claim_vs_witness=True)
    assert claim["label"] == CLAIM_VS_WITNESS
    assert claim["edge"] is False
    assert claim["worst_corner_margin_Wh"] is None
    heat = public_label([], heat_vs_bonus=True)
    assert heat["label"] == HEAT_VS_BONUS
    assert heat["edge"] is False
    assert heat["worst_corner_margin_Wh"] is None


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


LEMS_MARK = {
    640.0,
    1.231,
    0.297,
    1.528,
    541.0,
    0.0028,
    -28.0,
    98.6,
    37.99,
    5.92,
    245.15,
    73.15,
    0.8,
    0.006,
    0.05,
}
LUSEE_MARK = {7160.0, 12.4, 0.15, 128.0, 50.0, 328.0, 8218.54}
FLIP_MARK = {480.0, 30.0, 5420.0, 320.0, 450.0, 110.0}
FSS_MARK = {1770.0, 19.0}


def _walk_nums(obj: object, out: list[float]) -> None:
    if isinstance(obj, bool) or obj is None:
        return
    if isinstance(obj, (int, float)):
        out.append(float(obj))
        return
    if isinstance(obj, str):
        return
    if isinstance(obj, dict):
        for v in obj.values():
            _walk_nums(v, out)
        return
    if isinstance(obj, (list, tuple)):
        for v in obj:
            _walk_nums(v, out)


def test_flip_griffin1_identity_table() -> None:
    rec = evaluate(load_box(PKG / "boxes" / "flip_griffin1.json"))
    fix = load_box(PKG / "boxes" / "flip_griffin1.json")
    nums: list[float] = []
    _walk_nums(fix, nums)
    for n in nums:
        for bad in LEMS_MARK | LUSEE_MARK:
            assert abs(n - bad) > 1e-12, f"{bad} leaked into FLIP box"
    assert rec["label"] == LINE_OPEN_TWO_KNOBS
    assert rec["label_display"] == LINE_OPEN_TWO_KNOBS
    assert rec["identity"] == IDENTITY_LINE
    table = rec["identity_table"]
    expected = (1.98, 3.95, 9.89, 19.77)
    assert len(table) == 4
    for row, p_w in zip(table, expected):
        assert abs(float(row["max_avg_hibernation_load_W"]) - p_w) < 0.01
        assert "ASSUMED" in row["reserve_label"]
    rows = identity_hibernation_table(h_night=354.0)
    assert abs(float(rows[0]["max_avg_hibernation_load_W"]) - 700.0 / 354.0) < 0.01
    written = run_one(PKG / "boxes" / "flip_griffin1.json", OUT)
    text = (OUT / "flip_griffin1" / "LINE.md").read_text(encoding="utf-8")
    assert LINE_OPEN_TWO_KNOBS in text
    assert "no store is chosen" in text
    assert "ASSUMED" in text
    for p_w in expected:
        assert f"{p_w:.2f}" in text
    for line in text.splitlines():
        if line.startswith("|") and any(x in line for x in ("1.98", "3.95", "9.89", "19.77")):
            assert "ASSUMED" in line
    assert written["verify"]["ok"] is True
    assert written["verify"]["ladder_recompute_ok"] is True


def test_fss_store_open_nameplate() -> None:
    rec = evaluate(load_box(PKG / "boxes" / "fss.json"))
    fix = load_box(PKG / "boxes" / "fss.json")
    nums: list[float] = []
    _walk_nums(fix, nums)
    for n in nums:
        for bad in LEMS_MARK | LUSEE_MARK | FLIP_MARK:
            assert abs(n - bad) > 1e-12, f"{bad} leaked into FSS box"
    assert rec["label"] == LIVE_IF_STORE_ABOVE
    assert rec["label_display"] == LIVE_IF_STORE_ABOVE
    assert rec["identity"] == IDENTITY_STORE_LINE
    assert abs(float(rec["nameplate_line_Wh"]) - 1770.0) < 0.5
    table = rec["identity_table"]
    assert abs(float(table[0]["nameplate_line_Wh"]) - 1770.0) < 0.5
    assert table[0]["reserve_label"].startswith("OPEN")
    assert "ASSUMED" in table[1]["reserve_label"]
    assert abs(float(table[1]["usable_Wh"]) - 1770.0) < 0.5
    assert abs(float(table[1]["nameplate_line_Wh"]) - (1770.0 / 0.70)) < 0.5
    rows = identity_store_table(p_load=5.0, h_night=354.0)
    assert abs(float(rows[0]["nameplate_line_Wh"]) - 1770.0) < 0.5
    assert rows[0]["identity"] == IDENTITY_STORE_LINE
    written = run_one(PKG / "boxes" / "fss.json", OUT)
    text = (OUT / "fss" / "LINE.md").read_text(encoding="utf-8")
    assert LIVE_IF_STORE_ABOVE in text
    assert "1770" in text
    assert "ASSUMED" in text
    assert "2528.57" in text
    for line in text.splitlines():
        if "2528.57" in line:
            assert "ASSUMED" in line
    assert written["verify"]["ok"] is True
    assert written["verify"]["ladder_recompute_ok"] is True


def test_bgm1_claim_vs_witness() -> None:
    rec = evaluate(load_box(PKG / "boxes" / "bgm1_flown.json"))
    fix = load_box(PKG / "boxes" / "bgm1_flown.json")
    nums: list[float] = []
    _walk_nums(fix, nums)
    for n in nums:
        for bad in LEMS_MARK | LUSEE_MARK | FLIP_MARK | FSS_MARK:
            assert abs(n - bad) > 1e-12, f"{bad} leaked into BGM1 box"
    rec_nums: list[float] = []
    _walk_nums(rec, rec_nums)
    for n in rec_nums:
        for bad in LEMS_MARK | LUSEE_MARK | FLIP_MARK | FSS_MARK:
            assert abs(n - bad) > 1e-12, f"{bad} leaked into BGM1 rec"
    assert 400.0 * 354.0 not in rec_nums

    def walk_keys(o: object) -> None:
        if isinstance(o, dict):
            for k, v in o.items():
                assert "leftover" not in str(k).lower(), k
                walk_keys(v)
        elif isinstance(o, list):
            for v in o:
                walk_keys(v)

    walk_keys(rec)
    walk_keys(fix)
    assert rec["label"] == CLAIM_VS_WITNESS
    assert rec["label_display"] == CLAIM_VS_WITNESS
    assert rec["identity"] == IDENTITY_DURATION_LINE
    assert rec["after_sunset_h"] == 5.0
    assert rec["energy_wh"] is None
    assert rec["store_Wh"] is None
    assert rec.get("E_night_Wh") is None
    assert rec.get("leftover_Wh") is None
    assert rec.get("leftover") is None
    assert abs(float(rec["duration_gap_h"]) - 349.0) < 1e-12
    assert rec["peak_vs_night_keepalive"] == "OPEN"
    assert rec["product_surface_ops"] == "Lunar day + night"
    assert rec["payload_power_quote"] == "> 400 W"
    assert rec["witness"] == "flown"
    assert rec["H_night_h"] is None
    written = run_one(PKG / "boxes" / "bgm1_flown.json", OUT)
    text = (OUT / "bgm1" / "LINE.md").read_text(encoding="utf-8")
    assert CLAIM_VS_WITNESS in text
    assert "5 h" in text
    assert "349" in text
    assert "Lunar day + night" in text
    assert "> 400 W" in text
    assert "Not a DIE" in text
    assert "leftover" not in text.lower()
    assert "LuSEE" not in text
    assert "LEMS" not in text
    assert "Farside Seismic" not in text
    assert written["verify"]["ok"] is True
    assert written["verify"]["ladder_recompute_ok"] is True


def test_zeno_cs8_heat_vs_bonus() -> None:
    rec = evaluate(load_box(PKG / "boxes" / "zeno_cs8.json"))
    fix = load_box(PKG / "boxes" / "zeno_cs8.json")
    nums: list[float] = []
    _walk_nums(fix, nums)
    for n in nums:
        for bad in LEMS_MARK | LUSEE_MARK | FLIP_MARK | FSS_MARK:
            assert abs(n - bad) > 1e-12, f"{bad} leaked into Zeno box"
        assert abs(n - 400.0) > 1e-12, "400 W bus leaked into Zeno box"
        assert abs(n - 1770.0) > 1e-12, "5 Wt x 354 electrical mint leaked into Zeno box"
    rec_nums: list[float] = []
    _walk_nums(rec, rec_nums)
    for n in rec_nums:
        for bad in LEMS_MARK | LUSEE_MARK | FLIP_MARK | FSS_MARK:
            assert abs(n - bad) > 1e-12, f"{bad} leaked into Zeno rec"
        assert abs(n - 400.0) > 1e-12
        assert abs(n - 1770.0) > 1e-12
    assert 5.0 * 354.0 not in rec_nums
    assert rec["label"] == HEAT_VS_BONUS
    assert rec["identity"] == IDENTITY_HEAT_LINE
    assert BONUS_DURATION_LINE in rec["bonus_duration_line"]
    assert rec["P_thermal_W"] == 5.0
    assert rec["P_thermal_kind"] == "heat"
    assert rec["P_thermal_W"] != 400.0
    assert rec["payload_power_W"] is None
    assert rec["P_keepalive_W"] is None
    assert rec["store_Wh"] is None
    assert rec["after_sunset_h"] is None
    assert rec["after_sunset_h"] != 5.0
    assert "after_sunset_h" not in (fix.get("fields") or {})
    assert rec.get("E_night_Wh") is None
    assert rec.get("nameplate_line_Wh") is None
    assert rec.get("leftover") is None
    assert rec.get("leftover_Wh") is None
    assert rec["H_night_h"] is None
    assert rec["witness"] == "pending"
    assert "2028" in str(rec["launch_NET"])
    written = run_one(PKG / "boxes" / "zeno_cs8.json", OUT)
    text = (OUT / "zeno_cs8" / "LINE.md").read_text(encoding="utf-8")
    assert HEAT_VS_BONUS in text
    assert "5 Wt" in text
    assert "heat" in text.lower()
    assert "leftover" not in text.lower()
    assert written["verify"]["ok"] is True
    assert written["verify"]["ladder_recompute_ok"] is True

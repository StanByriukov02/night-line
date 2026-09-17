"""Witness map: named box on named host, not a seventh energy line."""
from __future__ import annotations

from pathlib import Path

from night_line.model import packaged_boxes
from night_line.ship_gate import classify_name, scan_cabin
from night_line.verify import independent_ride_label, verify_ride
from night_line.witness_map import evaluate_map, load_ride, packaged_rides

ROOT = Path(__file__).resolve().parents[1]
MAP_PAGE = ROOT / "WITNESS_MAP_V1.md"


def _by_id():
    return {r["ride_id"]: r for r in evaluate_map()["rows"]}


def test_not_a_seventh_energy_box() -> None:
    assert len(packaged_boxes()) == 6
    assert len(packaged_rides()) == 14
    doc = evaluate_map()
    assert doc["manifest_closed"] is False
    assert doc["n_packaged_energy_boxes"] == 6
    assert all(r["adds_energy_box"] is False for r in doc["rows"])


def test_vertex_is_day_only() -> None:
    row = _by_id()["vertex_im3"]
    assert row["label"] == "DAY_ONLY_PRINTED"
    assert row["full_night_possible"] == "no"
    txt = (ROOT / "sources" / "im3-vertex" / "lpsc-2025-1233" / "page.txt").read_text(
        encoding="utf-8"
    )
    assert "no night operations or survival" in txt
    apl = (ROOT / "sources" / "im3-vertex" / "apl-lunar-vertex" / "page.txt").read_text(
        encoding="utf-8"
    )
    assert "One lunar daylight period" in apl
    assert "conclude near sunset" in apl


def test_bgm2_lander_and_lusee_are_two_rows() -> None:
    by = _by_id()
    lander = by["bgm2_lander"]
    payload = by["lusee_night"]
    assert lander["label"] == "LANDER_OFF_BEFORE_NIGHT"
    assert lander["full_night_possible"] == "no"
    assert payload["label"] == "PAYLOAD_NIGHT_LANDER_OFF"
    assert payload["full_night_possible"] == "pending"
    assert lander["host"] != payload["named_box"]
    html = (ROOT / "sources" / "lusee-night" / "firefly-bgm2" / "page.txt").read_text(
        encoding="utf-8"
    )
    assert "power off prior to lunar nightfall" in html
    arx = (ROOT / "sources" / "lusee-night" / "arxiv-2407-07173" / "page.txt").read_text(
        encoding="utf-8"
    )
    assert "permanently shut down at the end of the first solar day" in arx


def test_griffin_lander_and_flip_are_two_rows() -> None:
    by = _by_id()
    lander = by["griffin1_lander"]
    rover = by["flip_griffin1"]
    assert lander["label"] == "LANDER_NIGHT_NOT_IN_PUG"
    assert lander["full_night_possible"] == "no"
    assert rover["label"] == "NIGHT_CLAIMED_STORE_OPEN"
    assert rover["full_night_possible"] == "pending"
    html = (
        ROOT / "sources" / "flip-griffin1" / "astrolab-flip-rover" / "page.html"
    ).read_text(encoding="utf-8")
    assert "store enough energy to survive the lunar night" in html


def test_mk1_does_not_invent_watts() -> None:
    row = _by_id()["mk1"]
    assert row["label"] == "SURFACE_STAY_NIGHT_W_OPEN"
    assert row["full_night_possible"] == "unverified"
    assert row["store_Wh_printed"] is False
    assert row["window"] == "year_unverified"
    txt = (ROOT / "sources" / "mk1" / "lunarsurface-2024-5028" / "page.txt").read_text(
        encoding="utf-8"
    )
    assert "three metric tons" in txt
    assert "Payload User" in txt
    assert "night keep-alive" not in txt.lower()


def test_flown_short_and_out_of_window_and_host_dead() -> None:
    by = _by_id()
    assert by["bgm1"]["label"] == "NIGHT_WITNESS_FLOWN_SHORT"
    assert by["bgm1"]["full_night_possible"] == "no"
    assert by["zeno_cs8"]["label"] == "OUT_OF_WINDOW"
    assert by["fss_cp12"]["label"] == "HOST_TERMINATED"


def test_verifier_recomputes_every_row() -> None:
    by = _by_id()
    for path in packaged_rides():
        fix = load_ride(path)
        rec = by[str(fix["ride_id"])]
        assert rec["label"] == independent_ride_label(fix["cited"])
        report = verify_ride(fix, rec, root=ROOT)
        assert report["ok"] is True, (fix["ride_id"], report)


def test_method_page_is_method_not_cabin() -> None:
    assert MAP_PAGE.is_file()
    assert classify_name(MAP_PAGE.name) == "method"
    text = MAP_PAGE.read_text(encoding="utf-8")
    assert not scan_cabin(text)
    assert "MANIFEST_CLOSED=false" in text
    assert "seventh energy line" in text
    assert "night-line witness-map" in text


def test_inherit_forbidden_pairs() -> None:
    doc = evaluate_map()
    pairs = {(p["host_ride_id"], p["payload_ride_id"]): p for p in doc["inherit_forbidden"]}
    g = pairs[("griffin1_lander", "flip_griffin1")]
    assert g["allowed"] is False
    assert "not a Griffin night-store" in g["why"]
    b = pairs[("bgm2_lander", "lusee_night")]
    assert b["allowed"] is False
    assert "not a Blue Ghost night-store" in b["why"]
    m = pairs[("griffin1_lander", "metal_flip")]
    assert m["allowed"] is False
    assert "METAL" in m["why"]
    passive = pairs[("flip_griffin1", "lra_flip")]
    assert passive["allowed"] is False
    assert "no power" in passive["why"]


def test_flip_wh_still_open_after_venturi_pages() -> None:
    bat = (ROOT / "sources" / "flip-griffin1" / "venturi-space-batteries" / "page.txt").read_text(
        encoding="utf-8"
    )
    intro = (
        ROOT / "sources" / "flip-griffin1" / "venturi-space-flip-intro" / "page.txt"
    ).read_text(encoding="utf-8")
    assert "10,000" in bat or "10000" in bat.replace(",", "")
    assert "180 hours of nights" in intro
    row = _by_id()["flip_griffin1"]
    assert row["store_Wh_printed"] is False
    assert row["label"] == "NIGHT_CLAIMED_STORE_OPEN"


def test_gsfc_lra_is_passive_no_power() -> None:
    row = _by_id()["lra_flip"]
    assert row["label"] == "PASSIVE_NO_POWER"
    assert row["full_night_possible"] == "n/a"
    html = (
        ROOT / "sources" / "flip-nasa-guests" / "astrolab-nasa-payloads-20260518" / "page.html"
    ).read_text(encoding="utf-8")
    assert "no power" in html
    assert "maintenance" in html
    assert "Laser Retroreflector Array" in html


def test_nasa_center_guests_wait_on_flip_not_griffin() -> None:
    by = _by_id()
    for ride_id in ("metal_flip", "ldes_flip", "lidar_flip"):
        row = by[ride_id]
        assert row["label"] == "GUEST_ON_OPEN_HOST"
        assert row["full_night_possible"] == "pending"
        assert row["store_Wh_printed"] is False
        assert "FLIP" in row["host"]
    html = (
        ROOT / "sources" / "flip-nasa-guests" / "astrolab-nasa-payloads-20260518" / "page.html"
    ).read_text(encoding="utf-8")
    assert "Interlune" in html
    assert "Moon Exploration for Titanium with Active Lighting" in html
    assert "radiator cooling" in html
    assert "Lunar LiDAR Demonstration" in html
    assert "Marshall" in html


def test_ucf_lunar_vise_is_day_only_2028() -> None:
    row = _by_id()["lunar_vise_cp21"]
    assert row["label"] == "DAY_ONLY_PRINTED"
    assert row["full_night_possible"] == "no"
    assert row["window"] == "2028+"
    ucf = (ROOT / "sources" / "lunar-vise" / "ucf-lunarvise" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "10-day science investigation" in ucf
    lpsc = (ROOT / "sources" / "lunar-vise" / "lpsc-2025-1750" / "page.txt").read_text(
        encoding="utf-8"
    )
    assert "one lunar day" in lpsc
    assert "2028" in lpsc
    assert "CP-21" in lpsc
    nasa = (ROOT / "sources" / "lunar-vise" / "nasa-cp21" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "Donaldson-Hanna" in nasa
    assert "University of Central Florida" in nasa
    assert "Blue Ghost 3" in nasa

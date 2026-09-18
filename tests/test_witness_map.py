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
    assert len(packaged_rides()) == 28
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
    assert "Project ended" in text
    assert "survive multiple lunar nights" in text
    assert "SLIM" in text
    assert "three lunar nights" in text
    assert "Awaiting their awakening" in text
    assert "one lunar daylight period" in text
    assert "5 RHUs" in text
    assert "lack of solar power" in text
    assert "lunar night survival" in text
    assert "night survivability" in text
    assert "640 Wh" in text
    assert "150 hours" in text
    assert "not only survive, but to operate" in text
    assert "200 Wh" in text
    assert "4 hrs" in text
    assert "60-hour" in text
    assert "propulsion system malfunction" in text


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
    csa = pairs[("moonranger_cs6", "csa_lrm_cs6")]
    assert csa["allowed"] is False
    assert "not MoonRanger cancelled" in csa["why"]
    rhu = pairs[("slim_jaxa", "yutu2_ce4")]
    assert rhu["allowed"] is False
    assert "not Yutu-2" in rhu["why"]
    zeno_rhu = pairs[("zeno_cs8", "yutu2_ce4")]
    assert zeno_rhu["allowed"] is False
    assert "not bus watts" in zeno_rhu["why"]
    flip_lupex = pairs[("flip_griffin1", "lupex_rover")]
    assert flip_lupex["allowed"] is False
    assert "not LUPEX" in flip_lupex["why"]
    zeno_lupex = pairs[("zeno_cs8", "lupex_rover")]
    assert zeno_lupex["allowed"] is False
    assert "not LUPEX" in zeno_lupex["why"]
    heat_tech = pairs[("yutu2_ce4", "lupex_rover")]
    assert heat_tech["allowed"] is False
    assert "not LUPEX" in heat_tech["why"]
    rhu_lems = pairs[("yutu2_ce4", "lems_a3")]
    assert rhu_lems["allowed"] is False
    assert "not that store" in rhu_lems["why"]
    zeno_lems = pairs[("zeno_cs8", "lems_a3")]
    assert zeno_lems["allowed"] is False
    assert "640 Wh" in zeno_lems["why"]
    flip_flex = pairs[("flip_griffin1", "flex_ltv")]
    assert flip_flex["allowed"] is False
    assert "150 hours" in flip_flex["why"]
    flip_dawn = pairs[("flip_griffin1", "lunar_dawn_ltv")]
    assert flip_dawn["allowed"] is False
    assert "operate-through-night" in flip_dawn["why"]
    flex_dawn = pairs[("flex_ltv", "lunar_dawn_ltv")]
    assert flex_dawn["allowed"] is False
    assert "not Lunar Dawn" in flex_dawn["why"]
    lems_flex = pairs[("lems_a3", "flex_ltv")]
    assert lems_flex["allowed"] is False
    assert "not FLEX" in lems_flex["why"]
    lems_dawn = pairs[("lems_a3", "lunar_dawn_ltv")]
    assert lems_dawn["allowed"] is False
    assert "not Lunar Dawn" in lems_dawn["why"]
    mr_flex = pairs[("moonranger_cs6", "flex_ltv")]
    assert mr_flex["allowed"] is False
    assert "4 h" in mr_flex["why"]
    iris_mr = pairs[("iris_peregrine", "moonranger_cs6")]
    assert iris_mr["allowed"] is False
    assert "never reached the Moon" in iris_mr["why"]
    iris_prag = pairs[("iris_peregrine", "pragyan_ch3")]
    assert iris_prag["allowed"] is False
    assert "never landed" in iris_prag["why"]


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


def test_moonranger_short_dark_store_is_not_lunar_night() -> None:
    row = _by_id()["moonranger_cs6"]
    assert row["label"] == "SHORT_DARK_STORE_NOT_NIGHT"
    assert row["full_night_possible"] == "no"
    assert row["window"] == "2029+"
    assert row["store_Wh_printed"] is True
    iac = (ROOT / "sources" / "moonranger-cs6" / "iac-22-c3-4-8" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "200 Wh" in iac
    assert "4 hrs of dark survival" in iac
    nasa = (ROOT / "sources" / "moonranger-cs6" / "nasa-cs6" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "permanently shadowed regions" in nasa
    assert "MoonRanger" in nasa
    fire = (
        ROOT / "sources" / "moonranger-cs6" / "firefly-bgm4" / "page.html"
    ).read_text(encoding="utf-8")
    assert "more than 12 days on the lunar surface" in fire
    assert "2029" in fire
    cmu = (
        ROOT / "sources" / "moonranger-cs6" / "cmu-2025-08" / "page.html"
    ).read_text(encoding="utf-8")
    assert "2029 mission to the moon" in cmu
    assert "Carnegie Mellon" in cmu
    assert _by_id()["flex_ltv"]["label"] == "POLAR_DARKNESS_H_STORE_OPEN"
    assert _by_id()["flex_ltv"]["label"] != row["label"]
    assert _by_id()["lems_a3"]["label"] == "ELECTRICAL_STORE_CITED"
    assert _by_id()["lems_a3"]["label"] != row["label"]


def test_iris_never_landed_is_not_a_night() -> None:
    row = _by_id()["iris_peregrine"]
    assert row["label"] == "HOST_NEVER_LANDED"
    assert row["full_night_possible"] == "no"
    assert row["store_Wh_printed"] is False
    assert row["window"] == "flown_no_landing"
    cmu = (ROOT / "sources" / "iris-peregrine" / "cmu-2023-03" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "60-hour mission" in cmu
    ri = (ROOT / "sources" / "iris-peregrine" / "ri-iris" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "propulsion system malfunction" in ri
    assert _by_id()["pragyan_ch3"]["label"] == "HOPED_WAKE_NOT_STORE"
    assert _by_id()["pragyan_ch3"]["label"] != row["label"]
    assert _by_id()["slim_jaxa"]["label"] == "FLOWN_WOKE_NOT_DESIGNED"
    assert _by_id()["slim_jaxa"]["label"] != row["label"]
    assert _by_id()["moonranger_cs6"]["label"] != row["label"]


def test_esa_prospect_day_watts_are_not_night() -> None:
    row = _by_id()["prospect_cp22"]
    assert row["label"] == "DAY_W_PRINTED_NIGHT_NO"
    assert row["full_night_possible"] == "no"
    assert row["store_Wh_printed"] is False
    esa = (ROOT / "sources" / "prospect-cp22" / "esa-prospect" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "not planned to survive through the night" in esa
    assert "5 and 10 Earth days" in esa
    fr = (
        ROOT / "sources" / "prospect-cp22" / "frontiers-2024" / "page.html"
    ).read_text(encoding="utf-8")
    assert "85.6" in fr
    assert "Peak power" in fr


def test_leia_and_cp21_day_labs() -> None:
    leia = _by_id()["leia_cp22"]
    assert leia["label"] == "DAY_ONLY_PRINTED"
    html = (ROOT / "sources" / "leia-cp22" / "nasa-leia" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "10 Earth days" in html
    nmls = _by_id()["nmls_cp21"]
    assert nmls["label"] == "DAY_ONLY_PRINTED"
    heim = _by_id()["heimdall_cp21"]
    assert heim["label"] == "DAY_ONLY_PRINTED"
    fire = (
        ROOT / "sources" / "cp21-day-guests" / "firefly-bgm3" / "page.html"
    ).read_text(encoding="utf-8")
    assert "University of Alabama in Huntsville" in fire
    assert "more than 14 days on the lunar surface" in fire
    assert "Heimdall" in fire


def test_csa_lrm_ended_is_not_host_dead() -> None:
    row = _by_id()["csa_lrm_cs6"]
    assert row["label"] == "PROGRAM_ENDED_HOST_STILL_LISTS"
    assert row["full_night_possible"] == "no"
    assert row["store_Wh_printed"] is False
    assert row["window"] == "program_ended"
    rover = (
        ROOT / "sources" / "csa-lrm-cs6" / "csa-rover-ended" / "page.html"
    ).read_text(encoding="utf-8")
    assert "Project ended" in rover
    assert "Status" in rover
    dp = (
        ROOT / "sources" / "csa-lrm-cs6" / "csa-dp-2026-2027" / "page.html"
    ).read_text(encoding="utf-8")
    assert "Terminate work on the" in dp
    assert "Lunar Rover Mission" in dp
    assert "LRM" in dp
    fire = (
        ROOT / "sources" / "csa-lrm-cs6" / "firefly-bgm4" / "page.html"
    ).read_text(encoding="utf-8")
    assert "survive multiple lunar nights" in fire
    assert "14 Earth days" in fire
    moon = _by_id()["moonranger_cs6"]
    assert moon["label"] == "SHORT_DARK_STORE_NOT_NIGHT"
    assert moon["label"] != row["label"]


def test_slim_woke_is_not_a_designed_night() -> None:
    row = _by_id()["slim_jaxa"]
    assert row["label"] == "FLOWN_WOKE_NOT_DESIGNED"
    assert row["full_night_possible"] == "no"
    assert row["store_Wh_printed"] is False
    assert row["window"] == "flown"
    assert _by_id()["bgm1"]["label"] == "NIGHT_WITNESS_FLOWN_SHORT"
    assert _by_id()["bgm1"]["label"] != row["label"]
    press = (
        ROOT / "sources" / "slim-jaxa" / "jaxa-press-20240826" / "page.html"
    ).read_text(encoding="utf-8")
    assert "survive three lunar nights" in press
    assert "not being part of the original mission plan" in press
    cosmos = (
        ROOT / "sources" / "slim-jaxa" / "isas-cosmos-slim" / "page.html"
    ).read_text(encoding="utf-8")
    assert "not been expected to continue past dark" in cosmos
    assert "SLIM did wake" in cosmos
    briefing = (
        ROOT / "sources" / "slim-jaxa" / "jaxa-briefing-20241226" / "page.txt"
    ).read_text(encoding="utf-8")
    assert "設計上想定していなかった" in briefing
    assert "3回の越夜" in briefing


def test_pragyan_hoped_wake_is_not_a_night_store() -> None:
    row = _by_id()["pragyan_ch3"]
    assert row["label"] == "HOPED_WAKE_NOT_STORE"
    assert row["full_night_possible"] == "no"
    assert row["store_Wh_printed"] is False
    assert row["window"] == "flown"
    assert _by_id()["slim_jaxa"]["label"] == "FLOWN_WOKE_NOT_DESIGNED"
    assert _by_id()["slim_jaxa"]["label"] != row["label"]
    assert _by_id()["lunar_vise_cp21"]["label"] == "DAY_ONLY_PRINTED"
    assert _by_id()["lunar_vise_cp21"]["label"] != row["label"]
    isro = (ROOT / "sources" / "pragyan-ch3" / "isro-ch3" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "sleep mode" in isro
    assert "Awaiting their awakening" in isro
    pib = (ROOT / "sources" / "pragyan-ch3" / "pib-daylight" / "page.txt").read_text(
        encoding="utf-8"
    )
    assert "one lunar daylight period" in pib
    assert "14 Earth days" in pib
    data = (
        ROOT / "sources" / "pragyan-ch3" / "isro-data-release" / "page.html"
    ).read_text(encoding="utf-8")
    assert "101m" in data


def test_yutu2_flown_rhu_heat_is_not_a_night_store() -> None:
    row = _by_id()["yutu2_ce4"]
    assert row["label"] == "FLOWN_RHU_HEAT_NOT_STORE"
    assert row["full_night_possible"] == "n/a"
    assert row["store_Wh_printed"] is False
    assert row["window"] == "flown"
    assert _by_id()["slim_jaxa"]["label"] == "FLOWN_WOKE_NOT_DESIGNED"
    assert _by_id()["slim_jaxa"]["label"] != row["label"]
    assert _by_id()["pragyan_ch3"]["label"] == "HOPED_WAKE_NOT_STORE"
    assert _by_id()["pragyan_ch3"]["label"] != row["label"]
    assert _by_id()["zeno_cs8"]["label"] == "OUT_OF_WINDOW"
    assert _by_id()["zeno_cs8"]["label"] != row["label"]
    rhu = (ROOT / "sources" / "yutu2-ce4" / "cnsa-rhu" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "5 RHUs" in rhu
    assert "survival and power supply during the moonlight" in rhu
    wake = (
        ROOT / "sources" / "yutu2-ce4" / "cnsa-first-wake" / "page.html"
    ).read_text(encoding="utf-8")
    assert "surviving their first lunar night" in wake
    assert "lack of solar power" in wake
    clep = (ROOT / "sources" / "yutu2-ce4" / "clep-night" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "接通供热装置" in clep
    assert "十三次月昼月夜" in clep


def test_lupex_night_survival_tech_is_not_a_store() -> None:
    row = _by_id()["lupex_rover"]
    assert row["label"] == "NIGHT_SURVIVAL_TECH_STORE_OPEN"
    assert row["full_night_possible"] == "pending"
    assert row["store_Wh_printed"] is False
    assert row["window"] == "2028+"
    assert _by_id()["flip_griffin1"]["label"] == "NIGHT_CLAIMED_STORE_OPEN"
    assert _by_id()["flip_griffin1"]["label"] != row["label"]
    assert _by_id()["zeno_cs8"]["label"] == "OUT_OF_WINDOW"
    assert _by_id()["zeno_cs8"]["label"] != row["label"]
    assert _by_id()["yutu2_ce4"]["label"] == "FLOWN_RHU_HEAT_NOT_STORE"
    assert _by_id()["yutu2_ce4"]["label"] != row["label"]
    jaxa = (ROOT / "sources" / "lupex-rover" / "jaxa-lupex" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "lunar night survival" in jaxa
    assert "More than 3 months" in jaxa
    assert "No earlier than 2028" in jaxa
    mhi = (ROOT / "sources" / "lupex-rover" / "mhi-lupex" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "night survivability" in mhi
    assert "3.5 months after landing" in mhi


def test_lems_electrical_store_is_not_rhu_heat() -> None:
    row = _by_id()["lems_a3"]
    assert row["label"] == "ELECTRICAL_STORE_CITED"
    assert row["full_night_possible"] == "pending"
    assert row["store_Wh_printed"] is True
    assert _by_id()["yutu2_ce4"]["label"] == "FLOWN_RHU_HEAT_NOT_STORE"
    assert _by_id()["yutu2_ce4"]["label"] != row["label"]
    assert _by_id()["zeno_cs8"]["label"] == "OUT_OF_WINDOW"
    assert _by_id()["zeno_cs8"]["label"] != row["label"]
    assert _by_id()["lusee_night"]["label"] == "PAYLOAD_NIGHT_LANDER_OFF"
    assert _by_id()["lusee_night"]["label"] != row["label"]
    ices = (ROOT / "sources" / "lems-a3" / "ices-2025-tcs-ntrs" / "page.txt").read_text(
        encoding="utf-8"
    )
    assert "640 Wh" in ices
    assert "354 hr" in ices
    gsfc = (ROOT / "sources" / "lems-a3" / "gsfc-lems-a3" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "continuous (day and night)" in gsfc
    nasa = (ROOT / "sources" / "lems-a3" / "nasa-science-lems" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "day and night" in nasa


def test_flex_150h_is_not_cataldo_and_not_flip() -> None:
    row = _by_id()["flex_ltv"]
    assert row["label"] == "POLAR_DARKNESS_H_STORE_OPEN"
    assert row["full_night_possible"] == "pending"
    assert row["store_Wh_printed"] is False
    assert _by_id()["flip_griffin1"]["label"] == "NIGHT_CLAIMED_STORE_OPEN"
    assert _by_id()["flip_griffin1"]["label"] != row["label"]
    assert _by_id()["lems_a3"]["label"] == "ELECTRICAL_STORE_CITED"
    assert _by_id()["lems_a3"]["label"] != row["label"]
    html = (ROOT / "sources" / "flex-ltv" / "siemens-flex" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "survive solely on battery storage" in html
    assert "five days in darkness" in html
    assert "150 hours" in html


def test_lunar_dawn_operate_is_not_hibernate() -> None:
    row = _by_id()["lunar_dawn_ltv"]
    assert row["label"] == "OPERATE_THROUGH_NIGHT_STORE_OPEN"
    assert row["full_night_possible"] == "pending"
    assert row["store_Wh_printed"] is False
    assert _by_id()["flip_griffin1"]["label"] == "NIGHT_CLAIMED_STORE_OPEN"
    assert _by_id()["flip_griffin1"]["label"] != row["label"]
    assert _by_id()["flex_ltv"]["label"] == "POLAR_DARKNESS_H_STORE_OPEN"
    assert _by_id()["flex_ltv"]["label"] != row["label"]
    assert _by_id()["yutu2_ce4"]["label"] == "FLOWN_RHU_HEAT_NOT_STORE"
    assert _by_id()["yutu2_ce4"]["label"] != row["label"]
    lockheed = (
        ROOT / "sources" / "lunar-dawn-ltv" / "lockheed-ltvs" / "page.html"
    ).read_text(encoding="utf-8")
    assert "not only survive, but to operate" in lockheed
    assert "two-week long lunar nights" in lockheed
    gm = (ROOT / "sources" / "lunar-dawn-ltv" / "gm-battery" / "page.html").read_text(
        encoding="utf-8"
    )
    assert "14-day long lunar night" in gm
    assert "survive in total darkness" in gm


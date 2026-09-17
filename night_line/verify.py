"""Verifier: sha256 of saved sources, recorded URL status, independent ladder recompute."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from night_line.nist import k_integral_w_m

SIGMA_W_M2_K4 = 5.670374419e-8
TEXT_SUFFIXES = {".txt", ".html", ".htm", ".md", ".csv", ".json", ".xml"}


def canonical_bytes(path: Path) -> bytes:
    """Hash text as LF so Windows CRLF and Linux checkout agree."""
    raw = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return raw


def _sha256(path: Path) -> str:
    return hashlib.sha256(canonical_bytes(path)).hexdigest()


def refresh_source_hashes(root: Path) -> int:
    """Rewrite sha256_by_file to canonical LF hashes. Returns files changed."""
    sources = root / "sources"
    if not sources.is_dir():
        return 0
    n = 0
    for srcp in sorted(sources.rglob("SOURCE.json")):
        rec = json.loads(srcp.read_text(encoding="utf-8"))
        by = dict(rec.get("sha256_by_file") or rec.get("saved_sha256") or {})
        changed = False
        for f in sorted(srcp.parent.iterdir(), key=lambda p: p.name.lower()):
            if not f.is_file() or f.name == "SOURCE.json":
                continue
            digest = _sha256(f)
            if by.get(f.name) != digest:
                by[f.name] = digest
                changed = True
            if rec.get("filename") == f.name and rec.get("sha256") != digest:
                rec["sha256"] = digest
                changed = True
        rec["sha256_by_file"] = by
        rec["hash_newline"] = "lf"
        if changed:
            srcp.write_text(
                json.dumps(rec, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            n += 1
    return n


def _source_hashes(folder: Path) -> dict[str, Any]:
    srcp = folder / "SOURCE.json"
    rec = json.loads(srcp.read_text(encoding="utf-8"))
    by = rec.get("sha256_by_file") or rec.get("saved_sha256") or {}
    mismatches: list[str] = []
    checked: list[dict[str, str]] = []
    for f in sorted(folder.iterdir()):
        if f.name == "SOURCE.json" or not f.is_file():
            continue
        digest = _sha256(f)
        expected = by.get(f.name)
        checked.append({"file": f.name, "sha256": digest})
        if expected and expected != digest:
            mismatches.append(f"{folder.name}/{f.name}")
    primary = rec.get("filename")
    if primary and (folder / str(primary)).is_file():
        got = _sha256(folder / str(primary))
        if rec.get("sha256") and rec["sha256"] != got:
            mismatches.append(f"{folder.name} primary sha256")
    status = rec.get("status_20260917")
    urls: list[dict[str, Any]] = []
    url_list = [rec[k] for k in ("url", "html_url", "file_url") if rec.get(k)]
    if isinstance(status, dict):
        for u in url_list:
            urls.append(
                {
                    "url": u,
                    "status": status.get(u),
                    "live": status.get(u) == 200,
                    "checked_date": "2026-09-17",
                }
            )
    elif url_list:
        urls.append(
            {
                "url": url_list[0],
                "status": status,
                "live": status == 200,
                "checked_date": "2026-09-17",
            }
        )
    omitted = rec.get("omitted_binaries") or []
    return {
        "slug": folder.name,
        "ok": not mismatches,
        "mismatches": mismatches,
        "files": checked,
        "url_status": urls,
        "omitted_binaries": omitted,
        "primary_sha256": rec.get("sha256"),
        "primary_url": rec.get("url"),
    }


def independent_ladder(
    *,
    store_Wh: float,
    night_hours: float,
    reserve_soc: float,
    eta_discharge: float,
    load_unc: float,
    floor_soc: float,
) -> dict[str, float]:
    """Recompute ladder rungs from printed inputs. Does not import model.py arithmetic."""
    nameplate = float(store_Wh) / float(night_hours)
    usable = float(store_Wh) * (1.0 - float(reserve_soc)) / float(night_hours)
    derated_discharge = usable * float(eta_discharge)
    derated = derated_discharge / (1.0 + float(load_unc))
    floor_usable = float(store_Wh) * (1.0 - float(floor_soc)) / float(night_hours)
    floor_derated = floor_usable * float(eta_discharge) / (1.0 + float(load_unc))
    return {
        "nameplate": nameplate,
        "usable": usable,
        "derated_discharge": derated_discharge,
        "derated": derated,
        "soc8": floor_derated,
    }


def independent_corner(
    *,
    G: float,
    eps: float,
    A_rad: float,
    T_box: float,
    T_env: float,
    p_electronics: float,
    store_Wh: float,
    h_night: float,
) -> dict[str, float]:
    p_cond = float(G) * (float(T_box) - float(T_env))
    p_rad = (
        float(eps)
        * SIGMA_W_M2_K4
        * float(A_rad)
        * (float(T_box) ** 4 - float(T_env) ** 4)
    )
    p_leak = p_cond + p_rad
    p_elec = max(float(p_electronics), p_leak)
    e = p_elec * float(h_night)
    return {
        "P_cond_W": p_cond,
        "P_rad_W": p_rad,
        "P_leak_W": p_leak,
        "P_elec_W": p_elec,
        "E_night_Wh": e,
        "hours_lived": float(store_Wh) / p_elec,
        "margin_Wh": float(store_Wh) - e,
    }


def independent_ride_label(cited: dict[str, Any]) -> str:
    """Recompute a witness-map label from cited flags. Does not import witness_map."""
    if cited.get("host_terminated"):
        return "HOST_TERMINATED"
    if cited.get("flown_after_sunset_h") is not None:
        return "NIGHT_WITNESS_FLOWN_SHORT"
    if cited.get("day_W_printed") and cited.get("night_refused"):
        return "DAY_W_PRINTED_NIGHT_NO"
    if cited.get("daylight_only"):
        return "DAY_ONLY_PRINTED"
    if cited.get("psr_in_host_day"):
        return "PSR_IN_HOST_DAY"
    if cited.get("out_of_window"):
        return "OUT_OF_WINDOW"
    if cited.get("lander_off_before_night") and cited.get(
        "payload_continues_after_lander_off"
    ):
        return "PAYLOAD_NIGHT_LANDER_OFF"
    if cited.get("lander_off_before_night"):
        return "LANDER_OFF_BEFORE_NIGHT"
    if cited.get("no_power"):
        return "PASSIVE_NO_POWER"
    if cited.get("guest_on_open_host"):
        return "GUEST_ON_OPEN_HOST"
    if cited.get("survive_night_claim") and not cited.get("store_Wh_printed"):
        return "NIGHT_CLAIMED_STORE_OPEN"
    if cited.get("pug_thermal_excludes_night") and not cited.get("survive_night_claim"):
        return "LANDER_NIGHT_NOT_IN_PUG"
    if cited.get("surface_stay_claim") and not cited.get("night_W_printed"):
        return "SURFACE_STAY_NIGHT_W_OPEN"
    raise ValueError("unclassified ride")


def independent_full_night_possible(label: str) -> str:
    no = {
        "HOST_TERMINATED",
        "OUT_OF_WINDOW",
        "NIGHT_WITNESS_FLOWN_SHORT",
        "DAY_ONLY_PRINTED",
        "DAY_W_PRINTED_NIGHT_NO",
        "PSR_IN_HOST_DAY",
        "LANDER_OFF_BEFORE_NIGHT",
        "LANDER_NIGHT_NOT_IN_PUG",
    }
    if label in no:
        return "no"
    if label == "PASSIVE_NO_POWER":
        return "n/a"
    if label in {
        "NIGHT_CLAIMED_STORE_OPEN",
        "PAYLOAD_NIGHT_LANDER_OFF",
        "GUEST_ON_OPEN_HOST",
    }:
        return "pending"
    if label == "SURFACE_STAY_NIGHT_W_OPEN":
        return "unverified"
    raise ValueError(f"unclassified full-night: {label}")


def verify_ride(fix: dict[str, Any], rec: dict[str, Any], *, root: Path) -> dict[str, Any]:
    rel = str(fix.get("sources_dir") or "")
    sources = (root / rel) if rel else None
    hash_rows: list[dict[str, Any]] = []
    sources_ok = True
    if sources is not None and sources.is_dir():
        for folder in sorted(p for p in sources.iterdir() if p.is_dir()):
            if not (folder / "SOURCE.json").is_file():
                continue
            row = _source_hashes(folder)
            hash_rows.append(row)
            if not row["ok"]:
                sources_ok = False
    want = independent_ride_label(dict(fix.get("cited") or {}))
    label_ok = rec.get("label") == want
    night_ok = rec.get("full_night_possible") == independent_full_night_possible(want)
    closed_ok = rec.get("manifest_closed") is False
    seventh_ok = rec.get("adds_energy_box") is not True
    return {
        "sources_sha256_ok": sources_ok,
        "label_recompute_ok": label_ok,
        "full_night_recompute_ok": night_ok,
        "manifest_closed_false": closed_ok,
        "not_a_seventh_box": seventh_ok,
        "source_files": hash_rows,
        "ok": sources_ok and label_ok and night_ok and closed_ok and seventh_ok,
    }


def independent_integral_cond(
    *, nist_id: str, A_path: float, L_path: float, T_box: float, T_env: float
) -> float:
    return float(A_path) / float(L_path) * k_integral_w_m(nist_id, T_env, T_box)


def probe_url(url: str, timeout: float = 8.0) -> int | None:
    req = Request(url, method="HEAD")
    try:
        with urlopen(req, timeout=timeout) as resp:
            return int(getattr(resp, "status", 200) or 200)
    except HTTPError as e:
        return int(e.code)
    except (URLError, TimeoutError, OSError, ValueError):
        return None


def verify_box(
    fix: dict[str, Any],
    rec: dict[str, Any],
    *,
    root: Path,
    live_urls: bool = False,
) -> dict[str, Any]:
    rel = str(fix.get("sources_dir") or "")
    sources = (root / rel) if rel else None
    hash_rows: list[dict[str, Any]] = []
    url_status: list[dict[str, Any]] = []
    sources_ok = True
    if sources is not None and sources.is_dir():
        for folder in sorted(p for p in sources.iterdir() if p.is_dir()):
            if not (folder / "SOURCE.json").is_file():
                continue
            row = _source_hashes(folder)
            hash_rows.append(row)
            if not row["ok"]:
                sources_ok = False
            url_status.extend(row["url_status"])
    if live_urls:
        for u in url_status:
            code = probe_url(str(u["url"]))
            u["live_probe"] = code
            if code is not None:
                u["live"] = code == 200
                u["status"] = code

    ladder_ok = True
    fields = fix.get("fields") or {}
    soc = fields.get("SOC_min_conops_pct")
    if isinstance(soc, dict) and soc.get("value") is not None:
        indep = independent_ladder(
            store_Wh=float(rec["store_Wh"]),
            night_hours=float(rec["H_night_h"]),
            reserve_soc=float(soc["value"]) / 100.0,
            eta_discharge=float(fields["charge_discharge_eff_pct"]["value"]) / 100.0,
            load_unc=float(fields["power_load_uncertainty_margin_pct"]["value"]) / 100.0,
            floor_soc=float(fields["SOC_min_aggressive_pct"]["value"]) / 100.0,
        )
        by = {r["rung"]: float(r["P_W"]) for r in rec.get("ladder") or []}
        if abs(indep["nameplate"] - by.get("nameplate", 0.0)) > 1e-9:
            ladder_ok = False
        if abs(indep["usable"] - by.get("usable", 0.0)) > 1e-9:
            ladder_ok = False
        if abs(indep["derated"] - by.get("derated", 0.0)) > 1e-9:
            ladder_ok = False
        rec["_independent_ladder"] = indep
    else:
        indep = None

    if rec.get("label") == "HEAT_VS_BONUS":
        p_th = float(rec["P_thermal_W"])
        if abs(p_th - 5.0) > 1e-12:
            ladder_ok = False
        if rec.get("P_thermal_kind") != "heat":
            ladder_ok = False
        if rec.get("P_keepalive_W") is not None:
            ladder_ok = False
        if rec.get("store_Wh") is not None:
            ladder_ok = False
        if rec.get("after_sunset_h") is not None:
            ladder_ok = False
        if rec.get("payload_power_W") is not None:
            ladder_ok = False
        if rec.get("E_night_Wh") is not None:
            ladder_ok = False
        if rec.get("nameplate_line_Wh") is not None:
            ladder_ok = False
        if abs(p_th * 354.0 - 1770.0) < 1e-9 and rec.get("E_night_Wh") is not None:
            ladder_ok = False
        return {
            "sources_sha256_ok": sources_ok,
            "ladder_recompute_ok": ladder_ok,
            "independent_ladder": None,
            "independent_worst_corner": None,
            "url_status": url_status,
            "source_files": hash_rows,
            "open_upward_knobs": ["store_Wh", "P_keepalive_W", "H_night_h"],
            "plain_LIVE_forbidden": True,
            "ok": sources_ok and ladder_ok,
        }

    if rec.get("label") == "CLAIM_VS_WITNESS":
        after = float(rec["after_sunset_h"])
        cataldo = float(rec["cataldo_mason_night_h"])
        gap = cataldo - after
        if abs(after - 5.0) > 1e-12:
            ladder_ok = False
        if rec.get("energy_wh") is not None:
            ladder_ok = False
        if rec.get("store_Wh") is not None:
            ladder_ok = False
        if rec.get("E_night_Wh") is not None:
            ladder_ok = False
        if abs(float(rec["duration_gap_h"]) - gap) > 1e-12:
            ladder_ok = False
        if abs(gap - 349.0) > 1e-12:
            ladder_ok = False
        return {
            "sources_sha256_ok": sources_ok,
            "ladder_recompute_ok": ladder_ok,
            "independent_ladder": None,
            "independent_worst_corner": None,
            "url_status": url_status,
            "source_files": hash_rows,
            "open_upward_knobs": ["store_Wh", "energy_wh", "P_keepalive_W"],
            "plain_LIVE_forbidden": True,
            "ok": sources_ok and ladder_ok,
        }

    if rec.get("label") == "LIVE_IF_STORE_ABOVE":
        p_load = float(rec["P_keepalive_W"])
        h = float(rec["H_night_h"])
        nameplate = p_load * h
        if abs(float(rec["nameplate_line_Wh"]) - nameplate) > 1e-9:
            ladder_ok = False
        for i, row in enumerate(rec.get("identity_table") or []):
            if i == 0:
                expect = nameplate
                if "OPEN" not in str(row.get("reserve_label") or ""):
                    ladder_ok = False
            else:
                expect = nameplate / 0.70
                if "ASSUMED" not in str(row.get("reserve_label") or ""):
                    ladder_ok = False
            if abs(float(row["nameplate_line_Wh"]) - expect) > 1e-6:
                ladder_ok = False
            if abs(float(row["usable_Wh"]) - nameplate) > 1e-9:
                ladder_ok = False
        return {
            "sources_sha256_ok": sources_ok,
            "ladder_recompute_ok": ladder_ok,
            "independent_ladder": None,
            "independent_worst_corner": None,
            "url_status": url_status,
            "source_files": hash_rows,
            "open_upward_knobs": ["store_Wh"],
            "plain_LIVE_forbidden": True,
            "ok": sources_ok and ladder_ok,
        }

    if rec.get("label") == "LINE_OPEN_TWO_KNOBS":
        for row in rec.get("identity_table") or []:
            kwh = float(row["nameplate_kWh"])
            usable = kwh * 1000.0 * 0.70
            load = usable / float(rec["H_night_h"])
            if abs(float(row["usable_Wh"]) - usable) > 1e-9:
                ladder_ok = False
            if abs(float(row["max_avg_hibernation_load_W"]) - load) > 1e-9:
                ladder_ok = False
            if "ASSUMED" not in str(row.get("reserve_label") or ""):
                ladder_ok = False
        open_upward = False
        return {
            "sources_sha256_ok": sources_ok,
            "ladder_recompute_ok": ladder_ok,
            "independent_ladder": None,
            "independent_worst_corner": None,
            "url_status": url_status,
            "source_files": hash_rows,
            "open_upward_knobs": ["store_Wh", "P_keepalive_W"],
            "plain_LIVE_forbidden": True,
            "ok": sources_ok and ladder_ok,
        }

    hi = rec["hi"]
    corner = independent_corner(
        G=float(hi["G_W_per_K"]),
        eps=float(hi["eps_eff"]),
        A_rad=float(hi["A_rad_m2"]),
        T_box=float(hi["T_box_K"]),
        T_env=float(hi["T_env_K"]),
        p_electronics=float(hi["P_electronics_W"]),
        store_Wh=float(rec["store_Wh"]),
        h_night=float(rec["H_night_h"]),
    )
    if abs(corner["E_night_Wh"] - float(hi["E_night_Wh"])) > 1e-6:
        ladder_ok = False
    if hi.get("P_cond_integral_check_W") is not None:
        if abs(float(hi["P_cond_integral_check_W"]) - float(hi["P_cond_W"])) > 1e-6:
            ladder_ok = False

    open_upward = rec.get("electronics_hi_open") is True
    return {
        "sources_sha256_ok": sources_ok,
        "ladder_recompute_ok": ladder_ok,
        "independent_ladder": indep,
        "independent_worst_corner": corner,
        "url_status": url_status,
        "source_files": hash_rows,
        "open_upward_knobs": ["P_NIGHT"] if open_upward else [],
        "plain_LIVE_forbidden": open_upward,
        "ok": sources_ok and ladder_ok,
    }

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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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

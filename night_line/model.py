"""Night Line electrical + thermal model.

P_leak = P_cond + P_rad
P_elec = max(P_electronics, P_leak)
E_night = P_elec × night hours

Conduction: printed G → P_cond = G·ΔT. If A and L plus a named alloy,
P_cond = (A/L)·∫ k(T) dT over the interval actually used (NIST fit, no
extrapolation). Radiation: P_rad = e* σ A (T_box⁴ − T_env⁴).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from night_line.nist import k_integral_w_m, k_mean_w_mk, nist_cite

SIGMA_W_M2_K4 = 5.670374419e-8
EDGE_FRAC_OF_STORE = 0.02
LINE_OPEN_TWO_KNOBS = "LINE_OPEN_TWO_KNOBS"
LIVE_IF_STORE_ABOVE = "LIVE_IF_STORE_ABOVE"
CLAIM_VS_WITNESS = "CLAIM_VS_WITNESS"
HEAT_VS_BONUS = "HEAT_VS_BONUS"
ASSUMED_SOC_RESERVE_FRAC = 0.30
ASSUMED_NAMEPLATE_KWH = (1.0, 2.0, 5.0, 10.0)
IDENTITY_LINE = "usable_Wh / H_night_h = hibernation load W"
IDENTITY_STORE_LINE = "P_night_W × H_night_h = nameplate store Wh"
IDENTITY_DURATION_LINE = (
    "hours_after_sunset_flown vs 354 h Cataldo/Mason = duration gap (not Wh)"
)
IDENTITY_HEAT_LINE = "5 Wt thermal is heat, not electrical bus watts"
BONUS_DURATION_LINE = (
    "NASA CS-8 bonus = radioisotope + transmit after a full lunar night "
    "(duration claim, not Wh)"
)
CATALDO_NIGHT_H = 354.0
P_THERMAL_W = 5.0
PKG = Path(__file__).resolve().parent
BOXES = PKG / "boxes"
ROOT = PKG.parent

KITCHEN_KEYS = frozenset(
    {"leftover_Wh", "leftover", "solar_W", "delivered_W", "source_W"}
)


def _refuse(row: Any) -> None:
    if isinstance(row, dict):
        for bad in KITCHEN_KEYS:
            if bad in row:
                raise ValueError(f"refuse kitchen key {bad}")
        for v in row.values():
            _refuse(v)
    elif isinstance(row, (list, tuple)):
        for v in row:
            _refuse(v)


def load_box(path: Path | str) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        alt = BOXES / p.name
        if alt.is_file():
            p = alt
        else:
            raise FileNotFoundError(path)
    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("box file is not an object")
    _refuse(raw)
    return raw


def packaged_boxes() -> list[Path]:
    return sorted(BOXES.glob("*.json"))


def field(fix: dict[str, Any], name: str) -> dict[str, Any]:
    rec = (fix.get("fields") or {}).get(name)
    if not isinstance(rec, dict):
        raise KeyError(name)
    return rec


def field_value(fix: dict[str, Any], name: str) -> Any:
    return field(fix, name).get("value")


def p_elec_W(*, p_electronics: float, p_leak: float) -> float:
    pe = float(p_electronics)
    pl = float(p_leak)
    if pe < 0.0 or pl < 0.0:
        raise ValueError("P_electronics and P_leak must be >= 0")
    return max(pe, pl)


def p_heater_W(*, p_electronics: float, p_leak: float) -> float:
    return max(0.0, float(p_leak) - float(p_electronics))


def p_cond_from_G(*, G: float, T_box: float, T_env: float) -> float:
    return float(G) * (float(T_box) - float(T_env))


def p_cond_from_integral(
    *, nist_id: str, A_path: float, L_path: float, T_box: float, T_env: float
) -> float:
    if float(L_path) <= 0.0:
        raise ValueError("L_path must be > 0")
    return float(A_path) / float(L_path) * k_integral_w_m(nist_id, T_env, T_box)


def p_rad_W(*, eps_eff: float, A_rad: float, T_box: float, T_env: float) -> float:
    tb = float(T_box)
    te = float(T_env)
    return float(eps_eff) * SIGMA_W_M2_K4 * float(A_rad) * (tb**4 - te**4)


def hours_lived_of(*, store_Wh: float, p_total: float) -> float:
    if p_total <= 0.0:
        raise ValueError("P_elec must be > 0")
    return float(store_Wh) / float(p_total)


def corner_live(store_Wh: float, e_night: float) -> str:
    return "LIVE" if float(store_Wh) >= float(e_night) else "DIE"


def public_label(
    corners: list[dict[str, Any]],
    *,
    store_Wh: float | None = None,
    open_upward_knob: str | None = None,
    two_knobs_open: bool = False,
    store_open_load_printed: bool = False,
    claim_vs_witness: bool = False,
    heat_vs_bonus: bool = False,
) -> dict[str, Any]:
    """Label on declared corners only. LIVE_IF_<knob>_BELOW when a knob has no upper bound.

    Store and hibernation load both OPEN → LINE_OPEN_TWO_KNOBS (identity line).
    Load printed and store OPEN → LIVE_IF_STORE_ABOVE (nameplate P×H).
    Flown cited night vs public product sentence → CLAIM_VS_WITNESS (no Wh line).
    Printed thermal watts vs NASA-paid full-night bonus → HEAT_VS_BONUS (heat not bus).
    """
    if heat_vs_bonus:
        return {
            "label": HEAT_VS_BONUS,
            "edge": False,
            "worst_corner_margin_Wh": None,
        }
    if claim_vs_witness:
        return {
            "label": CLAIM_VS_WITNESS,
            "edge": False,
            "worst_corner_margin_Wh": None,
        }
    if two_knobs_open:
        return {
            "label": LINE_OPEN_TWO_KNOBS,
            "edge": False,
            "worst_corner_margin_Wh": None,
        }
    if store_open_load_printed:
        return {
            "label": LIVE_IF_STORE_ABOVE,
            "edge": False,
            "worst_corner_margin_Wh": None,
        }
    if not corners:
        raise ValueError("public_label needs declared corners")
    worst_margin = min(float(c["margin_Wh"]) for c in corners)
    if open_upward_knob:
        return {
            "label": f"LIVE_IF_{open_upward_knob}_BELOW",
            "edge": False,
            "worst_corner_margin_Wh": worst_margin,
        }
    labels = {str(c["verdict"]) for c in corners}
    live = "LIVE" in labels
    die = "DIE" in labels
    if live and die:
        verdict = "BRACKET"
    elif die and not live:
        verdict = "DIE"
    elif live and not die:
        verdict = "LIVE"
    else:
        verdict = "BRACKET" if len(labels) > 1 else next(iter(labels))
    edge = verdict == "LIVE" and worst_margin <= EDGE_FRAC_OF_STORE * float(store_Wh)
    return {
        "label": verdict,
        "edge": edge,
        "worst_corner_margin_Wh": worst_margin,
    }


def _t_env_states(fix: dict[str, Any]) -> list[dict[str, Any]]:
    spec = field(fix, "T_env_K")
    if spec.get("tier") == "OPEN":
        lo_b = spec.get("bracket_lo")
        hi_b = spec.get("bracket_hi")
        if not isinstance(lo_b, dict) or not isinstance(hi_b, dict):
            raise ValueError("T_env_K OPEN requires cited bracket_lo and bracket_hi")
        t_lo = float(lo_b["value"])
        t_hi = float(hi_b["value"])
        if t_lo >= t_hi:
            raise ValueError("T_env bracket_lo must be colder than bracket_hi")
        t_c_spec = (fix.get("fields") or {}).get("T_env_C")
        if isinstance(t_c_spec, dict) and t_c_spec.get("value") is not None:
            if abs(t_hi - (273.15 + float(t_c_spec["value"]))) > 1e-9:
                raise ValueError("T_env_K.bracket_hi must equal 273.15 + T_env_C")
        return [
            {"role": "cold", "T_env_K": t_lo, "bound": lo_b},
            {"role": "warm", "T_env_K": t_hi, "bound": hi_b},
        ]
    t = spec.get("value")
    if t is None:
        raise ValueError("T_env_K missing value and not OPEN")
    t_env = float(t)
    t_c_spec = (fix.get("fields") or {}).get("T_env_C")
    if (
        isinstance(t_c_spec, dict)
        and t_c_spec.get("value") is not None
        and spec.get("derived_from") == "T_env_C"
    ):
        if abs(t_env - (273.15 + float(t_c_spec["value"]))) > 1e-9:
            raise ValueError("T_env_K must equal 273.15 + T_env_C")
    return [{"role": "cited", "T_env_K": t_env, "bound": spec}]


def store_load_both_open(fix: dict[str, Any]) -> bool:
    """True when usable store and hibernation load are both unprinted."""
    st = field(fix, "store_Wh")
    pk = field(fix, "P_keepalive_W")
    return (
        st.get("tier") == "OPEN"
        and st.get("value") is None
        and pk.get("tier") == "OPEN"
        and pk.get("value") is None
    )


def store_open_load_printed(fix: dict[str, Any]) -> bool:
    """True when hibernation load is printed and usable store is not."""
    st = field(fix, "store_Wh")
    pk = field(fix, "P_keepalive_W")
    return (
        st.get("tier") == "OPEN"
        and st.get("value") is None
        and pk.get("value") is not None
    )


def claim_vs_witness_of(fix: dict[str, Any]) -> bool:
    return str(fix.get("label_family") or "") == CLAIM_VS_WITNESS


def heat_vs_bonus_of(fix: dict[str, Any]) -> bool:
    return str(fix.get("label_family") or "") == HEAT_VS_BONUS


def identity_hibernation_table(
    *,
    h_night: float,
    reserve_frac: float = ASSUMED_SOC_RESERVE_FRAC,
    nameplates_kWh: tuple[float, ...] = ASSUMED_NAMEPLATE_KWH,
) -> list[dict[str, Any]]:
    """ASSUMED 30% reserve on example nameplates. Not a picked store."""
    h = float(h_night)
    if h <= 0.0:
        raise ValueError("H_night must be > 0")
    rows: list[dict[str, Any]] = []
    for kwh in nameplates_kWh:
        nameplate_Wh = float(kwh) * 1000.0
        usable_Wh = nameplate_Wh * (1.0 - float(reserve_frac))
        rows.append(
            {
                "nameplate_kWh": float(kwh),
                "nameplate_Wh": nameplate_Wh,
                "reserve_frac": float(reserve_frac),
                "reserve_label": "ASSUMED 30% nameplate reserve — not printed for this box",
                "usable_Wh": usable_Wh,
                "max_avg_hibernation_load_W": usable_Wh / h,
                "identity": IDENTITY_LINE,
            }
        )
    return rows


def identity_store_table(
    *,
    p_load: float,
    h_night: float,
    reserve_frac: float = ASSUMED_SOC_RESERVE_FRAC,
) -> list[dict[str, Any]]:
    """Nameplate line from printed load. ASSUMED 30% needs a higher store. Not a picked Wh."""
    h = float(h_night)
    p = float(p_load)
    if h <= 0.0 or p < 0.0:
        raise ValueError("H_night must be > 0 and P_load >= 0")
    nameplate_Wh = p * h
    assumed_nameplate_Wh = nameplate_Wh / (1.0 - float(reserve_frac))
    return [
        {
            "reserve_frac": 0.0,
            "reserve_label": "OPEN — SOC/efficiency not printed",
            "nameplate_line_Wh": nameplate_Wh,
            "usable_Wh": nameplate_Wh,
            "identity": IDENTITY_STORE_LINE,
            "note": "nameplate = printed load × H_night",
        },
        {
            "reserve_frac": float(reserve_frac),
            "reserve_label": "ASSUMED 30% ConOps reserve — not printed for this box",
            "nameplate_line_Wh": assumed_nameplate_Wh,
            "usable_Wh": nameplate_Wh,
            "identity": IDENTITY_STORE_LINE,
            "note": "usable line is higher store",
        },
    ]


def electronics_upper_open(fix: dict[str, Any]) -> bool:
    e_br = fix.get("electronics_bracket")
    if not isinstance(e_br, dict):
        return False
    if e_br.get("hi") is not None:
        return False
    pk = (fix.get("fields") or {}).get("P_keepalive_W") or {}
    if str(e_br.get("hi_tier") or "") == "OPEN":
        return True
    return pk.get("tier") == "OPEN" and e_br.get("lo") is not None


def _usable_night_lines(
    fix: dict[str, Any], store: float, h_night: float
) -> dict[str, Any] | None:
    fields = fix.get("fields") or {}
    conops = fields.get("SOC_min_conops_pct")
    floor = fields.get("SOC_min_aggressive_pct")
    if not isinstance(conops, dict) or conops.get("value") is None:
        return None
    if not isinstance(floor, dict) or floor.get("value") is None:
        return None
    soc_c = float(conops["value"]) / 100.0
    soc_f = float(floor["value"]) / 100.0
    if not (0.0 < soc_c < 1.0 and 0.0 < soc_f < 1.0):
        raise ValueError("SOC reserves must be in (0, 100) percent")
    usable_c = float(store) * (1.0 - soc_c)
    usable_f = float(store) * (1.0 - soc_f)
    h = float(h_night)
    out: dict[str, Any] = {
        "usable_conops_Wh": usable_c,
        "usable_floor_Wh": usable_f,
        "p_conops_W": usable_c / h,
        "p_soc8_W": usable_f / h,
        "p_nameplate_W": float(store) / h,
    }
    eff = fields.get("charge_discharge_eff_pct")
    unc = fields.get("power_load_uncertainty_margin_pct")
    if isinstance(eff, dict) and eff.get("value") is not None:
        eta = float(eff["value"]) / 100.0
        if not (0.0 < eta <= 1.0):
            raise ValueError("charge/discharge efficiency must be in (0, 100] percent")
        out["eta_discharge"] = eta
        out["applied_once"] = True
        out["p_conops_eff_W"] = out["p_conops_W"] * eta
        out["p_soc8_eff_W"] = out["p_soc8_W"] * eta
    if isinstance(unc, dict) and unc.get("value") is not None:
        margin = float(unc["value"]) / 100.0
        if margin < 0.0:
            raise ValueError("load uncertainty margin must be >= 0")
        m = 1.0 + margin
        out["load_unc_mult"] = m
        base_c = float(out.get("p_conops_eff_W", out["p_conops_W"]))
        base_8 = float(out.get("p_soc8_eff_W", out["p_soc8_W"]))
        out["p_conops_line_W"] = base_c / m
        out["p_soc8_line_W"] = base_8 / m
    return out


def _cite_of(fields: dict[str, Any], *names: str) -> str:
    bits: list[str] = []
    for n in names:
        s = fields.get(n)
        if not isinstance(s, dict):
            continue
        q = str(s.get("quote") or s.get("cite") or "").strip()
        if q and q not in bits:
            bits.append(q)
    return " ".join(bits)


def _ladder_from_usable(
    fix: dict[str, Any], usable: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    fields = fix.get("fields") or {}
    conops = [
        {
            "rung": "nameplate",
            "P_W": usable["p_nameplate_W"],
            "cite": _cite_of(fields, "store_Wh", "H_night_h"),
            "note": "not survival",
        },
        {
            "rung": "usable",
            "P_W": usable["p_conops_W"],
            "cite": _cite_of(fields, "SOC_min_conops_pct"),
            "note": "30 % ConOps reserve",
        },
    ]
    soc8 = [
        {
            "rung": "soc8_floor",
            "P_W": usable["p_soc8_W"],
            "cite": _cite_of(fields, "SOC_min_aggressive_pct"),
            "note": "8 % minimum SOC",
        },
    ]
    if "p_conops_eff_W" in usable:
        eff_note = (
            "×0.95 discharge; paper prints charging and discharging 95%; "
            "applied once (start-of-night assumed nameplate)"
        )
        conops.append(
            {
                "rung": "derated_discharge",
                "P_W": usable["p_conops_eff_W"],
                "cite": _cite_of(fields, "charge_discharge_eff_pct"),
                "note": eff_note,
            }
        )
        soc8.append(
            {
                "rung": "derated_discharge",
                "P_W": usable["p_soc8_eff_W"],
                "cite": _cite_of(fields, "charge_discharge_eff_pct"),
                "note": eff_note,
            }
        )
    if "p_conops_line_W" in usable:
        conops.append(
            {
                "rung": "derated",
                "P_W": usable["p_conops_line_W"],
                "cite": _cite_of(fields, "power_load_uncertainty_margin_pct"),
                "note": "÷1.10 load uncertainty",
            }
        )
        soc8.append(
            {
                "rung": "derated",
                "P_W": usable["p_soc8_line_W"],
                "cite": _cite_of(fields, "power_load_uncertainty_margin_pct"),
                "note": "÷1.10 load uncertainty",
            }
        )
    for row in conops + soc8:
        if not str(row.get("cite") or "").strip():
            raise ValueError(f"ladder rung {row['rung']} missing cite")
    return conops, soc8


def _k_at(
    fix: dict[str, Any], t_env: float, t_box: float
) -> tuple[float, dict[str, Any]]:
    k_spec = fix.get("k_path") or {}
    nist_id = str(k_spec.get("nist_id") or "").strip()
    if k_spec.get("tier") == "OPEN" or not nist_id:
        return 1.0, {
            "k_source": "OPEN",
            "temper_match": None,
            "k_mean_w_mk": None,
            "k_integral_w_m": None,
            "cite": str(k_spec.get("cite") or "OPEN alloy — no NIST map"),
            "nist_id": None,
        }
    if k_spec.get("temper_match") is not True:
        raise ValueError("cited k_path must declare temper_match true")
    k_mean = k_mean_w_mk(nist_id, t_env, t_box)
    integ = k_integral_w_m(nist_id, t_env, t_box)
    meta = nist_cite(nist_id)
    nist = {
        "k_source": "cited",
        "temper_match": True,
        "k_mean_w_mk": k_mean,
        "k_integral_w_m": integ,
        "nist_id": nist_id,
        "cite": (
            f"NIST {meta['name']} {meta['prop']} {meta['cite_url']} "
            f"rev={meta['rev'] if meta['rev'] is not None else 'as published on the cited page'}"
        ),
        **meta,
    }
    return k_mean, nist


def _state(
    *,
    G: float,
    eps: float,
    A_rad: float,
    k_path: float,
    L_path: float,
    T_box: float,
    T_env: float,
    p_electronics: float,
    store_Wh: float,
    h_night: float,
    nist_id: str | None,
) -> dict[str, Any]:
    p_c = p_cond_from_G(G=G, T_box=T_box, T_env=T_env)
    p_r = p_rad_W(eps_eff=eps, A_rad=A_rad, T_box=T_box, T_env=T_env)
    p_leak = p_c + p_r
    p_e = p_elec_W(p_electronics=p_electronics, p_leak=p_leak)
    if p_e <= 0.0:
        raise ValueError("P_elec must be > 0")
    e = p_e * float(h_night)
    hours = hours_lived_of(store_Wh=store_Wh, p_total=p_e)
    A_path = float(G) * float(L_path) / float(k_path) if k_path else None
    rec = {
        "P_cond_W": p_c,
        "P_rad_W": p_r,
        "P_leak_W": p_leak,
        "P_electronics_W": float(p_electronics),
        "P_heater_implied_W": p_heater_W(p_electronics=p_electronics, p_leak=p_leak),
        "P_elec_W": p_e,
        "E_night_Wh": e,
        "hours_lived": hours,
        "H_night_h": float(h_night),
        "margin_Wh": float(store_Wh) - float(e),
        "verdict": corner_live(store_Wh, e),
        "A_path_m2": A_path,
        "L_path_m": float(L_path),
        "k_path_w_mk": float(k_path),
    }
    if nist_id:
        rec["P_cond_integral_check_W"] = p_cond_from_integral(
            nist_id=nist_id,
            A_path=float(A_path),
            L_path=L_path,
            T_box=T_box,
            T_env=T_env,
        )
    _refuse(rec)
    return rec


def _hours_at(
    *,
    G: float,
    eps: float,
    A_rad: float,
    p_electronics: float,
    k_path: float,
    L_path: float,
    T_box: float,
    T_env: float,
    store_Wh: float,
    h_night: float,
) -> float:
    st = _state(
        G=G,
        eps=eps,
        A_rad=A_rad,
        k_path=k_path,
        L_path=L_path,
        T_box=T_box,
        T_env=T_env,
        p_electronics=p_electronics,
        store_Wh=store_Wh,
        h_night=h_night,
        nist_id=None,
    )
    return float(st["hours_lived"])


def _breaks(
    *,
    hi: dict[str, Any],
    store: float,
    h_night: float,
    k_path: float,
    L_path: float,
    T_box: float,
    T_env: float,
    p_electronics: float,
    G_hi: float,
    eps_hi: float,
    A_hi: float,
) -> list[dict[str, Any]]:
    p_budget = float(store) / float(h_night)
    dT = float(T_box) - float(T_env)
    dT4 = float(T_box) ** 4 - float(T_env) ** 4
    p_cond_hi = float(hi["P_cond_W"])
    p_rad_hi = float(hi["P_rad_W"])
    c_rad = float(eps_hi) * SIGMA_W_M2_K4 * dT4
    a_flip = None if c_rad <= 0.0 else (p_budget - p_cond_hi) / c_rad
    g_flip = None if dT <= 0.0 else (p_budget - p_rad_hi) / dT
    pe_flip = p_budget
    rows: list[dict[str, Any]] = []

    def pack(knob: str, value: float | None, unit: str, hours: float | None, held: str) -> None:
        rows.append(
            {
                "knob": knob,
                "value": value,
                "unit": unit,
                "hours": hours,
                "held": held,
            }
        )

    hours_a = None
    if a_flip is not None and a_flip > 0.0:
        hours_a = _hours_at(
            G=G_hi,
            eps=eps_hi,
            A_rad=a_flip,
            p_electronics=p_electronics,
            k_path=k_path,
            L_path=L_path,
            T_box=T_box,
            T_env=T_env,
            store_Wh=store,
            h_night=h_night,
        )
    pack(
        "A_rad_m2",
        a_flip,
        "m2",
        hours_a,
        "G, e*, P_electronics, T held at the worst declared corner",
    )
    hours_g = None
    if g_flip is not None and g_flip > 0.0:
        hours_g = _hours_at(
            G=g_flip,
            eps=eps_hi,
            A_rad=A_hi,
            p_electronics=p_electronics,
            k_path=k_path,
            L_path=L_path,
            T_box=T_box,
            T_env=T_env,
            store_Wh=store,
            h_night=h_night,
        )
    pack(
        "G_path_W_per_K",
        g_flip,
        "W/K",
        hours_g,
        "A_rad, e*, P_electronics, T held at the worst declared corner",
    )
    hours_pe = _hours_at(
        G=G_hi,
        eps=eps_hi,
        A_rad=A_hi,
        p_electronics=pe_flip,
        k_path=k_path,
        L_path=L_path,
        T_box=T_box,
        T_env=T_env,
        store_Wh=store,
        h_night=h_night,
    )
    pack(
        "P_electronics_W",
        pe_flip,
        "W",
        hours_pe,
        "G, A_rad, e*, T held; P_elec = max(P_electronics, P_leak)",
    )
    return rows


def evaluate(fix: dict[str, Any]) -> dict[str, Any]:
    if heat_vs_bonus_of(fix):
        thermal = field(fix, "P_thermal_W")
        p_th = float(thermal["value"])
        if abs(p_th - P_THERMAL_W) > 1e-12:
            raise ValueError("P_thermal_W must stay the cited 5 Wt")
        kind = str(thermal.get("kind") or "heat")
        if kind not in {"heat", "thermal", "RHU"}:
            raise ValueError("P_thermal_W kind must be heat")
        pk = field(fix, "P_keepalive_W")
        if pk.get("value") is not None:
            raise ValueError("REFUSE electrical keep-alive filled")
        store = field(fix, "store_Wh")
        if store.get("value") is not None:
            raise ValueError("REFUSE store_Wh filled")
        fields = fix.get("fields") or {}
        if "payload_power_W" in fields:
            raise ValueError("REFUSE 400 W bus field on this box")
        if "after_sunset_h" in fields:
            after = fields["after_sunset_h"].get("value") if isinstance(fields["after_sunset_h"], dict) else None
            if after is not None:
                raise ValueError("REFUSE after_sunset_h on this box")
        cataldo = float(field(fix, "cataldo_mason_night_h")["value"])
        if abs(cataldo - CATALDO_NIGHT_H) > 1e-12:
            raise ValueError("Cataldo/Mason night hours must stay 354")
        if field(fix, "H_night_h").get("value") is not None:
            raise ValueError("REFUSE H_night_h filled — bonus hours not printed")
        net = str(field(fix, "launch_NET").get("value") or "")
        if "2028" not in net:
            raise ValueError("NET must stay as printed (2028)")
        lab = public_label([], heat_vs_bonus=True)
        identity = (
            f"{IDENTITY_HEAT_LINE}. {BONUS_DURATION_LINE}. "
            f"Do not compute {p_th:g} Wt × {cataldo:g} h as electrical watt-hours."
        )
        rec: dict[str, Any] = {
            "schema": "night_line_record_v1",
            "box": fix.get("name"),
            "box_id": fix.get("box_id"),
            "mission": fix.get("mission"),
            "label": lab["label"],
            "label_display": lab["label"],
            "edge": False,
            "worst_corner_margin_Wh": None,
            "store_Wh": None,
            "energy_wh": None,
            "P_keepalive_W": None,
            "P_thermal_W": p_th,
            "P_thermal_kind": "heat",
            "P_thermal_unit": str(thermal.get("unit") or "Wt"),
            "payload_power_W": None,
            "after_sunset_h": None,
            "peak_vs_night_keepalive": "OPEN",
            "launch_NET": net,
            "cataldo_mason_night_h": cataldo,
            "H_night_h": None,
            "bonus_hours_printed": False,
            "identity": IDENTITY_HEAT_LINE,
            "identity_line": identity,
            "bonus_duration_line": BONUS_DURATION_LINE,
            "live_if_electrical": (
                "LIVE_IF a printed electrical keep-alive W is covered through a "
                "printed full-night duration by a printed store — not 5 Wt × 354 h."
            ),
            "T_box_K": None,
            "T_env_K": None,
            "P_electronics_W": None,
            "electronics_hi_open": False,
            "p_night_threshold_W": None,
            "p_night_threshold_soc8_W": None,
            "ladder": [],
            "ladder_soc8": [],
            "lo": None,
            "hi": None,
            "corners": [],
            "breaks": [],
            "electrical_model": {
                "P_elec": IDENTITY_HEAT_LINE,
                "reason": (
                    "5 Wt is RHU heat. Electrical keep-alive OPEN. Store OPEN. "
                    "NASA CS-8 bonus is radioisotope + transmit after a full lunar night "
                    "(duration). Do not treat 5 Wt as P_keepalive. Do not mint watt-hours "
                    "from 5 Wt × 354 h."
                ),
                "cite": str(fix.get("electrical_model") or IDENTITY_HEAT_LINE),
            },
            "heat_quotes": {
                "thermal": str(thermal.get("quote") or ""),
                "rhu": str((fields.get("rhu_heat") or {}).get("quote") or ""),
            },
            "bonus_quotes": {
                "cs8": str((fields.get("cs8_bonus") or {}).get("quote") or ""),
                "night_ops": str((fields.get("night_ops") or {}).get("quote") or ""),
            },
            "witness": "pending",
            "witness_expected": "pending",
            "sources_dir": fix.get("sources_dir"),
        }
        if rec.get("E_night_Wh") is not None:
            raise ValueError("REFUSE watt-hours computed from heat")
        if rec.get("nameplate_line_Wh") is not None:
            raise ValueError("REFUSE nameplate from 5 Wt")
        _refuse(rec)
        return rec
    if claim_vs_witness_of(fix):
        energy_spec = field(fix, "energy_wh")
        store_spec = field(fix, "store_Wh")
        pk = field(fix, "P_keepalive_W")
        if energy_spec.get("value") is not None:
            raise ValueError("REFUSE energy_wh filled")
        if store_spec.get("value") is not None:
            raise ValueError("REFUSE store_Wh filled")
        if pk.get("value") is not None:
            raise ValueError("REFUSE P_keepalive_W filled")
        after = float(field(fix, "after_sunset_h")["value"])
        cataldo = float(field(fix, "cataldo_mason_night_h")["value"])
        if abs(cataldo - CATALDO_NIGHT_H) > 1e-12:
            raise ValueError("Cataldo/Mason night hours must stay 354")
        duration_gap_h = cataldo - after
        power_spec = field(fix, "payload_power_W")
        product_ops = str(field(fix, "product_surface_ops").get("value") or "")
        lab = public_label([], claim_vs_witness=True)
        identity = (
            f"{IDENTITY_DURATION_LINE} "
            f"({after:g} h flown vs {cataldo:g} h = {duration_gap_h:g} h gap)."
        )
        rec: dict[str, Any] = {
            "schema": "night_line_record_v1",
            "box": fix.get("name"),
            "box_id": fix.get("box_id"),
            "mission": fix.get("mission"),
            "label": lab["label"],
            "label_display": lab["label"],
            "edge": False,
            "worst_corner_margin_Wh": None,
            "store_Wh": None,
            "energy_wh": None,
            "P_keepalive_W": None,
            "payload_power_W": float(power_spec["value"]),
            "payload_power_quote": str(power_spec.get("quote") or ""),
            "peak_vs_night_keepalive": "OPEN",
            "product_surface_ops": product_ops,
            "product_claim_prints_354_h": False,
            "after_sunset_h": after,
            "designed_for_night": False,
            "woke_after_night": False,
            "cataldo_mason_night_h": cataldo,
            "H_night_h": None,
            "duration_gap_h": duration_gap_h,
            "identity": IDENTITY_DURATION_LINE,
            "identity_line": identity,
            "T_box_K": None,
            "T_env_K": None,
            "P_electronics_W": None,
            "electronics_hi_open": False,
            "p_night_threshold_W": None,
            "p_night_threshold_soc8_W": None,
            "ladder": [],
            "ladder_soc8": [],
            "lo": None,
            "hi": None,
            "corners": [],
            "breaks": [],
            "electrical_model": {
                "P_elec": IDENTITY_DURATION_LINE,
                "reason": (
                    "Flown hours vs Cataldo/Mason darkness. Store OPEN. "
                    "Do not invent watt-hours. Do not print DIE on invented Wh. "
                    "Do not run Fourier leak."
                ),
                "cite": str(fix.get("electrical_model") or IDENTITY_DURATION_LINE),
            },
            "product_quotes": {
                "surface_ops": product_ops,
                "power": str(power_spec.get("quote") or ""),
            },
            "flown_quotes": {
                "after_sunset": str(field(fix, "after_sunset_h").get("quote") or ""),
                "not_designed": str(field(fix, "designed_for_night").get("quote") or ""),
                "batteries": str(field(fix, "woke_after_night").get("quote") or ""),
            },
            "witness": "flown",
            "witness_id": str(fix.get("witness_id") or ""),
            "witness_expected": "flown",
            "sources_dir": fix.get("sources_dir"),
        }
        if rec.get("E_night_Wh") is not None:
            raise ValueError("REFUSE watt-hours computed")
        _refuse(rec)
        return rec
    h_night = float(field_value(fix, "H_night_h"))
    if store_load_both_open(fix):
        table = identity_hibernation_table(h_night=h_night)
        lab = public_label([], two_knobs_open=True)
        t_env_spec = field(fix, "T_env_K")
        t_env_states = _t_env_states(fix)
        rec: dict[str, Any] = {
            "schema": "night_line_record_v1",
            "box": fix.get("name"),
            "box_id": fix.get("box_id"),
            "mission": fix.get("mission"),
            "label": lab["label"],
            "label_display": lab["label"],
            "edge": False,
            "worst_corner_margin_Wh": None,
            "store_Wh": None,
            "P_keepalive_W": None,
            "T_box_K": None,
            "T_env_K": max(float(s["T_env_K"]) for s in t_env_states),
            "T_env": {
                "tier": t_env_spec.get("tier"),
                "states": [
                    {
                        "role": s["role"],
                        "T_env_K": s["T_env_K"],
                        "cite": (s["bound"] or {}).get("cite"),
                    }
                    for s in t_env_states
                ],
            },
            "H_night_h": h_night,
            "identity": IDENTITY_LINE,
            "identity_line": (
                f"{IDENTITY_LINE} ({h_night:g} h). "
                "Both store Wh and hibernation load W are OPEN. Do not pick a store."
            ),
            "identity_table": table,
            "assumed_reserve_frac": ASSUMED_SOC_RESERVE_FRAC,
            "assumed_reserve_label": "ASSUMED — not printed for this box",
            "P_electronics_W": None,
            "P_electronics_tier": "OPEN",
            "electronics_hi_open": False,
            "p_night_threshold_W": None,
            "p_night_threshold_soc8_W": None,
            "ladder": [],
            "ladder_soc8": [],
            "lo": None,
            "hi": None,
            "corners": [],
            "breaks": [],
            "electrical_model": {
                "P_elec": IDENTITY_LINE,
                "reason": (
                    "Store and load both OPEN. Identity: usable_Wh / night hours "
                    "= hibernation load W. Do not run Fourier leak without printed "
                    "geometry and load. Do not pick a store."
                ),
                "cite": str(fix.get("electrical_model") or IDENTITY_LINE),
            },
            "witness": "first sunset after landing",
            "witness_expected": fix.get("witness_expected")
            or "first sunset after landing",
            "sources_dir": fix.get("sources_dir"),
        }
        _refuse(rec)
        return rec
    if store_open_load_printed(fix):
        pk = field(fix, "P_keepalive_W")
        p_load = float(pk["value"])
        nameplate_Wh = p_load * h_night
        table = identity_store_table(p_load=p_load, h_night=h_night)
        lab = public_label([], store_open_load_printed=True)
        t_env_spec = field(fix, "T_env_K")
        rec = {
            "schema": "night_line_record_v1",
            "box": fix.get("name"),
            "box_id": fix.get("box_id"),
            "mission": fix.get("mission"),
            "label": lab["label"],
            "label_display": lab["label"],
            "edge": False,
            "worst_corner_margin_Wh": None,
            "store_Wh": None,
            "P_keepalive_W": p_load,
            "T_box_K": None,
            "T_env_K": None,
            "T_env": {
                "tier": t_env_spec.get("tier"),
                "states": [],
                "cite": t_env_spec.get("cite"),
                "printed_site": (fix.get("fields") or {})
                .get("landing_site_name", {})
                .get("value"),
            },
            "H_night_h": h_night,
            "identity": IDENTITY_STORE_LINE,
            "identity_line": (
                f"{IDENTITY_STORE_LINE} ({p_load:g} W × {h_night:g} h = {nameplate_Wh:g} Wh). "
                "Store Wh OPEN. Reserve OPEN. Do not convert battery kg to Wh."
            ),
            "identity_table": table,
            "nameplate_line_Wh": nameplate_Wh,
            "reserve_tier": "OPEN",
            "assumed_reserve_frac": ASSUMED_SOC_RESERVE_FRAC,
            "assumed_reserve_label": "ASSUMED — not printed for this box",
            "P_electronics_W": p_load,
            "P_electronics_tier": str(pk.get("tier") or "cited_public"),
            "electronics_hi_open": False,
            "p_night_threshold_W": None,
            "p_night_threshold_soc8_W": None,
            "ladder": [],
            "ladder_soc8": [],
            "lo": None,
            "hi": None,
            "corners": [],
            "breaks": [],
            "electrical_model": {
                "P_elec": IDENTITY_STORE_LINE,
                "reason": (
                    "Load printed. Store OPEN. Identity: printed load × night hours "
                    "= nameplate store Wh. Do not convert battery kg to Wh. "
                    "Do not run Fourier leak without printed store and geometry."
                ),
                "cite": str(fix.get("electrical_model") or IDENTITY_STORE_LINE),
            },
            "witness": "pending",
            "witness_expected": fix.get("witness_expected") or "pending",
            "sources_dir": fix.get("sources_dir"),
        }
        _refuse(rec)
        return rec
    t_box = float(field_value(fix, "T_box_K"))
    t_box_c = (fix.get("fields") or {}).get("T_box_C")
    if isinstance(t_box_c, dict) and t_box_c.get("value") is not None:
        if abs(t_box - (273.15 + float(t_box_c["value"]))) > 1e-9:
            raise ValueError("T_box_K must equal 273.15 + T_box_C")
    t_env_states = _t_env_states(fix)
    store = float(field_value(fix, "store_Wh"))
    h_night = float(field_value(fix, "H_night_h"))
    pk = field(fix, "P_keepalive_W")
    e_br = fix.get("electronics_bracket") or {}
    if pk.get("tier") == "OPEN":
        if e_br.get("lo") is None:
            raise ValueError("OPEN P_night needs electronics_bracket.lo dated bound")
        p_electronics = float(e_br["lo"])
        p_electronics_tier = str(e_br.get("lo_tier") or "OPEN")
    else:
        p_electronics = float(pk.get("value"))
        p_electronics_tier = str(pk.get("tier") or "cited")
    br = fix["geometry_bracket"]
    g_lo = float(br["G_path_W_per_K"]["lo"])
    g_hi = float(br["G_path_W_per_K"]["hi"])
    eps_lo = float(br["eps_eff"]["lo"])
    eps_hi = float(br["eps_eff"]["hi"])
    a_lo = float(br["A_rad_m2"]["lo"])
    a_hi = float(br["A_rad_m2"]["hi"])
    L_path = float(br["L_path_m"]["value"])
    geom_specs = (
        (
            "lo_geom",
            g_lo,
            str(br["G_path_W_per_K"]["lo_tier"]),
            str(br["G_path_W_per_K"]["lo_cite"]),
            eps_lo,
            str(br["eps_eff"]["lo_tier"]),
            a_lo,
        ),
        (
            "hi_geom",
            g_hi,
            str(br["G_path_W_per_K"]["hi_tier"]),
            str(br["G_path_W_per_K"]["hi_cite"]),
            eps_hi,
            str(br["eps_eff"]["hi_tier"]),
            a_hi,
        ),
    )
    k_spec = fix.get("k_path") or {}
    nist_id = str(k_spec.get("nist_id") or "").strip() or None
    corners: list[dict[str, Any]] = []
    nist_last: dict[str, Any] = {}
    for g_name, G, G_tier, G_cite, eps, eps_tier, A_rad in geom_specs:
        for ts in t_env_states:
            k_here, nist_here = _k_at(fix, float(ts["T_env_K"]), t_box)
            nist_last = nist_here
            role = str(ts["role"])
            if role == "cited":
                cname = "lo" if g_name.startswith("lo") else "hi"
            else:
                cname = f"{g_name}_{role}_Tenv"
            st = _state(
                G=G,
                eps=eps,
                A_rad=A_rad,
                k_path=k_here,
                L_path=L_path,
                T_box=t_box,
                T_env=float(ts["T_env_K"]),
                p_electronics=p_electronics,
                store_Wh=store,
                h_night=h_night,
                nist_id=nist_id if nist_here.get("temper_match") else None,
            )
            rec = {
                "name": cname,
                "G_W_per_K": G,
                "G_tier": G_tier,
                "G_cite": G_cite,
                "eps_eff": eps,
                "eps_tier": eps_tier,
                "A_rad_m2": A_rad,
                "T_box_K": t_box,
                "T_env_K": float(ts["T_env_K"]),
                "T_env_role": role,
                "T_env_cite": str(ts["bound"].get("cite") or ""),
                "night_hours": h_night,
                **st,
                "k_source": nist_here.get("k_source"),
                "temper_match": nist_here.get("temper_match"),
            }
            _refuse(rec)
            corners.append(rec)
    lo = min(corners, key=lambda c: float(c["E_night_Wh"]))
    hi = max(corners, key=lambda c: float(c["E_night_Wh"]))
    e_hi_open = electronics_upper_open(fix)
    open_knob = "P_NIGHT" if e_hi_open else None
    lab = public_label(corners, store_Wh=store, open_upward_knob=open_knob)
    label = str(lab["label"])
    edge = bool(lab["edge"])
    worst_corner_margin_Wh = float(lab["worst_corner_margin_Wh"])
    usable = _usable_night_lines(fix, store, h_night)
    p_budget = float(store) / float(h_night)
    p_night_threshold_W: float | None = None
    p_night_threshold_soc8_W: float | None = None
    if e_hi_open and usable:
        p_night_threshold_W = float(usable.get("p_conops_line_W") or usable["p_conops_W"])
        p_night_threshold_soc8_W = float(
            usable.get("p_soc8_line_W") or usable["p_soc8_W"]
        )
        p_line = p_night_threshold_W
        p_soc8_line = p_night_threshold_soc8_W
        for c in corners:
            c["geometry_verdict"] = c["verdict"]
            c["verdict"] = label
            pe = float(c["P_elec_W"])
            c["P_elec_vs_conops"] = f"{pe:.3f} {'<' if pe < p_line else '>='} {p_line:.2f}"
            c["P_elec_vs_soc8"] = (
                f"{pe:.3f} {'<' if pe < p_soc8_line else '>='} {p_soc8_line:.2f}"
            )
            c["P_elec_under_line_W"] = p_line - pe
    breaks = _breaks(
        hi=hi,
        store=store,
        h_night=h_night,
        k_path=float(hi["k_path_w_mk"]),
        L_path=L_path,
        T_box=t_box,
        T_env=float(hi["T_env_K"]),
        p_electronics=p_electronics,
        G_hi=float(hi["G_W_per_K"]),
        eps_hi=float(hi["eps_eff"]),
        A_hi=float(hi["A_rad_m2"]),
    )
    ladder_conops: list[dict[str, Any]] = []
    ladder_soc8: list[dict[str, Any]] = []
    if usable:
        ladder_conops, ladder_soc8 = _ladder_from_usable(fix, usable)
    display = label
    if edge:
        display = f"{label} (edge)"
    rec: dict[str, Any] = {
        "schema": "night_line_record_v1",
        "box": fix.get("name"),
        "box_id": fix.get("box_id"),
        "mission": fix.get("mission"),
        "label": label,
        "label_display": display,
        "edge": edge,
        "worst_corner_margin_Wh": worst_corner_margin_Wh,
        "store_Wh": store,
        "T_box_K": t_box,
        "T_env_K": float(hi["T_env_K"]),
        "H_night_h": h_night,
        "P_electronics_W": p_electronics,
        "P_electronics_tier": p_electronics_tier,
        "P_electronics_break_W": p_budget,
        "electronics_hi_open": e_hi_open,
        "p_night_threshold_W": p_night_threshold_W,
        "p_night_threshold_soc8_W": p_night_threshold_soc8_W,
        "ladder": ladder_conops,
        "ladder_soc8": ladder_soc8,
        "lo": lo,
        "hi": hi,
        "corners": corners,
        "breaks": breaks,
        "nist": nist_last,
        "k_path_w_mk": nist_last.get("k_mean_w_mk"),
        "electrical_model": {
            "P_elec": "max(P_electronics, P_leak)",
            "reason": (
                "At night the box is one thermal node. Heat that leaves is the leak. "
                "Electronics dissipation is already part of that heat. The heater only "
                "makes up P_leak − P_electronics when the leak is larger."
            ),
            "cite": str(
                fix.get("electrical_model")
                or "ICES 2025 Fig. 14 heat balance"
            ),
        },
        "witness": "pending",
        "sources_dir": fix.get("sources_dir"),
    }
    _refuse(rec)
    return rec

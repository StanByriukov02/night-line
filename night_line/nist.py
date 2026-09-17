"""NIST cryogenic k(T) fits actually used by the published boxes, plus six common alloys.

Fits are copied from the NIST Cryogenic Materials Property Database. No coupon from us.
No extrapolation: T outside the printed fit range raises.
"""
from __future__ import annotations

import math
from typing import Any

LETTERS = "abcdefghi"

# Coefficients + URL + rev per material. k only. Forms as published by NIST.
MATERIALS: dict[str, dict[str, Any]] = {
    "invar": {
        "nist_id": "invar",
        "name": "Invar (Fe-36Ni) (UNS K93600)",
        "cite_url": "https://trc.nist.gov/cryogenics/materials/Invar(Fe-36Ni)/Invar_rev.htm",
        "rev": None,
        "k": {
            "form": "log10_poly8",
            "prop": "k",
            "coeffs": {
                "a": -2.7064,
                "b": 8.5191,
                "c": -15.923,
                "d": 18.276,
                "e": -11.9116,
                "f": 4.40318,
                "g": -0.86018,
                "h": 0.068508,
                "i": 0.0,
            },
            "T_min": 4.0,
            "T_max": 300.0,
            "cite_url": "https://trc.nist.gov/cryogenics/materials/Invar(Fe-36Ni)/Invar_rev.htm",
            "rev": None,
        },
    },
    "6061_t6": {
        "nist_id": "6061_t6",
        "name": "6061-T6 Aluminum (UNS A96061)",
        "cite_url": "https://trc.nist.gov/cryogenics/materials/6061%20Aluminum/6061_T6Aluminum_rev.htm",
        "rev": None,
        "k": {
            "form": "log10_poly8",
            "prop": "k",
            "coeffs": {
                "a": 0.07918,
                "b": 1.0957,
                "c": -0.07277,
                "d": 0.08084,
                "e": 0.02803,
                "f": -0.09464,
                "g": 0.04179,
                "h": -0.00571,
                "i": 0.0,
            },
            "T_min": 1.0,
            "T_max": 300.0,
            "cite_url": "https://trc.nist.gov/cryogenics/materials/6061%20Aluminum/6061_T6Aluminum_rev.htm",
            "rev": None,
        },
    },
    "ss_304": {
        "nist_id": "ss_304",
        "name": "304 Stainless (UNS S30400)",
        "cite_url": "https://trc.nist.gov/cryogenics/materials/304Stainless/304Stainless_rev.htm",
        "rev": None,
        "k": {
            "form": "log10_poly8",
            "prop": "k",
            "coeffs": {
                "a": -1.4087,
                "b": 1.3982,
                "c": 0.2543,
                "d": -0.626,
                "e": 0.2334,
                "f": 0.4256,
                "g": -0.4658,
                "h": 0.165,
                "i": -0.0199,
            },
            "T_min": 1.0,
            "T_max": 300.0,
            "cite_url": "https://trc.nist.gov/cryogenics/materials/304Stainless/304Stainless_rev.htm",
            "rev": None,
        },
    },
    "ss_304l": {
        "nist_id": "ss_304l",
        "name": "304L Stainless (UNS S30403)",
        "cite_url": "https://trc.nist.gov/cryogenics/materials/304LStainless/304LStainless_rev.htm",
        "rev": None,
        "k": {
            "form": "log10_poly8",
            "prop": "k",
            "coeffs": {
                "a": -1.4087,
                "b": 1.3982,
                "c": 0.2543,
                "d": -0.626,
                "e": 0.2334,
                "f": 0.4256,
                "g": -0.4658,
                "h": 0.165,
                "i": -0.0199,
            },
            "T_min": 1.0,
            "T_max": 300.0,
            "cite_url": "https://trc.nist.gov/cryogenics/materials/304LStainless/304LStainless_rev.htm",
            "rev": None,
        },
    },
    "ss_316": {
        "nist_id": "ss_316",
        "name": "316 Stainless",
        "cite_url": "https://trc.nist.gov/cryogenics/materials/316Stainless/316Stainless_rev.htm",
        "rev": None,
        "k": {
            "form": "log10_poly8",
            "prop": "k",
            "coeffs": {
                "a": -1.4087,
                "b": 1.3982,
                "c": 0.2543,
                "d": -0.626,
                "e": 0.2334,
                "f": 0.4256,
                "g": -0.4658,
                "h": 0.165,
                "i": -0.0199,
            },
            "T_min": 1.0,
            "T_max": 300.0,
            "cite_url": "https://trc.nist.gov/cryogenics/materials/316Stainless/316Stainless_rev.htm",
            "rev": None,
        },
    },
    "ti_6al_4v": {
        "nist_id": "ti_6al_4v",
        "name": "Ti 6Al 4V (UNS R56400)",
        "cite_url": "https://trc.nist.gov/cryogenics/materials/Ti6Al4V/Ti6Al4V_rev.htm",
        "rev": None,
        "k": {
            "form": "log10_poly8",
            "prop": "k",
            "coeffs": {
                "a": -5107.8774,
                "b": 19240.422,
                "c": -30789.064,
                "d": 27134.756,
                "e": -14226.379,
                "f": 4438.2154,
                "g": -763.07767,
                "h": 55.796592,
                "i": 0.0,
            },
            "T_min": 20.0,
            "T_max": 300.0,
            "cite_url": "https://trc.nist.gov/cryogenics/materials/Ti6Al4V/Ti6Al4V_rev.htm",
            "rev": None,
        },
    },
    "g10_cr": {
        "nist_id": "g10_cr",
        "name": "G-10 CR (Fiberglass Epoxy)",
        "cite_url": "https://trc.nist.gov/cryogenics/materials/G-10%20CR%20Fiberglass%20Epoxy/G10CRFiberglassEpoxy_rev.htm",
        "rev": None,
        "k": {
            "form": "log10_poly8",
            "prop": "k_normal",
            "coeffs": {
                "a": -4.1236,
                "b": 13.788,
                "c": -26.068,
                "d": 26.272,
                "e": -14.663,
                "f": 4.4954,
                "g": -0.6905,
                "h": 0.0397,
                "i": 0.0,
            },
            "T_min": 10.0,
            "T_max": 300.0,
            "cite_url": "https://trc.nist.gov/cryogenics/materials/G-10%20CR%20Fiberglass%20Epoxy/G10CRFiberglassEpoxy_rev.htm",
            "rev": None,
        },
    },
}


def material(nist_id: str) -> dict[str, Any]:
    want = str(nist_id or "").strip()
    if want in MATERIALS:
        return MATERIALS[want]
    raise KeyError(f"unknown nist_id {nist_id}")


def k_rec(nist_id: str) -> dict[str, Any]:
    return material(nist_id)["k"]


def eval_fit(rec: dict[str, Any], T_K: float) -> float:
    form = rec.get("form")
    T = float(T_K)
    tmin = rec.get("T_min")
    tmax = rec.get("T_max")
    if tmin is not None and T < float(tmin) - 1e-12:
        raise ValueError(f"T={T} outside [{tmin}, {tmax}]")
    if tmax is not None and T > float(tmax) + 1e-12:
        raise ValueError(f"T={T} outside [{tmin}, {tmax}]")
    coeffs = rec.get("coeffs") or {}
    if form == "log10_poly8":
        if T <= 0.0:
            raise ValueError("T must be > 0 for log10 fit")
        x = math.log10(T)
        s = 0.0
        for i, L in enumerate(LETTERS):
            s += float(coeffs.get(L, 0.0)) * (x**i)
        return 10.0**s
    if form == "ofhc_k_rational":
        a, b, c, d = (float(coeffs[k]) for k in "abcd")
        e, f, g, h = (float(coeffs[k]) for k in "efgh")
        i = float(coeffs.get("i", 0.0))
        st = math.sqrt(T)
        num = a + c * st + e * T + g * T * st + i * T * T
        den = 1.0 + b * st + d * T + f * T * st + h * T * T
        if den == 0.0:
            raise ValueError("OFHC rational denominator is 0")
        return 10.0 ** (num / den)
    if form == "poly4_T_with_floor":
        t_low = rec.get("T_low")
        if t_low is not None and T < float(t_low) and "f" in coeffs:
            return float(coeffs["f"])
        a = float(coeffs.get("a", 0.0))
        b = float(coeffs.get("b", 0.0))
        c = float(coeffs.get("c", 0.0))
        d = float(coeffs.get("d", 0.0))
        e = float(coeffs.get("e", 0.0))
        return a + b * T + c * T**2 + d * T**3 + e * T**4
    raise ValueError(f"unknown form {form}")


def nist_k(nist_id: str, T_K: float) -> float:
    val = eval_fit(k_rec(nist_id), float(T_K))
    if not math.isfinite(val):
        raise ValueError("cited fit is not finite at this T")
    return val


def k_integral_w_m(nist_id: str, T_lo: float, T_hi: float) -> float:
    """∫ k(T) dT between bounds. W/m. Raises outside the NIST fit range.

    1D steady Fourier: P_cond = (A/L) · ∫ k dT. Simpson n=256.
    """
    lo = float(T_lo)
    hi = float(T_hi)
    sign = 1.0
    if hi < lo:
        lo, hi = hi, lo
        sign = -1.0
    if hi - lo <= 0.0:
        return 0.0
    rec = k_rec(nist_id)
    eval_fit(rec, lo)
    eval_fit(rec, hi)
    n = 256
    h = (hi - lo) / float(n)
    acc = eval_fit(rec, lo) + eval_fit(rec, hi)
    odd = 0.0
    even = 0.0
    for i in range(1, n):
        val = eval_fit(rec, lo + i * h)
        if i % 2:
            odd += val
        else:
            even += val
    integ = (acc + 4.0 * odd + 2.0 * even) * h / 3.0
    if not math.isfinite(integ):
        raise ValueError("k integral is not finite")
    return sign * integ


def k_mean_w_mk(nist_id: str, T_lo: float, T_hi: float) -> float:
    lo = min(float(T_lo), float(T_hi))
    hi = max(float(T_lo), float(T_hi))
    dt = hi - lo
    if dt <= 0.0:
        raise ValueError("T_hi and T_lo must differ")
    return k_integral_w_m(nist_id, lo, hi) / dt


def nist_cite(nist_id: str) -> dict[str, Any]:
    mat = material(nist_id)
    rec = k_rec(nist_id)
    return {
        "nist_id": nist_id,
        "prop": rec.get("prop") or "k",
        "cite_url": rec.get("cite_url") or mat.get("cite_url"),
        "rev": rec.get("rev") if rec.get("rev") is not None else mat.get("rev"),
        "T_min": rec.get("T_min"),
        "T_max": rec.get("T_max"),
        "name": mat.get("name"),
    }

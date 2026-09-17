# Two courts — LuSEE-Night

SPDX-License-Identifier: MIT

Copyright (c) 2026 Night Line contributors. Permission is hereby granted, free of charge, to any person obtaining a copy of this document, to use, copy, modify, merge, publish, and distribute it, subject to including this notice. Provided “as is”, without warranty.

Dated **2026-09-17**. **MEASURED=false**.

I, Stanislav Byriukov, computed both courts on 17 September 2026 from the cited pages. Each URL in Sources returned HTTP 200 that day. No measurement by me.

A stranger can see **why** this repository prints `LIVE_IF_P_NIGHT_BELOW` **13.20 W** on LuSEE-Night, why another reconstruction of the same named box prints **DIE**, which dated print each stands on, and which knob flips them. The two courts are not averaged. CDR 12.4 W is not mixed into the 2024 line.

## Named box

**LuSEE-Night** (Lunar Surface Electromagnetics Experiment at Night) on CLPS CS-3 / Firefly Blue Ghost Mission 2. The lander is off before night. Night Line record: [LINES.md](LINES.md). Method: [NIGHT_LINE_SPEC_V1.md](NIGHT_LINE_SPEC_V1.md).

## Court A — Night Line on the 2024 print

Label: `LIVE_IF_P_NIGHT_BELOW` **13.20 W**.

Print: arXiv [2407.07173](https://arxiv.org/pdf/2407.07173) (SPIE 2024). Nameplate **7160 Wh**, **328 h**, ConOps **30 % SOC**, discharge **×0.95**, load uncertainty **÷1.10**.

```text
7160 × (1 − 0.30) / 328 = 15.28 W usable
15.28 × 0.95 = 14.52 W
14.52 ÷ 1.10 = 13.20 W
```

Nameplate 7160/328 = **21.83 W** is not the survival line. 2024 average night load is **not printed**. Geometry **A_rad** / `e*` / **G** is **OPEN**, so this court does not print a Fourier **DIE** from an assumed radiator area.

| Stands on | Does not stand on |
|---|---|
| 2024 printed store, hours, 30 % SOC, 95 % discharge, 10 % load uncertainty | A 2024 average night watt (not printed) |
| OPEN geometry — no assumed-area Fourier DIE | CDR 2023 12.4 W as 2024 flight load |
| The paper’s own usable → derated ladder | Nameplate 21.83 W as the line |

## Court B — Fourier reconstruction on unprinted fills

This court is **not** their 2024 print.

On **assumed** A_rad **0.15 m²**, catalog dust **3 g/m²**, assumed `e*` and k_ins **5e-4 W/m·K**, assumed T_env **70 K**, a derived heater **~34.5 W** plus CDR **12.4 W** exhausts the 7160 Wh nameplate before 328 h (**DIE**). P_ops **12.4 W** is CDR 2023 ([Zenodo 8173058](https://doi.org/10.5281/zenodo.8173058)), older than 2024. Those fills are not the 2024 print.

The 2024 paper prints night surface as low as **100 K**, pack **−5…+30 °C**, thermal switch **open** at night, and does **not** print radiator area.

`verdict_stands_on_latest_print: false`. Weakest knob: **A_rad**. Ops at **0 W** still DIE on that dusty assumed radiator — so DIE is not “they drew 12.4 W”.

That DIE exists only on those assumed fills. It is not the Night Line.

| Stands on | Does not stand on |
|---|---|
| Assumed A_rad 0.15 m² × catalog dust × assumed `e*`, k, T_env 70 K | 2024 radiator area (not printed) |
| Older CDR 12.4 W as P_ops | 2024 average night load |
| Derived heater 34.49 W on that geometry | 2024 night surface 100 K / pack −5…+30 °C as this court’s T_env / T_set |

## Hand energy on the 2024 nameplate (not P_night)

Do not mint a 2024 average watt. These brackets sit on nameplate only — not Court A’s ladder, not Court B.

```text
CDR-older 12.4 W × 328 h vs 7160 Wh → +3092.8 Wh  LIVE on nameplate
2024 night-core constants 18.21 W × 328 h → +1187 Wh  LIVE on nameplate
```

18.21 W is the arithmetic sum of 2024 printed night-core constant loads (PDU 0.1 + PFPS 6 + DCB 2 + SPT 9.25 + preamp 0.86 W). It is not a duty-cycled average. The paper prints that a continuous spectrometer does not fit; they duty-cycle. Average remains **OPEN**.

## Public tests — which label a signer may use

The human who can lose the box signs. The label is on the dated set named in the row. It is not a claim that the box will live.

| Dated set | Signer may use | Signer may not use |
|---|---|---|
| 2024 arXiv 2407.07173, geometry OPEN | `LIVE_IF_P_NIGHT_BELOW` 13.20 W | `LIVE` (average load unprinted); `DIE` from assumed A_rad |
| Reconstruction on assumed A_rad 0.15 m² + dust 3 g/m² + T_env 70 K + CDR 12.4 W | `DIE` on those assumed fills | “the 2024 paper says DIE”; that DIE as the Night Line |
| CDR 2023 12.4 W × 2024 328 h vs 2024 7160 Wh | LIVE on nameplate (+3092.8 Wh) | Court A’s 13.20 W; Court B’s DIE |

## Which knob flips them

| Knob | Court A | Court B |
|---|---|---|
| Printed 2024 average night load W | Closes `LIVE_IF` to `LIVE` or `DIE` | Unchanged (not this court’s load) |
| Printed radiator area m² (weakest on Court B) | Stays OPEN until printed; no assumed DIE | Heater and DIE energy move; 0.15 m² is the assumed fill |
| Drop assumed dust / 70 K / `e*` / k | No effect (those fills unused) | Can flip DIE |

Publishing only Court A while Court B exists on assumed fills is a false night-sign. Both, dated and unmixed, is the honest sign.

## Sources (HTTP 200, 2026-09-17)

| Page | URL | HTTP |
|---|---|---|
| arXiv 2407.07173 — 2024 print (7160 Wh, 328 h, ladder, no P_night, no A_rad) | https://arxiv.org/pdf/2407.07173 | 200 |
| Zenodo CDR 8173058 — older night 12.4 W | https://doi.org/10.5281/zenodo.8173058 | 200 |
| Firefly BGM2 — lander off before nightfall | https://fireflyspace.com/missions/blue-ghost-mission-2/ | 200 |
| NASA CS-3 — self-reliant payload | https://science.nasa.gov/lunar-science/clps-deliveries/cs-3/ | 200 |

Public record: [github.com/StanByriukov02/night-line](https://github.com/StanByriukov02/night-line) — `LINES.md`, `NIGHT_LINE_SPEC_V1.md`.

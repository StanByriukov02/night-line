# Two courts — LEMS-A3 leak

SPDX-License-Identifier: MIT

Copyright (c) 2026 Night Line contributors. Permission is hereby granted, free of charge, to any person obtaining a copy of this document, to use, copy, modify, merge, publish, and distribute it, subject to including this notice. Provided “as is”, without warranty.

Dated **2026-09-17**. **MEASURED=false** on the A3 flight row. One number below is their TVAC, on the TRL-6 article, not on A3.

I, Stanislav Byriukov, computed these identities on 17 September 2026 from ICES 2025 NTRS [20250005257](https://ntrs.nasa.gov/api/citations/20250005257/downloads/ICES_2025_LEMS_BurbridgeRodriguez_v5.pdf). No measurement by me. The courts are not averaged. TRL-6 watts are not the A3 Night Line.

A stranger can see three numbers that look like one leak: a **measured** predecessor leak, a **CDR analysis** leak, and a **Fourier** line on OPEN geometry. Taking any one as the other is the lie.

## Named box

**LEMS-A3** (Lunar Environment Monitoring Station for Artemis III), GSFC / UMD, PI Benna, HLS. Night Line record: [LINES.md](LINES.md). Method: [NIGHT_LINE_SPEC_V1.md](NIGHT_LINE_SPEC_V1.md). Sizing table around BREAK: [BREAK_SURFACE_LEMS_V1.md](BREAK_SURFACE_LEMS_V1.md). What to measure next: [MEASURE_LEMS_V1.md](MEASURE_LEMS_V1.md).

## Court M — TRL-6 TVAC (measured, predecessor)

ICES p.3: the nighttime thermal energy leak **was measured** to be **1407.3 Wh** for **354 h**, equivalent continuous **3.98 W**. That is DALI / TRL-6, 2018–2022, not the A3 flight article.

```text
1407.3 / 354 = 3.975 W  (paper rounds to 3.98 W)
3.98 × 354 = 1408.92 Wh
640 / 3.98 = 160.8 h
```

Against the A3 **640 Wh** allocation for **354 h**, a 3.98 W leak **exhausts the store in 161 h**. That is not a Night Line on A3. It is the measured leak of the article they already tested.

## Court C — A3 CDR Fig. 14 (analyzed, not measured)

ICES Fig. 14 / §V: nighttime heat leak **1.528 W** for **354 h** or **541 Wh**. Electronics CBE **1.231 W**, heater **0.297 W**. Path watts: heat switch **0.474 W**, SAPP **0.398 W**, launch lock **0.353 W**, IMLI **0.303 W**. Battery allocation **640 Wh**, analyzed margin **99 Wh (15 %)**.

```text
1.528 × 354 = 540.91 Wh  (paper 541 Wh)
640 − 541 = 99 Wh
```

The paper says the TCS leak was reduced **2.452 W / 61 %** versus the TRL-6 **3.98 W**. That reduction is **analysis versus a prior measurement**, not a new TVAC of A3.

Fig. 14 does **not** print strut A/L or IMLI area in square metres. ULTEM 2300 in Table 3 is a **coating** row (α, ε), not k(T). A Night Line that uses only NIST k(T) plus their printed A/L stays parked until A/L is printed.

## Court N — Night Line Fourier (OPEN geometry)

Public line on this repo: **LIVE (edge)**, worst declared corner **+5.76 Wh**, BREAK radiator **0.828 m²**, G **6.07 mW/K**, electronics **1.808 W**. That court uses the A3 printed store, hours, electronics, e* upper bound, heat-switch G bound, and a **declared** A_rad / extra-G bracket. It is not Court M. It is not Court C's 541 Wh (C already folds their Thermal Desktop leak; N rebuilds leak from OPEN A_rad).

P_elec = max(P_electronics, P_leak). Do not add 1.231 W on top of 1.528 W.

## Court P — A3 system TVAC plan (ICES 2026 490, not a leak measurement)

ICES 2026 490 is the **test plan** for a flight-like system TVAC. The abstract prints that the thermal system is limited to **2.5 W** of heat during the lunar night, and that **the test will measure** nighttime heat leaks for the bus and seismometers. That sentence is a future measurement. It is not Court M. It is not Court C.

The same paper prints a **measured battery capacity** at −30 °C of **940.8 Wh**. That is not the ICES 2025 **640 Wh** TCS allocation. Do not paste 940.8 onto the Night Line store.

It prints a **predicted** night consumption **849.5 Wh** (3σ systematic) against that 940.8 Wh capacity, leaving **121.3 Wh** for sensor-noise error **once the test is run**. Table 5 totals **2.318 W / 834.5 Wh** before that 3σ wrap. Table 4 flight-model bus heat loss **1.654 W** (TVAC-model **1.551 W**). “The system heat leak is about **1.5 W**” is the analysis used to justify a long cooldown, in the same family as Court C’s 1.528 W — not a new TVAC of A3.

January 2026 checkout in this paper used the **TRL-6 development unit plus GSE**, to prove a GN2 backfill trick. That is not the A3 leak.

```text
940.8 Wh  measured capacity @ −30 °C   ≠  640 Wh TCS allocation
849.5 Wh  predicted night (3σ)         ≠  measured leak
2.5 W     heat limit                    ≠  leak
2.318 W   Table 5 predicted total       ≠  Court C 1.528 W path leak
```

`MEASURED=false` on the A3 flight leak until the system TVAC writes Wh with the article named.

## Do not mix

| If you take… | as… | you print |
|---|---|---|
| 3.98 W measured | A3 flight leak | DIE on 640 Wh / 354 h — **wrong box** |
| 1.528 W analyzed | a measurement | **MEASURED=true** — lie |
| 0.828 m² BREAK | their radiator | **their print** — lie |
| suitcase-size | A/L | invented geometry |
| 940.8 Wh capacity @ −30 °C | the 640 Wh allocation | **wrong object** |
| 849.5 Wh predicted | a TVAC leak | **MEASURED=true** — lie |
| 2.5 W heat limit | the leak | **wrong kind** |

## Derived tension (not a print)

Fig. 14 heat-switch path **0.474 W**. Table 5 cold-op: bus heat switch **−29.2 °C**, bus radiator **−129.4 °C**. If those two nodes are the open-path ends:

```text
ΔT = 100.2 K
G_implied = 0.474 / 100.2 = 4.73 mW/K
```

Printed open conductance is **below 0.002 W/K**. 4.73 mW/K is derived, not A/L, and does not print A/L. It names a fight between the path watt and the G sentence **if** that ΔT is the path.

SAPP is the path that **does** print a ΔT: internal **−30 °C** to external **≈ −200 °C** (170 K). Fig. 14 SAPP **0.398 W** → G_implied **2.34 mW/K** on that ΔT. Also derived.

## Sources

| Object | URL | HTTP 17 Sep 2026 |
|---|---|---|
| ICES 2025 NTRS 20250005257 | https://ntrs.nasa.gov/api/citations/20250005257/downloads/ICES_2025_LEMS_BurbridgeRodriguez_v5.pdf | 200 |
| ICES 2026 490 (TTU-IR bitstream) | https://ttu-ir.tdl.org/bitstreams/e7bd2dd1-cb1b-434a-a341-4391e75cc6c7/download | 200 |

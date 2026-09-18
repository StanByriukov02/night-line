# LEMS-A3 — BREAK as a sizing surface

SPDX-License-Identifier: MIT

Copyright (c) 2026 Night Line contributors. Permission is hereby granted, free of charge, to any person obtaining a copy of this document, to use, copy, modify, merge, publish, and distribute it, subject to including this notice. Provided “as is”, without warranty.

Dated **2026-09-17**. **MEASURED=false**. Sweep values are **not** their print.

Hold the worst declared corner (T_env 23 K, G 0.006 W/K or A_rad 0.80 m², e* 0.0028, electronics 1.231 W). Move one knob. The BREAK is the value where the **640 Wh** allocation is empty at exactly **354 h**.

```text
night-line surface
```

Writes `out/lems_a3/BREAK_SURFACE_A_RAD.csv` and `BREAK_SURFACE_G.csv`.

P_elec = max(P_electronics, P_leak). On the printed heat-switch G bound (< 0.002 W/K) the leak sits **below** 1.231 W, so hours freeze on electronics ≈ 520 h — a tighter radiator does not buy night until leak exceeds electronics. On the worst declared G (0.006 W/K) the leak is already above electronics even at the small A_rad corner. That plateau is the useful fact.

## A_rad (G 0.006 W/K, e*, T held at the worst declared corner)

| A_rad m² | role | their print? | regime | P_leak W | hours | margin Wh | corner |
|---|---|---|---|---|---|---|---|
| 0.05 | declared_lo | no | leak_bound | 1.362 | 470.0 | +158.0 | LIVE |
| 0.40 | ASSUMED_sweep | no | leak_bound | 1.562 | 409.7 | +87.0 | LIVE |
| 0.80 | declared_hi | no | leak_bound | 1.792 | 357.2 | +5.76 | LIVE |
| 0.828 | BREAK | no | leak_bound | 1.808 | 354.0 | 0 | LIVE |
| 1.00 | ASSUMED_sweep | no | leak_bound | 1.906 | 335.7 | −34.8 | DIE |
| 1.20 | ASSUMED_sweep | no | leak_bound | 2.021 | 316.7 | −75.4 | DIE |

Do not take 0.828 m² as a printed IMLI area. Do not take a middle row as their radiator. 1.00 m² is an assumed sweep that **dies** on this held corner — still not their print.

## G (A_rad 0.80 m², e*, T held)

| G W/K | role | their print? | regime | P_leak W | hours | margin Wh | corner |
|---|---|---|---|---|---|---|---|
| 0.002 | printed_G_bound | bound, one path | electronics_bound | 0.903 | 519.9 | +204.2 | LIVE |
| 0.006 | declared_hi | no | leak_bound | 1.792 | 357.2 | +5.76 | LIVE |
| 0.00607 | BREAK | no | leak_bound | 1.808 | 354.0 | 0 | LIVE |
| 0.008 | ASSUMED_sweep | no | leak_bound | 2.236 | 286.2 | −151.5 | DIE |
| 0.010 | ASSUMED_sweep | no | leak_bound | 2.680 | 238.8 | −308.8 | DIE |

## Courts

Fig. 14 path watts versus this Fourier: [TWO_COURTS_LEMS_V1.md](TWO_COURTS_LEMS_V1.md).

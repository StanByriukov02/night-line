# LEMS-A3 — what to measure (and what not to)

SPDX-License-Identifier: MIT

Copyright (c) 2026 Night Line contributors. Permission is hereby granted, free of charge, to any person obtaining a copy of this document, to use, copy, modify, merge, publish, and distribute it, subject to including this notice. Provided “as is”, without warranty.

Dated **2026-09-17**. This is a demand list on **this named box**, not a catalog of alloys that are not on it. No measurement by Night Line. **MEASURED=false** until a lab writes a number with a page.

Cites: ICES 2025 NTRS [20250005257](https://ntrs.nasa.gov/api/citations/20250005257/downloads/ICES_2025_LEMS_BurbridgeRodriguez_v5.pdf); ICES 2026 490 [TVAC plan](https://ttu-ir.tdl.org/items/558a9fff-ee0f-4923-8724-115fe3355fb7). Courts: [TWO_COURTS_LEMS_V1.md](TWO_COURTS_LEMS_V1.md).

## Closed without a new coupon

| Item | Why closed | Source |
|---|---|---|
| Invar Fe-36Ni k(T) | NIST 4–300 K, temper matches the named INVAR 36 rod | [NIST Invar](https://trc.nist.gov/cryogenics/materials/Invar(Fe-36Ni)/Invar_rev.htm) |
| IMLI e* upper | **measured** < 0.0028 on TRL-6 IMLI (same layup claimed for A3) | ICES §II.B |
| Fig. 14 path watts | printed analysis (not k, not A/L) | ICES Fig. 14 |
| TRL-6 leak 1407.3 Wh / 3.98 W | **measured**, predecessor article — do not rebuy; do not paste onto A3 | ICES 2025 p.3 |
| Flight battery capacity 940.8 Wh @ −30 °C | **measured** capacity, not the 640 Wh TCS allocation, not a leak | ICES 2026 490 |
| 2.5 W night heat **limit** | a constraint for the TCS, not a leak | ICES 2026 490 abstract |

Do not buy C-103, Haynes 230, Zr-702, or CFRP for LEMS. Those alloys are not named on this box.

## Needs a number (rank is leverage on the 640 Wh / 354 h allocation)

| Rank | Object | What to write | Closes |
|---|---|---|---|
| 1 | A3 system TVAC night leak **result** | Wh over a printed night, or equivalent W, with the article named. ICES 2026 490 is the **plan** (“the test will measure”). Predicted 849.5 Wh / 2.318 W is not that result. | Court M vs Court C vs Court P: is 1.528 W real on the flight stack, or still 3.98 W, or the 2.5 W limit? |
| 2 | Radiator / IMLI area | m², URL + figure | Fourier A_rad OPEN. BREAK 0.828 m² is not this number. |
| 3 | Four ULTEM 1000 standoffs A and L | mm² and mm, deployed path | Launch-lock G. Suitcase-size is not A/L. |
| 4 | ULTEM 1000 k(T) | 80–250 K, lot named | No NIST map. Night path is the four standoffs, not the Invar rod. |
| 5 | Titanium mechanical-leg alloy | named mill (not “titanium”) | Paper leaves the alloy OPEN. Do not assume Ti-6Al-4V. |

Rank 1 is the measurement that makes Court C honest or dead. Ranks 2–3 are prints the PI already has. Rank 4 is a coupon a cryo lab can run. Rank 5 is a sentence in an ICD.

The human who can lose the box signs which row is bought. This page does not.

# Witness map — which named box on which host can see a lunar night

SPDX-License-Identifier: MIT

Copyright (c) 2026 Night Line contributors. Permission is hereby granted, free of charge, to any person obtaining a copy of this document, to use, copy, modify, merge, publish, and distribute it, subject to including this notice. Provided “as is”, without warranty.

Dated **2026-09-17**. **MEASURED=false**. **MANIFEST_CLOSED=false**.

I, Stanislav Byriukov, read the cited public pages on 17 September 2026 and wrote this map from those prints. It is not a seventh energy line. It is not a closed list of CLPS flights. A landing name is not a row.

A lab can see, on one page, which named box on which host printed that it will **not** run the night — which named box printed that it might, with the store still OPEN or with the lander already off — which NASA-center guest waits on an OPEN host rover — and which box takes no power at all.

## What this is for

If you are sizing a night battery, a night TVAC, or a “next CLPS night” paragraph: read the host row and the payload row separately.

- Lunar Vertex on IM-3 printed **day-only**. Do not wait for that night.
- Blue Ghost Mission 2 **the lander** printed power-off before nightfall. LuSEE-Night **the payload** printed that it stays. Those are two rows.
- Griffin-1 **the lander** PUG thermal envelope excludes lunar night. FLIP **the rover** printed survive-the-night with watt-hours OPEN. Those are two rows. Launch NET November 2026 is not a sunset. Venturi’s battery page prints **10,000 cells** and −240…+130 °C, not watt-hours. A Venturi intro prints **180 hours** of nights under −180 °C — that is not a store, and not Cataldo 354 h.
- MK1 prints cargo mass and names a PUG that is not public here. Do not mint night watts. The product page returned HTTP 429 on 17 September 2026.
- Blue Ghost Mission 1 already flew **5 h** after sunset and printed it was not designed for the cold night. That is not a full-night offer and not BGM2.
- FSS on CP-12: the host task order is printed ended. Re-flight is UNVERIFIED — absent, not CANNOT.
- Zeno on CS-8: launch no earlier than **2028**. Not this window. 5 Wt is heat, not bus watts.
- GSFC **LRA** on FLIP: eight quartz cubes. The array **requires no power**. Do not wait for an LRA night-store.
- NASA Ames / Interlune **METAL**, JSC **LDES**, MSFC **Lunar LiDAR** ride FLIP as guests. They print cameras, dust-on-radiators, and maps — not watt-hours. Night wait is FLIP’s OPEN store, not Griffin PUG, not a seventh energy line.
- Lunar-VISE (UCF, PI Kerri Donaldson-Hanna) on Firefly Blue Ghost 3 / CP-21: **10-day** science investigation, **one lunar day** traverse, launch **2028**. Do not wait for a VISE night.

Unnamed task orders and the unpublished NASA Lunar Payload Database are **absent**. Absent is not CANNOT.

## Reproduce

```text
night-line witness-map
```

Writes `out/witness_map/{WITNESS_MAP.md,WITNESS_MAP.csv,WITNESS_MAP.json}`. The verifier recomputes each label from the cited flags and checks saved source hashes. The map prints **do not inherit** pairs: Griffin ↛ FLIP, Griffin ↛ FLIP guests, FLIP ↛ LRA, BGM2 ↛ LuSEE. Energy lines stay on [LINES.md](LINES.md). FLIP sunset clock: [WITNESS_CLOCK_FLIP_V1.md](WITNESS_CLOCK_FLIP_V1.md). Lander inputs sheet: [PUG_NIGHT_LINE_INPUTS_V1.md](PUG_NIGHT_LINE_INPUTS_V1.md). LEMS leak courts (including the ICES 2026 TVAC **plan**): [TWO_COURTS_LEMS_V1.md](TWO_COURTS_LEMS_V1.md).

The human who can lose the box signs which wait to keep. This page does not.

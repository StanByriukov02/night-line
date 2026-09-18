# Night Line inputs — payload Appendix A (CLPS lander requirements)

SPDX-License-Identifier: MIT

Copyright (c) 2026 Night Line contributors. Permission is hereby granted, free of charge, to any person obtaining a copy of this document, to use, copy, modify, merge, publish, and distribute it, subject to including this notice. Provided “as is”, without warranty.

Paste this page into the payload’s **Appendix A** — the document that defines lander requirements, CONOPS, **power**, and data — while that appendix is still open. It is not a lander PUG (that sheet is [PUG_NIGHT_LINE_INPUTS_V1.md](PUG_NIGHT_LINE_INPUTS_V1.md)). It is not a CLPS bid. It is not a seventh energy line.

I, Stanislav Byriukov, reconstructed the worked example from cited public pages on 18 September 2026. **MEASURED=false**. The human who can lose the named box signs. I do not.

A **Survive-the-Night** task-order name is not a watt-hour. Do not size a night store from the TO name. Print the knobs, or leave them OPEN.

## 1. Law (paste into Appendix A)

```
NL-A1  Survive-the-Night as a task-order or PRISM service name shall not be
       used as the payload’s night store Wh or as night keep-alive W.

NL-A2  A printed lunar-day operations window (hours of sunlight / payload
       ops) shall not be used as Cataldo night hours unless the page labels
       it darkness.

NL-A3  “No night operations” in a threshold mission shall not be rewritten
       as a keep-alive budget. It is a CONOPS bound, not a watt.

NL-A4  Each Night Line input in §3 shall carry a URL and a page or figure,
       or the cell shall remain OPEN. An OPEN cell shall not be filled from
       a predecessor design or a sibling box.
```

## 2. Worked example — DIMPLE on CLPS CP-32 (Appendix A still open)

Host lander TBD. Flight **2029**. PRISM grant **80NSSC24M0001**. NASA (19 July 2023): payload-suite cost cap **$50 million** ([news](https://www.nasa.gov/news-release/new-nasa-artemis-instruments-to-study-volcanic-terrain-on-the-moon/)). Map row: `STN_TO_PAYLOAD_DAY` on [WITNESS_MAP_V1.md](WITNESS_MAP_V1.md).

| Night Line input | Already printed | Still OPEN / payload must add |
|---|---|---|
| Named box | **DIMPLE** (Dating an Irregular Mare Patch with a Lunar Explorer) | — |
| Host | **CLPS CP-32**, lander TBD, Ina | Lander name when NASA prints the award |
| Surface CONOPS | LPSC 2024 2547: **All surface operations are to be completed within a single lunar day of ~348 hours** ([PDF](https://www.hou.usra.edu/meetings/lpsc2024/pdf/2547.pdf)) | Do not treat 348 h as darkness |
| Payload ops window | LPSC 2026 1816: **280 hour payload operations window** ([PDF](https://www.hou.usra.edu/meetings/lpsc2026/pdf/1816.pdf)) | Do not treat 280 h as night store hours |
| Appendix A status | LPSC 2026 1816: team **completing Appendix A** (lander requirements; **CONOPS, power**, data) | Fill §3 before freezing power |
| Survive-the-Night as TO name | Jenkins ESSIO 2023-01-11: **Survive the Night (Future TO CP-32)** ([PDF](https://science.nasa.gov/wp-content/uploads/2023/11/techshow-jej.pdf)) | Not a Wh |
| Threshold night ops | Jenkins: PRISM 3 threshold **survive through one lunar night**; **There will be no night operations supported in the threshold mission** | Not a keep-alive W |
| Store Wh nameplate | **not printed** | Nameplate Wh, or OPEN |
| Average night electrical load W | **not printed** | Night keep-alive W, or OPEN |
| Heater W | **not printed** | Heater W, or OPEN |
| Night hours | **not printed** as darkness | Printed darkness hours if a store is claimed. Cataldo/Mason 354 h is a reference, not DIMPLE’s print |

Do not mint W. Do not letter from this page.

## 3. Blank row — payload filling Appendix A now

Named box: ______________________________

Host lander / TO: ______________________________

Signer (human who can lose the box): ______________________________

| Night Line input | cited / OPEN / team_provided | URL + page or figure | Value |
|---|---|---|---|
| Store Wh nameplate | | | |
| Reserve SOC % | | | |
| Charge / discharge η | | | |
| Load uncertainty | | | |
| Night hours (darkness) | | | |
| Average night electrical load W | | | |
| Electronics dissipation W | | | |
| Heater W | | | |
| T_box | | | |
| T_env bounds | | | |
| Radiator area m² | | | |
| Effective emissivity e* | | | |
| Conductance G, or strut A/L + named alloy | | | |

A lunar-day ops window goes in CONOPS, not in “Night hours” unless the page labels darkness.

## 4. How a reconstruction starts

Fill §3. Open a GitHub issue from the **Night Line inputs** template, or attach [PO_SCOPE_V1.md](PO_SCOPE_V1.md) to the grant as professional services. Unpublished ICD / ITAR thermal stays in the lab ([15 CFR 734.7](https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C/part-734/section-734.7)).

Close one OPEN later with a number that already has a page: [CLOSE_PROTOCOL_V1.md](CLOSE_PROTOCOL_V1.md).

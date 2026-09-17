# Night Line — professional-services scope

SPDX-License-Identifier: MIT

Copyright (c) 2026 Night Line contributors. Permission is hereby granted, free of charge, to any person obtaining a copy of this document, to use, copy, modify, merge, publish, and distribute it, subject to including this notice. Provided “as is”, without warranty.

A university PI can attach this page to a grant as professional services. Method: [NIGHT_LINE_SPEC_V1.md](https://github.com/StanByriukov02/night-line/blob/main/NIGHT_LINE_SPEC_V1.md). Public examples: [github.com/StanByriukov02/night-line](https://github.com/StanByriukov02/night-line).

I, Stanislav Byriukov, reconstruct one Night Line on the PI’s named box. The human who can lose that box signs. I do not.

## 1. What is purchased

Independent reconstruction of a Night Line on the PI’s named box from (a) already-published numbers and/or (b) one team-provided number with a page or figure.

Deliverable:

- `LINE.md` — the line, the label, the OPEN knobs, and the cites
- `INPUTS.csv` — every input marked `cited`, `OPEN`, or `team_provided`
- a dated public row, if the PI allows it; otherwise a private `LINE.md` only

A Night Line is the largest average electrical load the named box can carry through the printed night on the team’s own printed store, reserves, and efficiencies. Unprinted knobs stay OPEN. The label is on declared corners only; it is not a claim that the box will live.

## 2. What is not purchased

- A Thermal Desktop model, or a replacement for one
- An unpublished lander ICD, or any ITAR / unpublished thermal file
- Measurement-lab coupons, or any measurement by me
- A C-corporation invoice — the buyer pays Stanislav Byriukov as an individual; I provide [IRS Form W-8BEN](https://www.irs.gov/forms-pubs/about-form-w-8ben); the work is performed outside the United States

## 3. Inputs the PI must supply

OPEN stays OPEN. I do not fill an unprinted knob from a predecessor design. I do not mint a number without a page or figure.

| Input | What the PI supplies |
|---|---|
| Named box | Official name as printed |
| Path (a) and/or (b) | (a) URL + page or figure for each published number used; and/or (b) one team-provided number with a page or figure |
| Store Wh (nameplate) | cited, team-provided with page/figure, or OPEN |
| Reserve SOC % | cited, team-provided with page/figure, or OPEN |
| Charge / discharge efficiency | cited, team-provided with page/figure, or OPEN |
| Load uncertainty | cited, team-provided with page/figure, or OPEN |
| Night hours | cited, team-provided with page/figure, or OPEN |
| Average night electrical load (W) | cited, team-provided with page/figure, or OPEN |
| Electronics dissipation (W) | cited, team-provided with page/figure, or OPEN |
| Heater (W) | cited, team-provided with page/figure, or OPEN |
| T_box | cited, team-provided with page/figure, or OPEN |
| T_env bounds | cited, team-provided with page/figure, or OPEN |
| Radiator area (m²) | cited, team-provided with page/figure, or OPEN |
| Effective emissivity e* | cited, team-provided with page/figure, or OPEN |
| Conductance G, or strut A/L + named alloy | cited, team-provided with page/figure, or OPEN |
| Public row | allow a dated public row, or keep the LINE private |
| Signer | name of the human who can lose the box |

## 4. Scope bound

This purchase is the public-numbers path. Published information is not subject to the EAR ([15 CFR 734.7](https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C/part-734/section-734.7)). Unpublished thermal data released to a foreign person is out of scope until the buyer classifies it.

## 5. Time and rate

Reconstruction from one already-published paper is hours of work, not weeks. I do not print a calendar quote on this page.

I do not print a bid. A published GSA Multiple Award Schedule Consultant not-to-exceed (NTE) figure — **not our price, not a quote** — is **$150.41–$162.03 per hour** (Consultant, Contractor Site, fully burdened with IFF) on AMSG MAS pricelist PO-0036, 23 January 2025: [PDF](https://amsgcorp.net/wp-content/uploads/2025/03/AMSG-GSA-MAS-Pricelist-PO-0036-01-23-2025.pdf).

## 6. Example already public

Already on [github.com/StanByriukov02/night-line](https://github.com/StanByriukov02/night-line):

- **LEMS-A3** — `LIVE (edge)` +5.76 Wh
- **LuSEE-Night** — `LIVE_IF` 13.20 W

## 7. How this starts

Complete the table in §3 for one named box (`cited` / `team_provided` / `OPEN`). Open an issue on this repository with that table, or send the table with a page or figure for each `team_provided` number. I return `LINE.md` and `INPUTS.csv`. OPEN stays OPEN until a page exists.

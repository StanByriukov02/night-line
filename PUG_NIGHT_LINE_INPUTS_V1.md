# Night Line inputs — lander PUG / payload questionnaire

SPDX-License-Identifier: MIT

Copyright (c) 2026 Night Line contributors. Permission is hereby granted, free of charge, to any person obtaining a copy of this document, to use, copy, modify, merge, publish, and distribute it, subject to including this notice. Provided “as is”, without warranty.

I, Stanislav Byriukov, reconstructed this sheet on 17 September 2026 from the cited public pages. Each URL in §§1–2 and the Cataldo/Mason PDF returned HTTP 200 that day. MEASURED=false. Cite or leave OPEN. I do not mint watt-hours from kilograms. The human who can lose the box signs. I do not.

Paste this page into a Payload Users Guide appendix or an ICD kickoff questionnaire. The rows are the Night Line inputs. Method and public record: [github.com/StanByriukov02/night-line](https://github.com/StanByriukov02/night-line) — `NIGHT_LINE_SPEC_V1.md`, `PO_SCOPE_V1.md`, `LINES.md`.

This sheet is for **published** numbers ([15 CFR 734.7](https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C/part-734/section-734.7)). Unpublished lander ICD / ITAR thermal stays off this page.

Night hours, unless the lander PUG prints a site-specific night: Cataldo & Mason 2018, LPI Contrib. 2106, abstract 7032 ([PDF](https://www.lpi.usra.edu/lpi/contribution_docs/LPI-002106.pdf)) — “A complete lunar day cycle is 354 hours of sunlight and 354 hours of darkness.” Darkness reference only.

## 1. Astrobotic Griffin — PUG 12 January 2022

Source (HTTP 200, 17 Sep 2026): [PUGLanders_011222.pdf](https://voyagertechnologies.com/wp-content/uploads/2026/07/PUGLanders_011222.pdf)

| Night Line input | Already printed | Still OPEN / payload must add |
|---|---|---|
| Store Wh nameplate | Li-ion pack named; watt-hours not printed (p.28 Power) | Nameplate Wh for the named box. Do not mint from kg. Do not copy a predecessor rover battery. |
| Reserve SOC % | — | Printed ConOps / safe-recharge minimum, or OPEN |
| Charge / discharge η | — | Printed efficiencies, or OPEN |
| Load uncertainty | — | Printed fractional margin, or OPEN |
| Night hours | Griffin polar surface ops **up to 14 days** (p.23 Polar Configuration). Peregrine lunar **day** 354 h sunrise-to-sunset (p.51 Landing Site). Surface thermal **does not include lunar night** (p.35). | Printed night hours for this box / this site. Polar 14 days is lander offer, not night. Peregrine 354 h is day, not night. Cataldo/Mason 354 h darkness is a reference unless this PUG prints that night. |
| Average night electrical load W | NOMINAL **1.0 W/kg**, PEAK **2.5 W/kg** while attached (p.55 Power Services). Deployed payloads take their own power after release (p.55). | Average night load W of the named box. 1.0 / 2.5 W/kg is the lander offer, not a rover night keep-alive. |
| Electronics dissipation W | — | Printed waste heat into the box (W), or OPEN |
| Heater W | — | Printed heater W at the team’s leak, or OPEN |
| T_box | — | Night hold of the node being protected, or OPEN |
| T_env bounds | Lunar surface **−30°C to 80°C** for nominal surface ops; **does not include lunar night** (p.35 Thermal Environment) | Night environment of that node. Do not use the day envelope as night T_env. |
| Radiator area m² | Polar decks / four radiator panels named (p.23, p.25); area not printed | Night radiating area (m²), or OPEN |
| Effective emissivity e* | — | e* of that surface, or OPEN |
| Conductance G, or strut A/L + named alloy | Bus “aluminum alloy” (p.25 Structure); night-path G / A/L + named alloy not printed | Printed G, or A and L plus a named alloy, or OPEN |

Griffin polar payload **625 kg** / **up to 14 days** (p.23) is mass and surface-ops duration, not watt-hours.

## 2. Firefly Blue Ghost — public product page

Source (HTTP 200, 17 Sep 2026): [fireflyspace.com/blue-ghost](https://fireflyspace.com/blue-ghost/) — Payload Resources.

Firefly prints that an unabridged PUG is available after NDA. Public Night Line uses the product page and the flown record only until a public PUG PDF is saved.

| Night Line input | Already printed | Still OPEN / payload must add |
|---|---|---|
| Store Wh nameplate | — | Nameplate or usable night store Wh. Product, wrap-up, NASA release, and LPSC 2026 1958 do not print Wh. |
| Reserve SOC % | — | Printed reserve, or OPEN |
| Charge / discharge η | — | Printed efficiencies, or OPEN |
| Load uncertainty | — | Printed fractional margin, or OPEN |
| Night hours | Product Surface Operations: **«Lunar day + night»** (Payload Resources). Page does not print 354 h. Custom line names “lunar night operations” without hours. | Printed full-night hours if a store is claimed against them. Cataldo/Mason 354 h is a darkness reference, not a Blue Ghost printed night. **Do not** paste BGM1 flown hours here as a PUG night offer (see notes). |
| Average night electrical load W | Product Power: **«> 400 W»** (Payload Resources). LPSC 2026 1958 Vehicle: “With 400 watts of power” (with comms). Peak vs night keep-alive unlabeled. | Average night keep-alive W of the named box. >400 W / 400 W is product/bus, not labeled night keep-alive. Do not treat 5 Wt RHU heat as bus watts. |
| Electronics dissipation W | — | Printed waste heat into the box (W), or OPEN |
| Heater W | — | Printed heater W, or OPEN |
| T_box | — | Night hold of the node, or OPEN |
| T_env bounds | — | Night environment of that node, or OPEN |
| Radiator area m² | — | Night radiating area (m²), or OPEN |
| Effective emissivity e* | — | e* of that surface, or OPEN |
| Conductance G, or strut A/L + named alloy | — | Printed G, or A and L plus a named alloy, or OPEN |

**BGM1 flown hours are not a PUG night store.** Firefly wrap-up (HTTP 200, 17 Sep 2026): operated just over **5 hours** into the lunar night ([wrap-up](https://fireflyspace.com/news/firefly-aerospace-successfully-completes-14-days-of-surface-operations-on-the-moon/)). LPSC 2026 1958 End Of Mission (HTTP 200): five hours after the end of the lunar day; “not designed to survive the cold lunar night” ([1958.pdf](https://www.hou.usra.edu/meetings/lpsc2026/pdf/1958.pdf)). NASA prints “multiple hours,” not 5.0 ([release](https://www.nasa.gov/news-release/nasa-science-continues-after-fireflys-first-moon-mission-concludes/), HTTP 200). That is flown hours vs the product sentence, not a printed night store in watt-hours.

**CS-3 / BGM2: lander off before nightfall.** Firefly BGM2 (HTTP 200): “Blue Ghost will power off prior to lunar nightfall” ([BGM2](https://fireflyspace.com/missions/blue-ghost-mission-2/)). arXiv 2407.07173 §2 (HTTP 200): lander and other payloads permanently shut down at the end of the first solar day ([PDF](https://arxiv.org/pdf/2407.07173)). That is not a lander night-store offer.

## 3. Intuitive Machines

Public lander PUG: **UNVERIFIED** as of 17 September 2026. The Nova-C product page returned HTTP 200 ([intuitivemachines.com/nova-c](https://www.intuitivemachines.com/nova-c)); I did not find a downloadable lander PUG PDF. I do not invent Nova-C night W or Wh.

## 4. Blue Origin MK1

Public PUG: **not opened**. [blueorigin.com/blue-moon/mark-1](https://www.blueorigin.com/blue-moon/mark-1) returned a browser-verification wall (HEAD HTTP 429, 17 Sep 2026). I do not invent MK1 night W or Wh.

## 5. Blank row — payload fills

Named box: ______________________________

Host lander: ______________________________

Signer (human who can lose the box): ______________________________

| Night Line input | cited / OPEN / team_provided | URL + page or figure | Value |
|---|---|---|---|
| Store Wh nameplate | | | |
| Reserve SOC % | | | |
| Charge / discharge η | | | |
| Load uncertainty | | | |
| Night hours | | | |
| Average night electrical load W | | | |
| Electronics dissipation W | | | |
| Heater W | | | |
| T_box | | | |
| T_env bounds | | | |
| Radiator area m² | | | |
| Effective emissivity e* | | | |
| Conductance G, or strut A/L + named alloy | | | |

Copy §1 or §2 for the host lander. Fill this table for the payload. Every number needs a URL plus page or figure, or the cell stays OPEN. The signer owns the outcome. This sheet does not sign.

Shall-language a PUG/ICD can paste: [PUG_SHALL_V1.md](PUG_SHALL_V1.md).

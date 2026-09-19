# Night Line specification v1

SPDX-License-Identifier: MIT

Copyright (c) 2026 Night Line contributors. Permission is hereby granted, free of charge, to any person obtaining a copy of this document, to use, copy, modify, merge, publish, and distribute it, subject to including this notice. Provided “as is”, without warranty.

Written for a thermal engineer at GSFC, JPL, or Firefly. Rows in `LINES.md` were computed on 2026-09-17 from the cited URLs.

## What a Night Line is

A Night Line is one number: the largest average electrical load a named lunar-night box can carry through the printed night on the team’s own printed store, reserves, and efficiencies.

## What a PI uses this for

Night Line does not write the night paragraph. A competing proposal that generates a store from a Survive-the-Night task-order name will lose a reviewer who read the TO briefing, or freeze the wrong mass into Appendix A. Night Line evaluates **this** named box from **this** team’s printed numbers. LIVE / DIE / LIVE_IF. Unprinted knobs stay OPEN. The label is not a claim that the box will live. Job for the PI: [FOR_A_LAB_V1.md](FOR_A_LAB_V1.md). Paste table: [APPENDIX_A_NIGHT_INPUTS_V1.md](APPENDIX_A_NIGHT_INPUTS_V1.md).

## Inputs

Use only printed or team-provided values. Each input is `cited`, `OPEN`, or `team_provided`.

| Input | What it is |
|---|---|
| Store Wh nameplate | Battery energy at 100 % SOC. An allocation for heaters is not nameplate; keep nameplate OPEN and cite the allocation separately. |
| Reserve SOC % | ConOps and/or safe-recharge minimum, as printed. |
| Charge / discharge efficiency | As printed. If both are named and start-of-night is assumed nameplate, apply discharge once on the night. |
| Load uncertainty | Fractional margin on total power load, as printed. |
| Night hours | Printed duration between illuminations. |
| Average night electrical load | Duty-cycled mean watts for the night. Component lists are not an average. |
| Electronics dissipation | Waste heat from electronics into the box (W). |
| Heater | Printed heater watts at the team’s leak, if given. |
| T_box | Night hold temperature of the node you are protecting. |
| T_env bounds | Environment seen by that node. Path-specific zones are not a whole-box sink. |
| Radiator area | Area that radiates at night (m²). |
| Effective emissivity | e* of that radiating surface. |
| Conductance G, or strut A/L + alloy | Night conduction. Prefer a printed G. If A and L are printed, G = k A / L with k from a named alloy. |

## The ladder

1. **Nameplate** — nameplate Wh / night hours. Not a survival line.
2. **Usable** — nameplate × (1 − reserve SOC).
3. **Derated** — usable × discharge efficiency / (1 + load uncertainty).
4. **BREAK** — see below.

If a rung is unprinted, leave it OPEN. Do not fill it from a predecessor design.

## The electrical model

`P_leak = P_cond + P_rad` (Fourier conduction + radiation).

`P_elec = max(P_electronics, P_leak)`

`E_night = P_elec × night hours`

Reason (ICES 2025 Fig. 14 heat balance): at night the box is one thermal node. Heat that leaves is the leak. Electronics dissipation is already part of that heat. The heater only makes up `P_leak − P_electronics` when the leak is larger. Battery draw is therefore the larger of electronics watts and leak watts, not the sum. Do not add electronics on top of the leak.

## BREAK definition

Hold every other input fixed. Move one knob until the cited store is exhausted at **exactly** the printed night hours. That single-knob value is the BREAK. Report the knob, the value, and the hours (must equal night hours).

## OPEN rule

Unprinted → declared bracket. Show both corners. Never a middle.

## Labels

The label is on declared corners only. It is not a claim that the box will live.

- `LIVE` — every declared corner survives the printed night hours. Print the worst-corner margin (store − E_night at that corner). Write `edge` when that margin is ≤ 2 % of store.
- `DIE` — every declared corner fails the printed night hours.
- `BRACKET` — declared corners disagree. Show both. Never a middle.
- `LIVE_IF_<knob>_BELOW` — a knob has no printed upper bound. The line is the BREAK value on the team’s own reserve / efficiency / uncertainty rungs.
- `LINE_OPEN_TWO_KNOBS` — store Wh and average night load W are both unprinted. Print the identity `usable_Wh / night hours = load W` and an **ASSUMED**-labelled example table. Do not pick a store. Do not print `LIVE`.
- `LIVE_IF_STORE_ABOVE` — average night load W is printed and store Wh is not. Print the identity `P_night_W × night hours = nameplate store Wh`. Battery mass in kg is not watt-hours. An **ASSUMED** 30 % reserve row may show a higher nameplate; it is not a picked store. Do not print `LIVE`.
- `CLAIM_VS_WITNESS` — a flown night against a public product sentence. Print flown hours after sunset vs Cataldo/Mason 354 h as a **duration gap**. Store Wh and energy_wh stay OPEN. Do not invent watt-hours. Do not print `DIE` on invented Wh. Peak vs night keep-alive stays OPEN if unlabeled.
- `HEAT_VS_BONUS` — printed thermal watts (RHU heat) vs a NASA-paid full-night radioisotope+transmit bonus. Heat is not electrical bus watts. Electrical keep-alive and store stay OPEN. Do not mint watt-hours from heat × night hours. Do not print `LIVE` from 5 Wt.

## Cite rule

Every number: URL + page or figure. Derived kelvin from printed celsius is `273.15 + T_C` only. NIST k(T): fit by **integral** over the temperature interval actually used; the material **temper must match** the named alloy. No coupon from us.

## Verifier protocol

A second person recomputes from the cited URLs, checks each URL still resolves, records sha256 of the source bytes they used, and will not print `LIVE` when a knob has no printed upper bound (use `LIVE_IF_<knob>_BELOW`). When store and load are both OPEN, print `LINE_OPEN_TWO_KNOBS`, not `LIVE`. When load is printed and store is OPEN, print `LIVE_IF_STORE_ABOVE`, not `LIVE`; do not convert battery kg to Wh. When a flown night is set against a public product sentence and store Wh is OPEN, print `CLAIM_VS_WITNESS`, not `DIE` on invented Wh. When printed watts are thermal (RHU heat) and electrical keep-alive is OPEN, print `HEAT_VS_BONUS`; do not mint watt-hours from heat × night hours. `LIVE` on declared corners still prints worst-corner margin; `edge` when that margin is ≤ 2 % of store.

## What Night Line is not

Not a replacement for a thermal model. Not a flight sign-off. The label is on declared corners only; it is not a claim that the box will live. The human who can lose the box signs.

## Reproduce

```text
night-line --all
```

No measurement by us; all values printed by the team or NIST.

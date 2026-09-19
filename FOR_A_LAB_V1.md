# Night Line — what a lab uses this for

SPDX-License-Identifier: MIT

Copyright (c) 2026 Night Line contributors. Permission is hereby granted, free of charge, to any person obtaining a copy of this document, to use, copy, modify, merge, publish, and distribute it, subject to including this notice. Provided “as is”, without warranty.

The difference is not that Night Line calculates faster. **Night Line does not write a night paragraph.**

The other suite competing for the same PRISM, DALI, or CLPS payload seat will generate “we survive the night” from the task-order name. That sentence is fast. It dies when a hostile reviewer who read the Survive-the-Night briefing, or a lander thermal, asks for a watt-hour.

Night Line evaluates declared knobs on **your** named box: night W, store Wh, hours — `cited` or `OPEN`. Three verdicts: **LIVE**, **DIE**, **LIVE_IF**. OPEN stays OPEN. It cannot return a watt you did not print. A wrong cited number can still LIVE. Honesty prevents mint, not measurement error.

You win the grant and keep the mission seat if your Appendix A is **faster to freeze, more precise than the TO name, and recomputable by a stranger**. It is not a thermal model. It is not a seventh energy line.

## The job

A university PI, deputy PI, or payload thermal lead is scored on science and on implementation risk. Survive-the-Night in a call is a discriminator. The human who can lose the box wants three things the other suite also wants:

1. **The grant.** A false store that wins the paper and dies at CDR is not a win.
2. **The mission seat.** Appendix A / PUG / ICD freeze. First team with cited knobs looks ready. First team with a TO-name store looks ready until the lander asks for Wh.
3. **To beat the other suite.** They do not have an independent reconstruction of *your* box. They have a brochure number and a spreadsheet only the RA can open.

## What they already have — and what still loses the review

| They already have | That is not enough |
|---|---|
| Thermal Desktop / a MEL | Not the grant paragraph. Not Appendix A. |
| The TO name “Survive the Night” | Not a watt-hour. |
| A lunar-day ops window (hours of sunlight) | Not Cataldo night unless the page labels darkness. |
| “No night operations” in a threshold mission | Not keep-alive W. |
| A spreadsheet only the RA can open | A hostile reviewer cannot recompute it. Neither can the lander. |

What Night Line is: one number — the largest average electrical load the named box can carry through the printed night on the team’s own printed store, reserves, and efficiencies — plus every input marked `cited` / `OPEN` / `team_provided`. LIVE / DIE / LIVE_IF sit on declared corners. OPEN stays OPEN.

- **Faster:** clone; `night-line appendix-a` writes the table on your disk; paste [NL-A1–A4](APPENDIX_A_NIGHT_INPUTS_V1.md) while Appendix A is still open.
- **More precise:** do not mix TO name, lunar-day hours, and night store.
- **More reliable:** a second person recomputes from the cited URLs. A reviewer who read Jenkins cannot kill OPEN cells you named. They can kill a store you invented from the TO name.

## How you use it this week

There is no login and no file drop. Unpublished thermal, ICD, and night budgets stay in your lab ([15 CFR 734.7](https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C/part-734/section-734.7)).

1. **Public print.** `git clone` this repo. `night-line --all` and `night-line witness-map` do not upload.
2. **Appendix A still open.** Paste [APPENDIX_A_NIGHT_INPUTS_V1.md](APPENDIX_A_NIGHT_INPUTS_V1.md). On your machine: `night-line appendix-a --ride dimple_cp32` (worked example: DIMPLE on CP-32 — 348 h lunar day / 280 h ops / Survive-the-Night TO name is not the store). Or open a GitHub issue from the Night Line inputs template.
3. **One number that already has a page.** `night-line close` — value + URL + page or figure. Method: [CLOSE_PROTOCOL_V1.md](CLOSE_PROTOCOL_V1.md).
4. **Paid reconstruction.** Attach [PO_SCOPE_V1.md](PO_SCOPE_V1.md) to the grant as professional services. The human who can lose the box signs the line. This repository does not.

Do not letter from this page. **MEASURED=false**. Specification: [NIGHT_LINE_SPEC_V1.md](NIGHT_LINE_SPEC_V1.md).

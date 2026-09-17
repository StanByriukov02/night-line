# Night Line — close protocol v1

SPDX-License-Identifier: MIT

Copyright (c) 2026 Night Line contributors. Permission is hereby granted, free of charge, to any person obtaining a copy of this document, to use, copy, modify, merge, publish, and distribute it, subject to including this notice. Provided “as is”, without warranty.

I, Stanislav Byriukov, close one OPEN input only when a number arrives with a URL and a page or figure. I write a dated `LINE.md` and `INPUTS.csv`. I do not rewrite public `LINES.md` from this command. I do not mint a number from email prose.

Method: [NIGHT_LINE_SPEC_V1.md](NIGHT_LINE_SPEC_V1.md). Inputs the PI supplies: [PO_SCOPE_V1.md](PO_SCOPE_V1.md) §3.

## What `team_provided` means

`team_provided` is one number the team supplies, with a URL and a page or figure (for example `Fig. 3` or `p.12`). It is not `cited` until that page exists. It is not an email sentence. It is not a predecessor design.

URL and page or figure are both required. Missing URL → the tool REFUSES. Missing page → the tool REFUSES. An unparsable value or an unknown input name → the tool REFUSES.

## OPEN stays OPEN

One overlay fills one named input. Every other unprinted knob stays OPEN. I do not fill a hole from a sibling box or from a DALI / TRL-6 predecessor.

## Synthetic is not Benna

A test fixture may overlay a made-up radiator area on a copy of LEMS-A3 so the command can be proven. That overlay is labelled SYNTHETIC. It is not Mehdi Benna’s printed number. It is not a LEMS-A3 flight print. Do not publish it as theirs.

## Public row

The public LEMS-A3 row in `LINES.md` stays `LIVE (edge)` until a real team page exists and the operator accepts a dated public row. This command writes only under `--out`. It has no `--record` flag. Recording a public row is a later human act.

## Reproduce

```text
night-line close --box lems-a3 --input A_rad_m2 --value <float> --url <url> --page "Fig. X" --out <dir>
```

Writes `LINE.md`, `INPUTS.csv`, and `RECEIPT.txt` under `--out` (default `out/close_<box>_<input>/`). Does not write `LINES.md`.

No measurement by me; all values printed by the team or NIST, or one `team_provided` number with a page.

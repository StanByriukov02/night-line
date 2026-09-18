# Night Line — shall language for a PUG / ICD

SPDX-License-Identifier: MIT

Copyright (c) 2026 Night Line contributors. Permission is hereby granted, free of charge, to any person obtaining a copy of this document, to use, copy, modify, merge, publish, and distribute it, subject to including this notice. Provided “as is”, without warranty.

Paste the block below into a Payload Users Guide appendix or an ICD kickoff. Inputs and method: [PUG_NIGHT_LINE_INPUTS_V1.md](PUG_NIGHT_LINE_INPUTS_V1.md), [NIGHT_LINE_SPEC_V1.md](NIGHT_LINE_SPEC_V1.md). Public record: [github.com/StanByriukov02/night-line](https://github.com/StanByriukov02/night-line).

The human who can lose the named box signs. This page does not.

```
NL-1  The payload shall declare Night Line inputs for the named box: store Wh
      (nameplate), reserve SOC, charge/discharge efficiency, load uncertainty,
      night hours, average night electrical load W, electronics dissipation W,
      heater W, T_box, T_env bounds, radiator area, e*, and conductance G or
      strut A/L with a named alloy. Each value shall carry a URL and a page or
      figure, or the cell shall remain OPEN.

NL-2  A day thermal envelope shall not be used as night T_env.

NL-3  Lander offered W/kg (or a product bus watt) shall not be used as the
      payload's night store Wh or as night keep-alive W unless the page labels
      it that way.

NL-4  Flown hours after sunset shall not be used as a PUG night-store offer.

NL-5  Printed thermal watts (RHU heat) shall not be used as electrical bus watts.

NL-6  An unprinted knob shall stay OPEN. It shall not be filled from a
      predecessor design, a sibling box, or a middle of a bracket.

NL-7  The Night Line label (LIVE / DIE / LIVE_IF / CLAIM_VS_WITNESS /
      HEAT_VS_BONUS / LINE_OPEN_TWO_KNOBS / LIVE_IF_STORE_ABOVE) shall be
      computed only from declared corners. It is not a claim that the box
      will live.

NL-8  The human who can lose the named box shall sign the line. The
      reconstruction does not sign.
```

Copy §5 of [PUG_NIGHT_LINE_INPUTS_V1.md](PUG_NIGHT_LINE_INPUTS_V1.md) for the blank table. Unpublished lander ICD numbers stay off this page until the buyer classifies them.

"""Public-ship gate for github.com/StanByriukov02/night-line.

A root file does not go public because an F-cell wrote it.
Class → allow or refuse. Cabin tokens never ship. Offer pages need --go-offer.

Exit 0 only when the tree is allowed to push.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# What a stranger is allowed to clone without a human GO.
RECORD = {
    "LICENSE",
    "LINES.md",
    "NIGHT_LINE_SPEC_V1.md",
    "README.md",
    "night_line_schema_v1.json",
    "pyproject.toml",
    "MANIFEST.in",
    ".gitattributes",
    ".gitignore",
}

METHOD = {
    "PUG_NIGHT_LINE_INPUTS_V1.md",
    "PUG_SHALL_V1.md",
    "WITNESS_CLOCK_FLIP_V1.md",
    "CLOSE_PROTOCOL_V1.md",
    "BREAK_SURFACE_LEMS_V1.md",
    "MEASURE_LEMS_V1.md",
    "WITNESS_MAP_V1.md",
    "PUBLIC_SHIP.md",
    "APPENDIX_A_NIGHT_INPUTS_V1.md",
}

HONESTY = {
    "TWO_COURTS_LUSEE_V1.md",
    "TWO_COURTS_LEMS_V1.md",
}

# Money, W-8BEN, bid/TO language. Not auto-push.
OFFER = {
    "PO_SCOPE_V1.md",
    "TO_NIGHT_APPENDIX_V1.md",
    "EXPORT_AP_MEMO_V1.md",
}

SKIP_DIRS = {
    ".git",
    ".github",
    ".pytest_cache",
    "__pycache__",
    "night_line",
    "sources",
    "tests",
    "tools",
    "out",
}

# Dual / leftover / yard / F-cells / vault — cabin. Not their package.
CABIN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bDual-hostile\b"), "Dual cabin"),
    (re.compile(r"\bDual\b"), "Dual cabin"),
    (re.compile(r"\byard\b", re.I), "yard cabin"),
    (re.compile(r"hardware_atom"), "monorepo path"),
    (re.compile("dogfood" + "_platform"), "kitchen import"),
    (re.compile(r"docs/agent_workflow"), "vault path"),
    (re.compile(r"\bFLOOR\.txt\b"), "plant file"),
    (re.compile(r"\bTABU\b"), "internal TABU"),
    (re.compile(r"\bTHINK_L0\b"), "agent kernel"),
    (re.compile(r"PRODUCT_WORKS"), "market mint"),
    (re.compile(r"STARSHIP_READY"), "north-star mint"),
    (re.compile(r"\bF3[0-9]{2}\b"), "internal F-cell"),
    (re.compile(r"leftover\s+−?-?[0-9]"), "Dual leftover number"),
    (re.compile(r"\bleftover\b", re.I), "leftover cabin"),
    (re.compile(r"−8218"), "yard DIE leftover"),
    (re.compile(r"-8218"), "yard DIE leftover"),
]

OFFER_BODY: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"W-8BEN"), "W-8BEN offer"),
    (re.compile(r"\bGSA\b"), "GSA rate sheet"),
    (re.compile(r"not-to-exceed|\bNTE\b"), "rate NTE"),
    (re.compile(r"I am not a CLPS offeror"), "bid-liability sentence"),
    (re.compile(r"\bSeller:\s"), "seller line"),
]


def classify_name(name: str) -> str:
    if name in RECORD:
        return "record"
    if name in METHOD:
        return "method"
    if name in HONESTY:
        return "honesty"
    if name in OFFER:
        return "offer"
    return "unknown"


def scan_cabin(text: str) -> list[str]:
    hits: list[str] = []
    for i, line in enumerate(text.splitlines(), 1):
        for pat, why in CABIN_PATTERNS:
            if pat.search(line):
                hits.append(f"{i}:{why}: {line.strip()[:100]}")
                break
    return hits


def scan_offer_body(text: str) -> list[str]:
    hits: list[str] = []
    for i, line in enumerate(text.splitlines(), 1):
        for pat, why in OFFER_BODY:
            if pat.search(line):
                hits.append(f"{i}:{why}: {line.strip()[:100]}")
                break
    return hits


def inspect_root(root: Path | None = None, *, go_offer: bool = False) -> dict[str, Any]:
    base = Path(root) if root is not None else ROOT
    files: list[dict[str, Any]] = []
    fails: list[str] = []
    for path in sorted(base.iterdir(), key=lambda p: p.name.lower()):
        if path.name in SKIP_DIRS or path.name.startswith("."):
            if path.name in {".gitattributes", ".gitignore"}:
                pass
            else:
                continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".json", ".toml", ".in", ".txt"} and path.name not in RECORD:
            # LICENSE has no suffix
            if path.name != "LICENSE":
                continue
        kind = classify_name(path.name)
        rec: dict[str, Any] = {
            "file": path.name,
            "class": kind,
            "ok": True,
            "hits": [],
        }
        text = ""
        if path.suffix.lower() in {".md", ".txt", ".json", ".toml", ".in"} or path.name == "LICENSE":
            text = path.read_text(encoding="utf-8", errors="replace")
        cabin = scan_cabin(text) if text else []
        if cabin:
            rec["ok"] = False
            rec["hits"].extend(cabin)
            fails.append(f"{path.name}: CABIN")
        if kind == "unknown":
            rec["ok"] = False
            rec["hits"].append("0:unknown root file — not on the public allowlist")
            fails.append(f"{path.name}: UNKNOWN")
        if kind == "offer":
            offer_hits = scan_offer_body(text) if text else ["offer filename"]
            rec["hits"].extend([h for h in offer_hits if h not in rec["hits"]])
            if not go_offer:
                rec["ok"] = False
                fails.append(f"{path.name}: OFFER needs operator GO")
        files.append(rec)
    ok = not fails
    return {
        "schema": "night_line_public_ship_v1",
        "root": str(base),
        "go_offer": go_offer,
        "ok": ok,
        "fail": fails,
        "files": files,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="night-line ship-gate")
    p.add_argument("--root", type=Path, default=None)
    p.add_argument(
        "--go-offer",
        action="store_true",
        help="operator GO: allow PO_SCOPE / TO appendix. Still refuses cabin.",
    )
    args = p.parse_args(argv)
    doc = inspect_root(args.root, go_offer=args.go_offer)
    print(json.dumps(doc, indent=2, ensure_ascii=False))
    if not doc["ok"]:
        print("PUBLIC_SHIP FAIL", file=sys.stderr)
        for f in doc["fail"]:
            print(f, file=sys.stderr)
        return 1
    print("PUBLIC_SHIP PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

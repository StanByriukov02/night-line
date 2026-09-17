"""Redact e-mail addresses in saved source copies under sources/ and refresh sha fields in SOURCE.json.

Usage: python tools/redact_sources.py sources
Saved pages are kept for number provenance only; personal addresses are not part of a Night Line.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

EMAIL = re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TEXT_EXT = {".txt", ".html", ".htm", ".md"}


def main(root: Path) -> int:
    changed = []
    for source_json in root.rglob("SOURCE.json"):
        folder = source_json.parent
        rec = json.loads(source_json.read_text(encoding="utf-8"))
        touched = False
        for f in folder.iterdir():
            if f.name == "SOURCE.json" or not f.is_file() or f.suffix.lower() not in TEXT_EXT:
                continue
            raw = f.read_bytes()
            redacted, n = EMAIL.subn(b"[email-redacted]", raw)
            if n:
                f.write_bytes(redacted)
                touched = True
                changed.append((f.relative_to(root).as_posix(), n))
        if not touched:
            continue
        rec["redacted_personal_email"] = True
        for key in ("sha256_by_file", "saved_sha256"):
            if key in rec and isinstance(rec[key], dict):
                for name in list(rec[key].keys()):
                    p = folder / name
                    if p.is_file():
                        rec[key][name] = hashlib.sha256(p.read_bytes()).hexdigest()
        primary = rec.get("filename") or rec.get("extract")
        if primary and (folder / primary).is_file() and rec.get("sha256"):
            rec["sha256"] = hashlib.sha256((folder / primary).read_bytes()).hexdigest()
        source_json.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for path, n in changed:
        print(f"redacted {path} ({n})")
    print(f"files_changed {len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "sources")))

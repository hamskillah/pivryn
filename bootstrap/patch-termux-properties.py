#!/usr/bin/env python3
"""Pin a Termux source build to a dedicated Android application ID."""
from pathlib import Path
import re

PATTERN = re.compile(r'(?m)^TERMUX_APP__PACKAGE_NAME="com\.termux"$')
CUSTOM = 'TERMUX_APP__PACKAGE_NAME="com.pivryn"'

def patch(text: str, package: str) -> str:
    if package != "com.pivryn":
        raise ValueError("Unexpected Pivryn application ID")
    if text.count(CUSTOM) == 1 and not PATTERN.search(text):
        return text
    if len(PATTERN.findall(text)) != 1:
        raise ValueError("Upstream Termux properties changed; review before proceeding")
    return PATTERN.sub(CUSTOM, text, count=1)

def main() -> None:
    # Parse the intentionally tiny command format strictly, including mode.
    import sys
    if len(sys.argv) not in (3, 4) or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit("usage: patch-termux-properties.py --check|--apply <path> [com.pivryn]")
    path = Path(sys.argv[2])
    package = sys.argv[3] if len(sys.argv) == 4 else "com.pivryn"
    source = path.read_text(encoding="utf-8")
    result = patch(source, package)
    if sys.argv[1] == "--apply":
        path.write_text(result, encoding="utf-8")
    print("Verified Termux source package identity: com.pivryn")

if __name__ == "__main__":
    main()

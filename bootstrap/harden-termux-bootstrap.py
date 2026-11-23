#!/usr/bin/env python3
"""Guard an unsafe cleanup branch in a pinned upstream Termux bootstrap builder.

The pinned build-bootstraps.sh uses -f to run:
    rm -f "$TERMUX_BUILT_PACKAGES_DIRECTORY_FOR_ARCH"/*
but this variable is never initialized in that script/buildarch helper.
An empty value expands to /*. Enforce an invariant even if -f is reintroduced.
"""
from pathlib import Path
import sys

OLD = 'rm -f "$TERMUX_BUILT_PACKAGES_DIRECTORY_FOR_ARCH"/*'
NEW = '''if [[ -z "${TERMUX_BUILT_PACKAGES_DIRECTORY_FOR_ARCH:-}" ||
      "$TERMUX_BUILT_PACKAGES_DIRECTORY_FOR_ARCH" == "/" ]]; then
    echo "ERROR: unsafe Termux cleanup directory; aborting" >&2
    exit 95
  fi
  rm -f "$TERMUX_BUILT_PACKAGES_DIRECTORY_FOR_ARCH"/*'''

def patch(text: str) -> str:
    if NEW in text and OLD not in text.replace(NEW, ""):
        return text
    if text.count(OLD) != 1:
        raise ValueError("Termux source cleanup changed; aborting for review")
    return text.replace(OLD, NEW, 1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: harden-termux-bootstrap.py <upstream-build-bootstraps.sh>")
    p = Path(sys.argv[1])
    p.write_text(patch(p.read_text()))
    print("Upstream Termux cleanup is guarded against an empty directory")

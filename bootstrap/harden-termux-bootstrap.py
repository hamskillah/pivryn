#!/usr/bin/env python3
"""Guard pinned upstream Termux bootstrap generation and package drift.

Pinned upstream builder has two problems:
- In force mode, an unset cleanup path expands to a root glob.
- Its base list still calls source recipe bzip2, now named libbz2.
The libbz2 recipe emits a bzip2 subpackage; libcurl emits a curl subpackage.
"""
from pathlib import Path
import re
import sys

OLD = 'rm -f "$TERMUX_BUILT_PACKAGES_DIRECTORY_FOR_ARCH"/*'
NEW = '''if [[ -z "${TERMUX_BUILT_PACKAGES_DIRECTORY_FOR_ARCH:-}" ||
      "$TERMUX_BUILT_PACKAGES_DIRECTORY_FOR_ARCH" == "/" ]]; then
    echo "ERROR: unsafe Termux cleanup directory; aborting" >&2
    exit 95
  fi
  rm -f "$TERMUX_BUILT_PACKAGES_DIRECTORY_FOR_ARCH"/*'''
OLD_BZIP2 = 'PACKAGES+=("bzip2")'
NEW_BZIP2 = 'PACKAGES+=("libbz2")'

def patch(text: str) -> str:
    if NEW in text and OLD not in text.replace(NEW, ""):
        pass
    elif text.count(OLD) == 1:
        text = text.replace(OLD, NEW, 1)
    else:
        raise ValueError("Termux source cleanup changed; review before building")

    if NEW_BZIP2 in text and OLD_BZIP2 not in text:
        return text
    if text.count(OLD_BZIP2) != 1:
        raise ValueError("Termux bzip2 recipe mapping changed; review upstream")
    return text.replace(OLD_BZIP2, NEW_BZIP2, 1)


def validate_sources(builder: str, source_root: Path, additional: str) -> tuple[str, ...]:
    core = re.findall(r'(?m)^\s*PACKAGES\+=\("([^"$]+)"\)', builder)
    extra = additional.split(",")
    if not core or not extra or any(not x or not re.fullmatch(r"[a-z0-9.+-]+", x) for x in extra):
        raise ValueError("Malformed package list")
    required = tuple(dict.fromkeys(core + extra))
    missing = [name for name in required
               if not (source_root / "packages" / name / "build.sh").is_file()]
    if missing:
        raise ValueError("Pinned Termux packages have no source recipe: " + ", ".join(missing))
    return required


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: harden-termux-bootstrap.py <upstream-builder.sh> <comma-separated-extra-packages>"
        )
    p = Path(sys.argv[1])
    patched = patch(p.read_text())
    checked = validate_sources(patched, p.parent.parent, sys.argv[2])
    p.write_text(patched)
    print(f"Verified {len(checked)} source recipes; guarded cleanup, mapped bzip2 to libbz2")

#!/usr/bin/env python3
"""Verify a source-built Termux bootstrap before linking it into Pivryn."""
import sys
import zipfile
from pathlib import Path

OLD = b"/data/data/com.termux/files"
NEW = b"/data/data/com.pivryn/files"

def verify(zip_path: Path, package: str) -> dict:
    if package != "com.pivryn":
        raise ValueError("Wrong application ID")
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        if len(names) != len(archive.infolist()):
            raise ValueError("Duplicate archive entries")
        required = {"bin/bash", "bin/node", "bin/npm", "bin/python", "bin/git",
                    "SYMLINKS.txt"}
        # In Termux symlinks are represented in SYMLINKS.txt.
        symlinks = archive.read("SYMLINKS.txt") if "SYMLINKS.txt" in names else b""
        present = names | {line.rsplit(b"\xe2\x86\x90", 1)[-1].lstrip(b"./").decode("utf-8", errors="replace")
                           for line in symlinks.splitlines()}
        missing = required - present
        if missing:
            raise ValueError(f"Incomplete custom bootstrap (missing {sorted(missing)})")
        occurrences = 0
        for info in archive.infolist():
            if info.is_dir():
                continue
            if info.filename.startswith("/") or ".." in Path(info.filename).parts:
                raise ValueError(f"Unsafe archive entry {info.filename}")
            data = archive.read(info)
            if OLD in data:
                raise ValueError(f"Official Termux prefix embedded in {info.filename}")
            occurrences += data.count(NEW)
        if occurrences == 0:
            raise ValueError("Custom package prefix not detected in bootstrap")
        return {"files": len(names), "custom_prefix_references": occurrences}

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: verify-custom-prefix.py <archive.zip> com.pivryn")
    result = verify(Path(sys.argv[1]), sys.argv[2])
    print(f"Verified custom-prefix bootstrap: {result}")

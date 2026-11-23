#!/data/data/com.termux/files/usr/bin/python3
"""Pin pi-agent-dashboard's bundled server to loopback on Android.

This is an intentionally minimal, fail-closed patch against pinned dashboard
v0.5.3. Never rely on CORS alone to protect a local agent server.
"""
from __future__ import annotations

import sys
from pathlib import Path


OLD = 'await fastify.listen({ port: config.port, host: "0.0.0.0" });'
NEW = 'await fastify.listen({ port: config.port, host: "127.0.0.1" });'


def patch(file: Path) -> bool:
    if not file.is_file():
        return False
    source = file.read_text(encoding="utf-8")
    if NEW in source and OLD not in source:
        return True  # idempotent
    if source.count(OLD) != 1 or NEW in source:
        return False  # fail on unrecognized upstream version / source changes
    file.write_text(source.replace(OLD, NEW), encoding="utf-8")
    return NEW in file.read_text(encoding="utf-8")


def discover(prefix: Path) -> list[Path]:
    global_modules = prefix / "lib/node_modules"
    return [
        global_modules / "@blackbelt-technology/pi-agent-dashboard/node_modules"
        / "@blackbelt-technology/pi-dashboard-server/src/server.ts",
        global_modules / "@blackbelt-technology/pi-dashboard-server/src/server.ts",
    ]


if __name__ == "__main__":
    # An explicit file argument is solely for reproducible tests and audits.
    # Runtime calls this without arguments and uses installed package discovery.
    candidates = (
        [Path(sys.argv[1])]
        if len(sys.argv) == 2
        else discover(Path(__import__("os").environ.get("PREFIX", "")))
    )
    matches = [file for file in candidates if file.is_file()]
    if len(matches) != 1 or not patch(matches[0]):
        print("ERROR: Cannot verify dashboard loopback binding. Refusing to start.",
              file=sys.stderr)
        sys.exit(1)
    print("Verified pi-dashboard binds HTTP on 127.0.0.1")

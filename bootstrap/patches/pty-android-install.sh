#!/data/data/com.termux/files/usr/bin/bash
# Optional Pivryn Android ARM64 native PTY adapter for upstream pi-agent-dashboard.
# Package: @mmmbuto/node-pty-android-arm64@1.1.2 (MIT).
# Restore existing node-pty on any failure; never leave dashboard unimportable.
set -euo pipefail

NODE_PTY_PKG="$PREFIX/lib/node_modules/@blackbelt-technology/pi-agent-dashboard/node_modules/node-pty"
ARCHIVE="$PREFIX/etc/pocket-pi/vendor/node-pty-android-arm64-1.1.2.tgz"
EXPECTED="dd5fa0cff041cd403bcf860caa6effcad0fc1d27472cbdbacc06f44719dfac95"

if [ ! -d "$NODE_PTY_PKG" ] || [ ! -f "$ARCHIVE" ]; then
  echo "Pivryn PTY: dashboard dependency or verified artifact unavailable"
  exit 2
fi
if [ "$(uname -m)" != "aarch64" ]; then
  echo "Pivryn PTY: unsupported architecture; retaining original fallback"
  exit 3
fi
printf '%s  %s\n' "$EXPECTED" "$ARCHIVE" | sha256sum -c - >/dev/null || {
  echo "Pivryn PTY: artifact digest mismatch"
  exit 4
}
mkdir -p "$PREFIX/tmp"
STAGING="$(mktemp -d "$PREFIX/tmp/pivryn-pty.XXXXXXXX")"
BACKUP="$STAGING/original-node-pty"
rollback() {
  if [ -d "$BACKUP" ]; then
    rm -rf "$NODE_PTY_PKG"
    mv "$BACKUP" "$NODE_PTY_PKG"
  fi
  rm -rf "$STAGING"
}
trap rollback EXIT
tar -xzf "$ARCHIVE" -C "$STAGING" --no-same-owner
test -f "$STAGING/package/lib/index.js"
test -f "$STAGING/package/prebuilds/android-arm64/pty.node"
test -f "$STAGING/package/LICENSE"
mv "$NODE_PTY_PKG" "$BACKUP"
mv "$STAGING/package" "$NODE_PTY_PKG"
chmod 700 "$NODE_PTY_PKG/prebuilds/android-arm64/pty.node"

# Do a genuine PTY spawn as well as native require(): a bare import can succeed
# while shell launch fails due to missing shared libraries or Android policies.
if ! node - "$NODE_PTY_PKG" <<'JS'
const pty = require(process.argv[2]);
const fs = require("node:fs");
const shell = process.env.PREFIX + "/bin/sh";
if (!fs.existsSync(shell)) process.exit(19);
let output = "";
let finished = false;
const timer = setTimeout(() => {
  if (!finished) {
    try { term.kill(); } catch {}
    process.exit(20);
  }
}, 7000);
let term;
try {
  term = pty.spawn(shell, ["-c", "printf PIVRYN_PTY_SMOKE_OK"], {
    name: "xterm-256color", cols: 80, rows: 24,
    cwd: process.env.HOME, env: process.env,
  });
} catch (e) {
  console.error("PTY spawn failed:", e.message);
  process.exit(21);
}
term.onData(data => { output += data; });
term.onExit(() => {
  finished = true;
  clearTimeout(timer);
  process.exit(output.includes("PIVRYN_PTY_SMOKE_OK") ? 0 : 22);
});
JS
then
  echo "Pivryn PTY: native smoke failed; restoring dashboard's original binding"
  exit 5
fi
# Keep original only until verified; rollback trap now removes staging.
rm -rf "$BACKUP"
echo "Pivryn PTY: installed and smoke-tested Android PTY binding"

#!/usr/bin/env bash
# Build a Termux bootstrap zip pre-populated with Pocket Pi payload:
#   - postinstall script + npm/pip package lists
#   - the hermes-evolve patch
#   - a "skel" directory mirroring the user's $HOME, copied into place by
#     postinstall on first launch (Termux's bootstrap zip extracts only into
#     $PREFIX, never into $HOME, so HOME content has to be seeded from skel).
#
# Output: bootstrap/dist/bootstrap-${ARCH}.zip
#
# Usage:
#   ./build-bootstrap.sh aarch64       # default phones
set -euo pipefail

ARCH="${1:-aarch64}"
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
WORK="$HERE/work/$ARCH"
DIST="$HERE/dist"
mkdir -p "$WORK" "$DIST"

case "$ARCH" in
  aarch64|arm|i686|x86_64) ;;
  *) echo "unsupported arch: $ARCH (expected aarch64|arm|i686|x86_64)" >&2; exit 1 ;;
esac

echo "==> Fetching Termux base bootstrap for $ARCH"
# Tested Termux binary release, not the moving "latest".
TERMUX_BOOTSTRAP_URL="${TERMUX_BOOTSTRAP_URL:-https://github.com/termux/termux-packages/releases/download/bootstrap-2026.11.15-r1+apt.android-7/bootstrap-${ARCH}.zip}"
if [ "$ARCH" = "aarch64" ]; then
  TERMUX_BOOTSTRAP_SHA256="${TERMUX_BOOTSTRAP_SHA256:-388acf91cc247e7062d80cd8aa791fe72f360515fb78dc54ff45742120facae7}"
fi
if [ ! -f "$WORK/base.zip" ]; then
  curl --fail --location --retry 3 --retry-delay 2     --output "$WORK/base.zip.tmp" "$TERMUX_BOOTSTRAP_URL"
  mv "$WORK/base.zip.tmp" "$WORK/base.zip"
fi
if ! unzip -tq "$WORK/base.zip" >/dev/null; then
  echo "ERROR: invalid Termux bootstrap ZIP; delete $WORK/base.zip and retry" >&2
  exit 1
fi
if [ -n "${TERMUX_BOOTSTRAP_SHA256:-}" ]; then
  echo "$TERMUX_BOOTSTRAP_SHA256  $WORK/base.zip" | sha256sum -c -
fi

# The base zip's contents map directly to $PREFIX. We unpack it into a staging
# tree, layer our payload at the right paths inside that tree, then re-zip.
rm -rf "$WORK/prefix"
mkdir -p "$WORK/prefix"
( cd "$WORK/prefix" && unzip -q "$WORK/base.zip" )

echo "==> Layering Pocket Pi payload"

# 1. Pocket Pi metadata + scripts go under $PREFIX/etc/pocket-pi/
mkdir -p "$WORK/prefix/etc/pocket-pi"
cp "$HERE/postinstall.sh"   "$WORK/prefix/etc/pocket-pi/postinstall.sh"
cp "$HERE/packages.txt"     "$WORK/prefix/etc/pocket-pi/packages.txt"
cp "$HERE/npm-packages.txt" "$WORK/prefix/etc/pocket-pi/npm-packages.txt"
cp "$HERE/pip-packages.txt" "$WORK/prefix/etc/pocket-pi/pip-packages.txt"
cp -R "$HERE/patches"       "$WORK/prefix/etc/pocket-pi/patches"
chmod +x "$WORK/prefix/etc/pocket-pi/postinstall.sh"
chmod +x "$WORK/prefix/etc/pocket-pi/patches/"*.sh

# Android ARM64 node-pty adapter (MIT). The artifact is pinned by both version
# and checksum and carries its own license. On-device we run a real PTY smoke
# and fall back to the upstream stub if the binary cannot be loaded.
if [ "$ARCH" = "aarch64" ]; then
  PTY_VERSION="1.1.2"
  PTY_SHA256="dd5fa0cff041cd403bcf860caa6effcad0fc1d27472cbdbacc06f44719dfac95"
  PTY_URL="https://registry.npmjs.org/@mmmbuto/node-pty-android-arm64/-/node-pty-android-arm64-$PTY_VERSION.tgz"
  mkdir -p "$WORK/prefix/etc/pocket-pi/vendor"
  PTY_TGZ="$WORK/prefix/etc/pocket-pi/vendor/node-pty-android-arm64-$PTY_VERSION.tgz"
  if [ ! -f "$PTY_TGZ" ]; then
    curl --fail --location --retry 3 --retry-delay 2 \
      --output "$PTY_TGZ.tmp" "$PTY_URL"
    mv "$PTY_TGZ.tmp" "$PTY_TGZ"
  fi
  echo "$PTY_SHA256  $PTY_TGZ" | sha256sum -c -
  tar -tzf "$PTY_TGZ" >/dev/null
fi

# 2. HOME skel — copied into the user's $HOME on first launch by postinstall.
# No api-key placeholders: provider keys are user-supplied through the
# dashboard's settings UI on first run. Pre-creating a stub file for any
# specific provider would imply we're endorsing it.
SKEL="$WORK/prefix/etc/pocket-pi/skel"
mkdir -p "$SKEL/.pi/agent/skills/proposed"
cp "$ROOT/config/AGENTS.md"          "$SKEL/.pi/agent/AGENTS.md"
cp "$ROOT/config/claude-bridge.json" "$SKEL/.pi/agent/claude-bridge.json"
cp "$ROOT/config/models.json"        "$SKEL/.pi/agent/models.json"
cp -R "$ROOT/skills/."               "$SKEL/.pi/agent/skills/"

# 2a. Bundled Pi extensions — built TypeScript dropped under
# $PREFIX/lib/pocket-pi/<name>/. postinstall.sh runs `pi install` against
# each path so they're registered for the agent at first launch. We ship
# them from this monorepo because they're Pocket-Pi-specific (no upstream
# npm registry counterpart).
PI_EXT_DST="$WORK/prefix/lib/pocket-pi"
mkdir -p "$PI_EXT_DST"
for ext in pi-termux-tools; do
  src="$ROOT/extensions/$ext"
  if [ ! -d "$src/dist" ]; then
    echo "==> Building extension: $ext"
    ( cd "$src" && pnpm install --silent && pnpm build )
  fi
  mkdir -p "$PI_EXT_DST/$ext"
  cp -R "$src/dist"          "$PI_EXT_DST/$ext/dist"
  cp    "$src/package.json"  "$PI_EXT_DST/$ext/package.json"
  [ -f "$src/README.md" ] && cp "$src/README.md" "$PI_EXT_DST/$ext/README.md" || true
done

# 3. Repack
OUT="$DIST/bootstrap-${ARCH}.zip"
rm -f "$OUT"
( cd "$WORK/prefix" && zip -qry "$OUT" . )

unzip -tq "$OUT" >/dev/null
echo "==> Done: $OUT ($(du -h "$OUT" | cut -f1))"

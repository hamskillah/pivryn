#!/usr/bin/env bash
# Build a native custom-prefix Termux bootstrap for Pivryn Android.
# This does NOT rebrand com.termux binary packages.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERMUX_TREE="$HERE/termux-packages"
PACKAGE_ID="com.pivryn"
UPSTREAM_REPO="https://github.com/termux/termux-packages.git"
UPSTREAM_REVISION="90bab96741a878831e9e1ed328c7351083152be7"
PACKAGE_LIST="nodejs-lts,npm,python,git,ripgrep,curl,openssl"
ARCH="aarch64"

if [[ "${1:-}" == "--verify-source-config" ]]; then
  PROPERTIES="${2:?pass upstream properties.sh path}"
  python3 "$HERE/patch-termux-properties.py" --check "$PROPERTIES"
  exit 0
fi
if [[ "${1:-}" != "--build" ]]; then
  echo "Usage: $0 --build | --verify-source-config <properties.sh>" >&2
  exit 2
fi
for cmd in git python3 docker sha256sum unzip zip; do
  command -v "$cmd" >/dev/null || { echo "Missing required tool: $cmd" >&2; exit 3; }
done
docker info >/dev/null 2>&1 || { echo "Docker daemon is unavailable" >&2; exit 3; }

if [[ ! -d "$TERMUX_TREE/.git" ]]; then
  git clone --filter=blob:none "$UPSTREAM_REPO" "$TERMUX_TREE"
fi
git -C "$TERMUX_TREE" fetch --no-tags origin "$UPSTREAM_REVISION"
git -C "$TERMUX_TREE" checkout -q --detach "$UPSTREAM_REVISION"
python3 "$HERE/patch-termux-properties.py" --apply \
  "$TERMUX_TREE/scripts/properties.sh" "$PACKAGE_ID"

(
  cd "$TERMUX_TREE"
  ./scripts/run-docker.sh ./scripts/build-bootstraps.sh -f \
    --architectures "$ARCH" --add "$PACKAGE_LIST"
)
BASE_ZIP="$TERMUX_TREE/bootstrap-$ARCH.zip"
test -s "$BASE_ZIP"
unzip -tq "$BASE_ZIP" >/dev/null
python3 "$HERE/verify-custom-prefix.py" "$BASE_ZIP" "$PACKAGE_ID"

PIVRYN_CUSTOM_PREFIX=1 TERMUX_BASE_ZIP="$BASE_ZIP" \
  "$HERE/build-bootstrap.sh" "$ARCH"
echo "Custom-prefix bootstrap generated: $HERE/dist/bootstrap-$ARCH.zip"
echo "Prefix /data/data/$PACKAGE_ID/files/usr; revision $UPSTREAM_REVISION"

# Build verification

**Date:** 2026-11-23 UTC
**Baseline upstream:** `9cf4660dfcbaf49381dc828c2a4144d660d385fc`
**Machine:** Linux x86_64, 2 vCPU, ~4 GiB RAM.
**Toolchain:** Java 17, Gradle 8.10, Android SDK/build-tools 34.0.0, Node.js 24.
**Termux bootstrap:** `bootstrap-2026.11.15-r1+apt.android-7`, SHA-256 `388acf91cc247e7062d80cd8aa791fe72f360515fb78dc54ff45742120facae7`.

## Passed

- TypeScript builds: `pi-termux-tools`, `pi-skill-learner`.
- Python `py_compile` on optional backend.
- Shell syntax for bootstrap scripts.
- `python3 -m unittest discover -s tests -v`: 10 tests passed.
- `./gradlew :app:assembleDebug`: BUILD SUCCESSFUL.
- `./gradlew :app:lintDebug`: BUILD SUCCESSFUL, 0 errors.
- APK contains the complete `bootstrap-aarch64.zip` asset.

## Not validated

- First-run Android device bootstrap, Accessibility and permission handling.
- BYOK end-to-end against a model API.
- Interactive terminal: native adapter is packaged and checksummed but must pass its on-device PTY smoke; fallback remains if incompatible.
- Side-by-side installation with official Termux: not supported because package ID remains `com.termux`.
- Background survival and user-initiated process stop.
- Release key ownership/signing and public GitHub Actions run.

**Do not distribute the debug APK as a stable release. Never uninstall stock Termux to try this build.**


## Additional verification

- Pinned dashboard `@blackbelt-technology/pi-agent-dashboard@0.5.3` was installed with `npm --ignore-scripts` into a disposable global prefix. The loopback patch was successfully applied **twice** (idempotence) to its actual `@blackbelt-technology/pi-dashboard-server/src/server.ts`.
- Termux bootstrap includes verified `@mmmbuto/node-pty-android-arm64@1.1.2` archive with SHA-256 `dd5fa0cff041cd403bcf860caa6effcad0fc1d27472cbdbacc06f44719dfac95`. Its Android-native PTY has not been run in the test environment.
- Source unit tests expanded to 10.

- Native PTY rollback simulation executed on Linux with a forged architecture probe: incompatible native library caused exit code 5 and the original dashboard dependency was restored (**PASS**). Actual Android PTY success is still unverified.
- Verified upstream dashboard dependency layout via disposable global `npm install --ignore-scripts` before implementing the loopback patch.

## Final Android build (after PTY, Node 24 and network hardening)

- `./gradlew --no-daemon :app:lintDebug :app:assembleDebug`: BUILD SUCCESSFUL; 48 tasks, zero lint errors.
- Debug APK SHA-256: `cad5be9fdde0d4f97e1f0c05bcbd9b9ebdf998c1c09aeb532b78789621571afe`.
- Package ID is still `com.termux`; not safe to install next to official Termux.

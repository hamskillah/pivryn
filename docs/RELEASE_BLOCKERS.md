# Pivryn release gates

This file describes *verified source observations* and *tests not yet performed*. It is not a promise that every feature listed in the upstream README works in this fork.

## Known blockers

| Area | Current evidence | Release gate |
| --- | --- | --- |
| Package ID | `android/app/build.gradle.kts` still sets `applicationId = "com.termux"` because of baked-in native prefixes | Distinct package ID plus custom bootstrap verified; installation alongside official Termux |
| Terminal | Native ARM64 adapter included, tested for integrity and fallback; not executed on Android yet | Confirm real PTY keyboard, resize, exit/restart on physical device |
| Device tests | No physical Android test was available during this source snapshot | Install, bootstrap, permissions, BYOK, UI automation, background process and emergency stop tests |
| Build | Local Linux Java 17/SDK 34 debug assembly and Android Lint pass, but GitHub CI has not been run | Reproduce in GitHub Actions and verify APK boots on real Android |
| Bootstrap supply chain | Official development bootstrap and native PTY adapter pinned; custom Termux source build path added, but not executed | Verify custom source build and lock the runtime package dependency tree |
| Dependency pinning | Some first-run npm packages are not version-pinned | Lock critical versions and test tool integrations |
| Permissions | The app requests camera, microphone and location during initial activity launch | Audit least-privilege prompting and denial behavior |
| Source/runtime lifecycle | Upstream PiBridge termination strategy sweeps UID processes | Replace with testable process ownership and bounded shutdown |
| Security review | Dashboard wildcard-binding issue mitigated with verified localhost patch; full adversarial testing remains undone | Review auth, WS handlers, filesystem actions, prompt injection and sensitive logs |
| Licensing | Third-party notice review not complete for redistribution | License audit and source distribution obligations met |
| Production signing | Release signing workflow is implemented but no maintainer-owned key is configured | Stable private signing key, offline backup, GitHub secrets and actual signed APK verification |
| Package repository | Custom-prefix builder disables official Termux apt mirrors | Build isolated signed repository, or document bundled-only native packages and limited updates |

## GitHub Actions custom-prefix source build

The first GitHub Actions attempt (run 45200025586) failed during upstream
Termux bootstrap generation because `-f` hit an unset cleanup path,
expanding to `/*`. The wrapper now avoids force mode on fresh runners
and hardens the pinned upstream source to reject an empty or root cleanup
path. The next source build must still complete before the release gate is met.

The second attempt (run 45202825413) built a custom-prefix `apt` but failed
because upstream `build-bootstraps.sh` uses an obsolete `bzip2` recipe name.
The pinned tree instead defines `libbz2`, which builds the `bzip2` CLI
subpackage. The requested `curl` CLI similarly originates from the
`libcurl` source recipe. Both source package names are corrected, and a
fail-closed preflight now verifies **every** requested source recipe exists.
A complete custom-prefix bootstrap and Android APK remain unverified until CI
passes the corrected workflow.

## What this snapshot changes

- Visible app name and onboarding copy changed to **Pivryn** without prematurely changing Termux paths.
- Bootstrap ZIP path validation added for archive extraction and refresh.
- Removed unsafe unauthenticated APT repository fallback during bootstrap.
- ZIP integrity check and optional explicit SHA-256 validation added for Termux bootstrap downloads.
- CI adjusted to refuse automated publishing of development/debug APKs.
- Fixed Android Lint errors for API availability, notification permissions and invalid manifest permissions.
- Bounded and authenticated local HTTP bridge request parsing with timeouts.
- Restricted external WebView navigation and production WebView debugging.
- Pinned upstream Termux bootstrap release and SHA-256 checksum.
- Added checksum-verified Android ARM64 `node-pty` adapter with on-device PTY smoke and automatic fallback to upstream stub.
- Switched to Termux `nodejs-lts` (Node 24) and separately installed `npm` for pinned dashboard compatibility.
- Added a fail-closed loopback-only source patch and launcher guard for upstream dashboard 0.5.3, verified against the actual npm package.
- Added documentation and static source checks.

## What this snapshot intentionally does not change

- Original Pi agent loop, provider adapters, session formats, extension mechanism and dashboard.
- Original orb-eye Accessibility implementation and Android bridge.
- Existing native Termux prefix, Android package ID or any binary that expects `com.termux`.
- Native Android PTY adapter is experimental and falls back to the original stub when its on-device smoke fails.
- No Mimic fork or second companion APK.

## Verification language

- `PASSED`: an explicit check was run and recorded.
- `SOURCE ONLY`: source exists but runtime behavior not proven.
- `BLOCKED`: required Android tooling or device was unavailable.
- `NOT TESTED`: no check run.

A successful shell syntax check is not an Android runtime smoke test. A Gradle compilation is not an Android device test.
# Pivryn

**Your Android. Your Agent. Your Model.**

Pivryn is an experimental, open-source Android AI agent application forked from [Pocket Pi](https://github.com/CelestialCreator/pocket-pi). It bundles the original [Pi coding agent](https://github.com/earendil-works/pi-coding-agent), an embedded Termux environment, a chat dashboard, and Android device tools in a single Android project.

> **Status: verified development build, not a stable release.** Gradle assembly and Android Lint have passed, but on-device functionality and package coexistence have not yet been validated. See [release blockers](docs/RELEASE_BLOCKERS.md) before attempting distribution.

![Pocket Pi upstream demonstration](https://raw.githubusercontent.com/CelestialCreator/pocket-pi/9cf4660dfcbaf49381dc828c2a4144d660d385fc/assets/pocket-pi-demo.gif)

*Demo shows the upstream Pocket Pi application, not a tested Pivryn APK.*

## What it includes

| Capability | Implementation | Status |
| --- | --- | --- |
| AI model selection and BYOK | Original Pi runtime and dashboard | Upstream functionality; fork unverified |
| Android app UI | Kotlin + Jetpack Compose and WebView | Source included |
| Embedded shell and tooling | Termux bootstrap and scripts | Source included; initial download required |
| Screen reading, gestures, navigation | Existing orb-eye-based AccessibilityService | Manual opt-in; device test required |
| Notifications, intents, camera, microphone, clipboard | Original localhost Android bridge | Permission- and Android-version-dependent |
| Session and extension integration | Original Pi + upstream extensions | Runtime compatibility to be tested |
| Interactive dashboard PTY | Native ARM64 adapter + on-device smoke/fallback | **Physical-device result pending** |
| Coexistence with regular Termux | Independent com.pivryn source build prepared | **Not tested / not released** |

**Pivryn does not require a Claude subscription.** Choose a provider and supply your own API key through the existing dashboard. Provider usage may incur inference charges. Some OAuth flows listed in the dashboard are not usable without additional protocol adapters.

## Why a fork?

This fork favors *upstream-first engineering*. The Pi runtime, dashboard, Termux integration, and orb-eye Android control surface remain the original upstream implementation rather than being rewritten. Initial Pivryn changes concentrate on project identity and reliability fixes.

- **Not a new agent runtime**: Pivryn uses Pi.
- **Not a replacement Accessibility stack**: Pivryn uses Pocket Pi's existing orb-eye bridge. Mimic is **not** bundled.
- **Device-local dashboard**: installed dashboard server source is checked and restricted to 127.0.0.1 on each start, avoiding upstream's wildcard bind.
- **Not a way around Android security**: system privileges, Accessibility access, and app-private data remain governed by Android permissions and restrictions.
- **Not yet a production-ready app**: core compatibility and release gates still need real-world testing.

## Requirements

- A developer machine or CI runner to build the Android application, with Java 17, Android SDK and Gradle (wrapper included).
- Node.js 24 and pnpm 9 to compile bundled TypeScript extensions. The Android runtime installs Termux `nodejs-lts` (Node 24) and `npm` separately because the pinned dashboard does not support Node 25/26.
- Python 3.12 to package the optional Python extension.
- Android ARM64 device for actual testing.
- Internet access for upstream Termux bootstrap and first-run package installation.

### Source build

```bash
# Run from the repository root.
corepack enable

(cd extensions/pi-termux-tools && pnpm install --frozen-lockfile && pnpm build)
(cd extensions/pi-skill-learner && pnpm install --frozen-lockfile && pnpm build)

python3 -m pip install build
(cd python/skill_learner_dspy && python3 -m build --wheel)

./bootstrap/build-bootstrap.sh aarch64
(cd android && ./gradlew --no-daemon :app:assembleDebug)
```

Debug APK output: `android/app/build/outputs/apk/debug/app-debug.apk`.

**Important:** At present, the Android package ID deliberately remains `com.termux` because prebuilt Termux binaries contain absolute references to that package's file prefix. **Installing alongside stock Termux is not supported**; do not overwrite an existing Termux installation or risk its data. A distinct package name requires a verified custom-prefix bootstrap build, not merely editing Gradle's `applicationId`.

The project contains [`bootstrap/rebuild-with-prefix.sh`](bootstrap/rebuild-with-prefix.sh) from upstream as the foundation for that migration. This step has **not** been completed.

### Build verification

On **2026-11-23**, the development APK was built successfully with Gradle 8.10, Java 17, Android SDK 34 and the Termux aarch64 bootstrap. Android Lint returned **0 errors**. Six repository source tests and both TypeScript extension builds passed. No physical device or emulator was available. See [build verification](docs/BUILD_VERIFICATION.md).

### Custom-prefix build (experimental, Android ARM64 only)

Termux binary packages encode their Android application ID into native paths. To
ship a standalone Pivryn APK, packages must be compiled from source for
\`com.pivryn\`. The official Termux package repository cannot safely be mixed
with that prefix.

A dedicated [custom-prefix build script](bootstrap/rebuild-with-prefix.sh)
and a manually-triggered
[custom-prefix GitHub Actions workflow](.github/workflows/custom-prefix-bootstrap.yml)
are included.

\`\`\`bash
# Requires Linux + a working Docker daemon, significant CPU, disk and time.
bash bootstrap/rebuild-with-prefix.sh --build
(cd android && ./gradlew --no-daemon :app:lintDebug :app:assembleDebug -PpivrynCustomPrefix=true)
\`\`\`

The resulting APK is still a *development/test artifact*. A signed release
requires hardware testing and the maintainer's durable private signing key.
The custom-prefix bootstrap deliberately disables the official Termux apt
mirrors until a Pivryn-native package repository exists, so it is not yet
a full replacement for standalone Termux package management.

A normal debug build remains based on \`com.termux\`; the Gradle release
variant now **fails closed** without a verified custom-prefix bootstrap.

### CI

The workflow in [`.github/workflows/build-apk.yml`](.github/workflows/build-apk.yml) performs source checks and a development APK build, then uploads an **unsigned/development-only** artifact. It **does not publish a GitHub Release**. Do not distribute a debug build as a production release.

### Verify repository checks

```bash
python3 -m unittest discover -s tests -v
bash -n bootstrap/*.sh bootstrap/patches/*.sh
```

## Android permissions and privacy

Accessibility access is enabled manually by the user in Android Settings. When enabled, the agent can read visible screen content and issue gestures. A selected LLM provider can receive prompts and device observations required for tasks; **do not assume all data stays on the phone**.

Only grant sensitive permissions when appropriate. Be aware that camera, microphone, location, notifications, and UI content can involve personal data. Disable Accessibility access when it is not needed. The app's localhost bridge has a per-launch bearer token in the upstream implementation; security hardening and adversarial testing remain release blockers.

For safety and disclosure, see [SECURITY.md](SECURITY.md).

## Roadmap, deliberately small

1. Prove reproducible build + Android ARM64 first-run bootstrap.
2. Migrate to a distinct package ID and custom Termux prefix, without breaking existing apps.
3. Verify the Android-native PTY adapter on real phones and eliminate the fallback when stable.
4. Test BYOK and UI automation on real Android devices; fix stability and permission issues.
5. Publish a signed release **only after** functionality, licenses and security gates are satisfied.

## Upstream and licenses

This is a derivative of **Pocket Pi by CelestialCreator** (MIT). The original copyright and permission notice remain in [LICENSE](LICENSE). Its original documentation is preserved in [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md).

The runtime, dashboard, Termux bootstrap and Accessibility integration have their own upstream authors and license obligations. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). License review for final packaged binary distributions remains necessary.

**Baseline:** upstream Pocket Pi commit `9cf4660dfcbaf49381dc828c2a4144d660d385fc` (2026-05-14).
# Changelog

## 0.1.0-dev — 2026-11-23

- Forked Pocket Pi baseline `9cf4660` with upstream copyright preserved.
- Changed visible app identity and onboarding to Pivryn.
- Added bootstrap archive validation and pinned Termux base SHA-256.
- Removed unauthenticated APT mirror fallback.
- Fixed Android API and permission errors, passing Android Lint.
- Added HTTP parser limits and timeout, constant-time bearer comparison.
- Hardened WebView navigation and production debugging.
- Added source checks, CI, security, attribution and build documentation.
- Added pinned Android ARM64 PTY adapter with on-device smoke and safe fallback. Not yet hardware-verified.

- Replaced unqualified Termux nodejs (currently Node 26) with Node 24 LTS and standalone npm, matching pinned dashboard requirements.
- Hardened dashboard bootstrap/launcher to verify loopback-only binding, failing closed after incompatible upstream upgrades.

- Removed obsolete upstream emulator experiments from `scripts/` (not used by build or runtime).

**Development source snapshot, not a public stable release.**

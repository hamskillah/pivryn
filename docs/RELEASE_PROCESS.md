# Pivryn release process

**Current status: blocked.** There is no production-ready Pivryn APK.
This document defines release gates; it is not evidence of a successful
first-run installation, a signed release or compatibility with official Termux.

## Package identity

- Development compatibility builds can still use `com.termux`. Do not publish
  or install those builds alongside official Termux.
- Standalone Pivryn builds must use `com.pivryn` and source-built Termux
  libraries and packages, never mixed with the public com.termux apt repository.
- Source builds are handled by
  [`custom-prefix-bootstrap.yml`](../.github/workflows/custom-prefix-bootstrap.yml),
  which runs on relevant changes to main and can also be triggered manually.
- The workflow must produce a verified custom bootstrap ZIP and marker. A
  successful source compilation does **not** replace Android device testing.

## Release sign-off

Before any binary release, independently confirm:

1. Android ARM64 APK `com.pivryn` installs alongside an unmodified official
   Termux installation without overwriting user data.
2. First-run bootstrap succeeds, Pi launches, BYOK provider call works, and
   the dashboard can control the approved Android UI actions.
3. Accessibility permission can be revoked, the agent stops safely, shell
   and terminal behavior work, and cold-start/recovery tests pass.
4. No critical security findings in the local HTTP bridge, WebView, process
   lifecycle, shell or dependency supply chain.
5. Binary license obligations, attribution and third-party notices are complete.
6. A durable Android release keystore exists, is backed up **outside GitHub**,
   and the maintainer controls the password and key alias.

## Signing key setup (maintainer-owned)

Create the key in a trusted environment with Java 17+ installed. Do not
generate a fresh key for each CI run or store it in this Git repository.

```bash
keytool -genkeypair -v \
  -keystore pivryn-release.jks \
  -alias pivryn-release \
  -keyalg RSA -keysize 3072 -validity 36500 \
  -storetype PKCS12
```

Use interactive prompts for the passwords rather than putting them on the
command line. Back up the key and its passwords securely.

Configure these GitHub Actions repository secrets:

- `PIVRYN_RELEASE_KEYSTORE_BASE64`: Base64 of the complete keystore bytes.
- `PIVRYN_STORE_PASSWORD`: keystore password.
- `PIVRYN_KEY_ALIAS`: chosen alias.
- `PIVRYN_KEY_PASSWORD`: key password.

For example, after authenticating GitHub CLI:

```bash
base64 -w0 pivryn-release.jks | \
  gh secret set PIVRYN_RELEASE_KEYSTORE_BASE64 -R hamskillah/pivryn
gh secret set PIVRYN_STORE_PASSWORD -R hamskillah/pivryn
gh secret set PIVRYN_KEY_ALIAS -R hamskillah/pivryn
gh secret set PIVRYN_KEY_PASSWORD -R hamskillah/pivryn
```

The keystore is never committed and is only provided to the release job after
the human maintainer submits the required sign-offs. Configure protected
GitHub Environment `production` with required reviewers before enabling
release credentials.

## Release workflow

1. Merge and pass normal Android CI.
2. Wait for the `custom-prefix-bootstrap` source build to pass on **the
   exact intended main branch commit**.
3. Retrieve the successful run ID from Actions.
4. Test the resulting custom-prefix APK on real Android hardware.
5. Audit licenses and configure the production signing secrets.
6. Trigger
   [`signed-android-release.yml`](../.github/workflows/signed-android-release.yml)
   with the source build run ID, an increasing version code, and a candidate
   tag like `v0.1.0-rc.1`, plus the required sign-offs.
7. The workflow checks commit provenance, prefix and checksum, signs the APK,
   verifies it with `apksigner`, and creates a GitHub **pre-release**.
8. Do not promote to a stable version until all blockers have been closed.

If any check fails, do not bypass the gate or publish a debug APK instead.

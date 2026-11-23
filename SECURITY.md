# Security

Pivryn is experimental and should not be trusted with sensitive device workflows until an Android release has passed security and device testing.

## Responsible reporting

Please do not publish exploitable security issues as public GitHub issues. Contact the repository maintainer through a private channel when one becomes available, or use GitHub private vulnerability reporting if enabled.

## Security model

- The user must explicitly enable Android Accessibility permissions. Pivryn must not enable or bypass them programmatically.
- The local bridge must remain bound to the loopback interface and require an authenticated token, including across service restarts.
- Screen content, clipboard data, notifications, photos, microphone recordings and prompts may be sensitive and may reach the user's selected model API. Users control their provider credentials.
- Do not expose the local control bridge over the internet or via a public tunnel.
- Prompt injection from third-party UI text, notification content and webpages is a real risk. Payment, destructive actions, security setting changes and disclosures of sensitive information should require explicit user authorization.
- Never log API keys, authentication tokens or full sensitive payloads.
- Termux bootstrap and package downloads are supply-chain dependencies. Releases must use verified sources, immutable versions and checksums.
- Only install Android APKs from sources you trust. Never disable Play Protect or other system protections as a prerequisite.
- Android restricts app-private data, protected windows, and elevated system actions. Pivryn does not bypass those restrictions.

## Not yet validated

See `docs/RELEASE_BLOCKERS.md` for outstanding security, Android runtime, and test requirements. Do not advertise this snapshot as stable or publish the debug APK as a trusted release.
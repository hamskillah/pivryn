"""Small, dependency-free regression tests for Pivryn's source integration."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class IntegrationIntegrityTests(unittest.TestCase):
    def test_pivryn_app_label(self):
        values = (ROOT / "android/app/src/main/res/values/strings.xml").read_text()
        self.assertIn('<string name="app_name">Pivryn</string>', values)
        self.assertIn('<string name="accessibility_service_label">Pivryn</string>', values)

    def test_termux_prefix_is_not_pretend_migrated(self):
        gradle = (ROOT / "android/app/build.gradle.kts").read_text()
        self.assertIn('applicationId = "com.termux"', gradle)

    def test_zip_traversal_guard_present_in_extract_and_refresh(self):
        bootstrap = (
            ROOT / "android/app/src/main/java/com/zosma/pocketpi/pi/Bootstrapper.kt"
        ).read_text()
        self.assertIn("private fun safeBootstrapFile", bootstrap)
        self.assertEqual(bootstrap.count("safeBootstrapFile(prefix, entry.name)"), 2)
        self.assertIn("safeBootstrapFile(prefix, linknameRel)", bootstrap)

    def test_no_unauthenticated_apt_repository_fallback(self):
        install = (ROOT / "bootstrap/postinstall.sh").read_text()
        self.assertNotIn("Acquire::AllowInsecureRepositories", install)
        self.assertNotIn("Acquire::AllowDowngradeToInsecureRepositories", install)

    def test_bootstrap_supports_sha_verification(self):
        builder = (ROOT / "bootstrap/build-bootstrap.sh").read_text()
        self.assertIn("TERMUX_BOOTSTRAP_SHA256", builder)
        self.assertIn('unzip -tq "$WORK/base.zip"', builder)

    def test_bootstrap_selects_supported_node_lts_and_separate_npm(self):
        packages = (ROOT / "bootstrap/packages.txt").read_text().splitlines()
        self.assertIn("nodejs-lts", packages)
        self.assertIn("npm", packages)
        self.assertNotIn("nodejs", packages)
        installer = (ROOT / "bootstrap/postinstall.sh").read_text()
        self.assertIn("Pivryn requires Node 24 LTS", installer)

    def test_dashboard_listens_only_on_loopback(self):
        import importlib.util
        import tempfile
        spec = importlib.util.spec_from_file_location(
            "pivryn_dashboard_loopback",
            ROOT / "bootstrap/patches/dashboard-loopback.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "server.ts"
            f.write_text(module.OLD)
            self.assertTrue(module.patch(f))
            self.assertTrue(module.patch(f))
            self.assertEqual(f.read_text(), module.NEW)
            f.write_text("upstream changed server implementation")
            self.assertFalse(module.patch(f))

    def test_dashboard_loopback_rechecked_at_runtime(self):
        bridge = (ROOT / "android/app/src/main/java/com/zosma/pocketpi/pi/PiBridge.kt").read_text()
        self.assertIn("dashboard-loopback.py", bridge)
        setup = (ROOT / "bootstrap/postinstall.sh").read_text()
        self.assertIn('python3 "$ETC/patches/dashboard-loopback.py"', setup)

    def test_android_pty_adapter_is_version_and_checksum_pinned(self):
        builder = (ROOT / "bootstrap/build-bootstrap.sh").read_text()
        install = (ROOT / "bootstrap/postinstall.sh").read_text()
        adapter = (ROOT / "bootstrap/patches/pty-android-install.sh").read_text()
        sha = "dd5fa0cff041cd403bcf860caa6effcad0fc1d27472cbdbacc06f44719dfac95"
        self.assertIn(sha, builder)
        self.assertIn(sha, adapter)
        self.assertIn('PTY_VERSION="1.1.2"', builder)
        self.assertIn('sha256sum -c', adapter)
        self.assertIn('PIVRYN_PTY_SMOKE_OK', adapter)
        self.assertIn('NODE_PTY_PKG/lib/index.js', install)
        self.assertIn('pty-android-install.sh', install)

    def test_debug_apk_not_uploaded_as_a_public_release(self):
        workflow = (ROOT / ".github/workflows/build-apk.yml").read_text()
        self.assertNotIn("softprops/action-gh-release", workflow)
        self.assertIn("actions/upload-artifact@v4", workflow)


if __name__ == "__main__":
    unittest.main()

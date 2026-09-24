"""Live-client registration must preserve user configuration, including on failure."""
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="mario registration ")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / "codex home"
        self.env = dict(os.environ, CODEX_HOME=str(self.home))
        subprocess.run(["bash", str(ROOT / "scripts/link.sh"), "--target", "codex"],
                       env=self.env, capture_output=True, check=True)
        self.config = self.home / "config.toml"

    def run_register(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts/register_codex.py"), *args],
                              env=self.env, capture_output=True, text=True)

    def snapshot(self):
        return {str(p.relative_to(self.home)):
                ("link", os.readlink(p)) if p.is_symlink() else
                ("directory",) if p.is_dir() else ("file", p.read_bytes())
                for p in self.home.rglob("*")}

    def success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_dry_and_missing_check_do_not_write(self):
        before = self.snapshot()
        self.success(self.run_register("--dry"))
        self.assertEqual(self.run_register("--check").returncode, 1)
        self.assertEqual(self.snapshot(), before)

    def test_register_preserves_bytes_backup_permissions_and_is_idempotent(self):
        original = b'# existing user config\nmodel = "user-model"\n[features]\napps = true\n'
        self.config.write_bytes(original)
        self.config.chmod(0o640)
        self.success(self.run_register())
        self.assertTrue(self.config.read_bytes().startswith(original))
        self.assertEqual(stat.S_IMODE(self.config.stat().st_mode), 0o640)
        backups = [p for p in self.home.iterdir() if p.is_file() and p != self.config]
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        self.assertEqual(stat.S_IMODE(backups[0].stat().st_mode), 0o600)
        self.success(self.run_register("--check"))
        before = self.snapshot()
        self.success(self.run_register())
        self.assertEqual(self.snapshot(), before)

    def test_new_configuration(self):
        self.success(self.run_register())
        self.success(self.run_register("--check"))
        self.assertTrue(self.config.exists())
        self.assertEqual(stat.S_IMODE(self.config.stat().st_mode), 0o600)

    def test_relative_codex_home_writes_absolute_config_paths(self):
        relative_home = Path(self.tmp.name) / "relative home"
        install_env = dict(self.env, CODEX_HOME=str(relative_home))
        subprocess.run(
            ["bash", str(ROOT / "scripts/link.sh"), "--target", "codex"],
            env=install_env, capture_output=True, check=True,
        )
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/register_codex.py"),
             "--codex-home", "relative home"],
            cwd=self.tmp.name, env=self.env, capture_output=True, text=True,
        )
        self.success(result)
        config = (relative_home / "config.toml").read_text()
        self.assertIn(str(relative_home / "agents/architect.toml"), config)

    def test_foreign_role_refused_without_any_changes(self):
        self.config.write_text('[agents.architect]\ndescription="Mine"\nconfig_file="/foreign.toml"\n')
        before = self.snapshot()
        result = self.run_register()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_invalid_configuration_does_not_leak_content(self):
        secret = "DO_NOT_PRINT_PRIVATE_CONFIG_12345"
        self.config.write_text(f'token="{secret}"\nbroken = [\n')
        before = self.snapshot()
        result = self.run_register()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn(secret, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_inline_agent_table_fails_safely(self):
        self.config.write_text('agents = {}\n')
        before = self.snapshot()
        self.assertEqual(self.run_register().returncode, 1)
        self.assertEqual(self.snapshot(), before)

    def test_config_symlink_is_not_followed(self):
        other = self.home / "other.toml"
        other.write_text('# unrelated\n')
        self.config.symlink_to(other)
        before = self.snapshot()
        self.assertEqual(self.run_register().returncode, 1)
        self.assertEqual(self.snapshot(), before)

    def test_missing_installed_agent_prevents_partial_registration(self):
        (self.home / "agents/architect.toml").unlink()
        before = self.snapshot()
        self.assertEqual(self.run_register().returncode, 1)
        self.assertEqual(self.snapshot(), before)

    def test_atomic_replace_preserves_concurrent_config_change(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import register_codex
        finally:
            sys.path.pop(0)

        original = b'model = "before"\n'
        newer = b'model = "changed concurrently"\n'
        self.config.write_bytes(original)
        current = self.config.stat()
        identity = (current.st_dev, current.st_ino, current.st_size,
                    current.st_mtime_ns)

        def change_config(_fd):
            self.config.write_bytes(newer)

        with mock.patch.object(register_codex.os, "fsync", side_effect=change_config):
            with self.assertRaises(register_codex.RegistrationError):
                register_codex.atomic_replace(
                    self.config, b'model = "planned"\n', 0o600,
                    True, identity, original,
                )

        self.assertEqual(self.config.read_bytes(), newer)
        self.assertEqual(list(self.home.glob("config.toml.mario-*")), [])


if __name__ == '__main__':
    unittest.main()

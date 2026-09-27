"""Exercise native setup commands without touching a real client installation."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
ROLES = ("architect", "implementer", "code-reviewer", "mario-scribe")


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="mario setup ")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.claude = self.base / "claude home"
        self.codex = self.base / "codex home"
        native_home = self.base / "native home"
        self.env = dict(
            os.environ,
            HOME=str(native_home),
            USERPROFILE=str(native_home),
            CLAUDE_HOME=str(self.claude),
            CODEX_HOME=str(self.codex),
        )

    def install(self, *args, root=ROOT, env=None):
        return subprocess.run(
            [sys.executable, str(root / "scripts/install.py"), *args],
            env=env or self.env,
            capture_output=True,
            text=True,
        )

    def doctor(self, *args, root=ROOT, env=None):
        return subprocess.run(
            [sys.executable, str(root / "scripts/doctor.py"), *args],
            env=env or self.env,
            capture_output=True,
            text=True,
        )

    def success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def copy_checkout(self, name="source checkout"):
        copied = self.base / name
        copied.mkdir()
        for directory in (
            "scripts", "agents", "variants", "codex", "skills", "commands", "roles",
            ".claude-plugin",
        ):
            shutil.copytree(ROOT / directory, copied / directory)
        for filename in ("AGENTS.md", "METHOD.md", "README.md"):
            shutil.copy2(ROOT / filename, copied / filename)
        return copied

    def snapshot(self):
        result = {}
        for path in self.base.rglob("*"):
            key = str(path.relative_to(self.base))
            result[key] = (
                ("link", os.readlink(path)) if path.is_symlink() else
                ("dir",) if path.is_dir() else ("file", path.read_bytes())
            )
        return result

    def test_default_installs_claude_only_in_native_mode(self):
        self.success(self.install())
        for role in ROLES:
            destination = self.claude / "agents" / f"{role}.md"
            if os.name == "nt":
                self.assertEqual(destination.read_bytes(), (ROOT / "agents" / f"{role}.md").read_bytes())
            else:
                self.assertEqual(destination.resolve(), ROOT / "agents" / f"{role}.md")
        self.assertFalse(self.codex.exists())

    def test_copy_install_repeat_all_and_uninstall(self):
        self.success(self.install("--target", "all", "--mode", "copy"))
        self.success(self.doctor("--target", "all"))
        before = self.snapshot()
        self.success(self.install("--target", "all"))
        self.assertEqual(self.snapshot(), before)
        self.success(self.install("--target", "all", "--unlink"))
        self.assertFalse((self.claude / ".mario-install.json").exists())
        self.assertFalse((self.codex / ".mario-install.json").exists())

    def test_fable_copy_is_opt_in_sticky_and_switchable(self):
        architect = self.claude / "agents/architect.md"
        fable = ROOT / "variants/fable/architect.md"
        self.success(self.install("--mode", "copy", "--fable"))
        self.assertEqual(architect.read_bytes(), fable.read_bytes())
        self.success(self.install())
        self.assertEqual(architect.read_bytes(), fable.read_bytes())
        dry = self.install("--no-fable", "--dry")
        self.success(dry)
        self.assertIn("WOULD REFRESH", dry.stdout)
        self.assertEqual(architect.read_bytes(), fable.read_bytes())
        self.success(self.install("--no-fable"))
        self.assertEqual(architect.read_bytes(), (ROOT / "agents/architect.md").read_bytes())

    def test_exclusive_and_invalid_arguments_do_not_mutate(self):
        for args in (
            ("--fable", "--no-fable"), ("--dry", "--unlink"), ("--target",),
            ("--target", "other"), ("--mode", "other"), ("--wat",), ("extra",),
        ):
            with self.subTest(args=args):
                result = self.install(*args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(list(self.base.iterdir()), [])

    @unittest.skipIf(os.name == "nt", "shell launcher is POSIX compatibility only")
    def test_shell_launcher_remains_executable_and_forwards_args(self):
        result = subprocess.run(
            [str(ROOT / "scripts/link.sh"), "--target", "codex", "--dry"],
            env=self.env,
            capture_output=True,
            text=True,
        )
        self.success(result)
        self.assertEqual(list(self.base.iterdir()), [])

    def test_empty_home_overrides_use_native_home_consistently(self):
        env = dict(self.env, CLAUDE_HOME="", CODEX_HOME="")
        self.success(self.install("--target", "all", "--mode", "copy", env=env))
        native_home = Path(env["USERPROFILE"] if os.name == "nt" else env["HOME"])
        self.assertTrue((native_home / ".claude/agents/architect.md").is_file())
        self.assertTrue((native_home / ".codex/agents/architect.toml").is_file())
        self.success(self.doctor("--target", "all", env=env))

    def test_dry_and_absent_uninstall_create_nothing(self):
        for args in (("--target", "all", "--dry"), ("--target", "all", "--unlink")):
            with self.subTest(args=args):
                self.success(self.install(*args))
                self.assertEqual(list(self.base.iterdir()), [])

    def test_missing_sources_prevent_all_target_partial_install(self):
        for missing in ("codex/agents/mario-scribe.toml", "skills/start-project/SKILL.md"):
            with self.subTest(missing=missing):
                copied = self.copy_checkout("source " + missing.replace("/", "_"))
                (copied / missing).unlink()
                result = self.install("--target", "all", "--mode", "copy", root=copied)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertFalse(self.claude.exists())
                self.assertFalse(self.codex.exists())

    @unittest.skipIf(os.name == "nt", "unprivileged source-symlink creation is unavailable")
    def test_redirected_source_is_rejected(self):
        copied = self.copy_checkout()
        source = copied / "codex/agents/architect.toml"
        source.unlink()
        source.symlink_to(ROOT / "codex/agents/architect.toml")
        before = self.snapshot()
        result = self.install("--target", "codex", "--mode", "copy", root=copied)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_all_target_conflict_preflight_mutates_nothing(self):
        destination = self.codex / "agents/architect.toml"
        destination.parent.mkdir(parents=True)
        destination.write_text("foreign", encoding="utf-8")
        before = self.snapshot()
        result = self.install("--target", "all", "--mode", "copy")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_parent_file_prevents_partial_install(self):
        self.codex.mkdir()
        (self.codex / "agents").write_text("not a directory", encoding="utf-8")
        before = self.snapshot()
        self.assertEqual(
            self.install("--target", "all", "--mode", "copy").returncode, 1
        )
        self.assertEqual(self.snapshot(), before)

    @unittest.skipIf(os.name == "nt", "uses a POSIX symlink parent")
    def test_symlinked_parent_does_not_redirect_writes(self):
        elsewhere = self.base / "elsewhere"
        elsewhere.mkdir()
        self.codex.symlink_to(elsewhere, target_is_directory=True)
        before = self.snapshot()
        self.assertEqual(self.install("--target", "codex", "--mode", "copy").returncode, 1)
        self.assertEqual(self.snapshot(), before)

    @unittest.skipUnless(os.name == "nt", "Windows junction coverage")
    def test_windows_junction_parent_does_not_redirect_writes(self):
        elsewhere = self.base / "elsewhere"
        elsewhere.mkdir()
        result = subprocess.run(
            ["cmd.exe", "/c", "mklink", "/J", str(self.codex), str(elsewhere)],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            self.skipTest("junction creation unavailable")
        before = self.snapshot()
        self.assertEqual(self.install("--target", "codex", "--mode", "copy").returncode, 1)
        self.assertEqual(self.snapshot(), before)

    def test_same_content_foreign_file_is_not_adopted(self):
        destination = self.codex / "agents/architect.toml"
        destination.parent.mkdir(parents=True)
        destination.write_bytes((ROOT / "codex/agents/architect.toml").read_bytes())
        before = self.snapshot()
        result = self.install("--target", "codex", "--mode", "copy")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_atomic_copy_preserves_a_concurrent_destination(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import install as mario_install
        finally:
            sys.path.pop(0)
        destination = self.codex / "agents/architect.toml"
        destination.parent.mkdir(parents=True)
        before = mario_install.path_state(destination)

        def concurrent_write(_fd):
            destination.write_bytes(b"concurrent user content")

        with mock.patch.object(mario_install.os, "fsync", side_effect=concurrent_write):
            with self.assertRaises(mario_install.SetupError):
                mario_install.atomic_write(destination, b"planned", 0o600, before)
        self.assertEqual(destination.read_bytes(), b"concurrent user content")
        self.assertEqual(list(destination.parent.glob("architect.toml.mario-*")), [])

    @unittest.skipIf(os.name == "nt", "unprivileged source-symlink creation is unavailable")
    def test_action_rechecks_source_redirect_before_linking(self):
        copied = self.copy_checkout()
        sys.path.insert(0, str(copied / "scripts"))
        try:
            import install as mario_install
            plan = mario_install.plan_symlinks(
                "codex", self.codex, None, copied, False, False,
            )
            action = next(
                item for item in plan.actions
                if item.entry.destination_rel == "agents/architect.toml"
            )
            outside = self.base / "outside.toml"
            outside.write_bytes(b"outside\n")
            action.entry.source.unlink()
            action.entry.source.symlink_to(outside)
            with self.assertRaises(mario_install.SetupError):
                mario_install.apply_action(action)
            self.assertFalse(action.entry.destination.exists())
        finally:
            sys.path.pop(0)
            sys.modules.pop("install", None)

    def test_copy_refreshes_stale_source_but_refuses_modified_destination(self):
        copied = self.copy_checkout()
        self.success(self.install("--target", "codex", "--mode", "copy", root=copied))
        source = copied / "codex/agents/architect.toml"
        destination = self.codex / "agents/architect.toml"
        source.write_bytes(source.read_bytes() + b"\n# refreshed\n")
        self.assertEqual(self.doctor("--target", "codex", root=copied).returncode, 1)
        self.success(self.install("--target", "codex", root=copied))
        self.assertEqual(destination.read_bytes(), source.read_bytes())
        self.success(self.doctor("--target", "codex", root=copied))
        destination.write_bytes(b"user change\r\n")
        before = destination.read_bytes()
        self.assertEqual(self.install("--target", "codex", root=copied).returncode, 1)
        self.success(self.install("--target", "codex", "--unlink", root=copied))
        self.assertEqual(destination.read_bytes(), before)
        self.assertFalse((self.codex / ".mario-install.json").exists())

    def test_malformed_foreign_and_unsafe_receipts_are_rejected(self):
        receipt = self.codex / ".mario-install.json"
        cases = (
            b"{not json",
            json.dumps({"version": 1, "root": "/foreign", "files": {}}).encode(),
            json.dumps({
                "version": 1, "root": str(ROOT),
                "files": {"../escape": {"source": "codex/agents/architect.toml", "sha256": "0" * 64}},
            }).encode(),
            json.dumps({
                "version": 1, "root": str(ROOT),
                "files": {"agents/architect.toml": {"source": "README.md", "sha256": "0" * 64}},
            }).encode(),
            json.dumps({
                "version": 1, "root": str(ROOT),
                "files": {"agents/C:/evil.toml": {
                    "source": "codex/agents/C:/evil.toml", "sha256": "0" * 64,
                }},
            }).encode(),
            json.dumps({
                "version": 1, "root": str(ROOT),
                "files": {"agents/victim.toml": {
                    "source": "codex/agents/victim.toml", "sha256": "0" * 64,
                }},
            }).encode(),
            json.dumps({
                "version": 1, "root": str(ROOT),
                "files": {"skills/other/victim.txt": {
                    "source": "skills/other/victim.txt", "sha256": "0" * 64,
                }},
            }).encode(),
            json.dumps({
                "version": 1, "root": str(ROOT),
                "files": {"skills/start-project/victim.txt": {
                    "source": "skills/start-project/different.txt", "sha256": "0" * 64,
                }},
            }).encode(),
            json.dumps({
                "version": 1, "root": str(ROOT),
                "files": {"skills/start-project/victim.txt.": {
                    "source": "skills/start-project/victim.txt.", "sha256": "0" * 64,
                }},
            }).encode(),
            json.dumps({
                "version": 1, "root": str(ROOT),
                "files": {"skills//start-project/victim.txt": {
                    "source": "skills//start-project/victim.txt", "sha256": "0" * 64,
                }},
            }).encode(),
            json.dumps({
                "version": 1, "root": str(ROOT),
                "files": {"skills\\start-project\\victim.txt": {
                    "source": "skills\\start-project\\victim.txt", "sha256": "0" * 64,
                }},
            }).encode(),
            (
                '{"version":1,"version":1,"root":' + json.dumps(str(ROOT)) +
                ',"files":{}}'
            ).encode(),
        )
        for content in cases:
            with self.subTest(content=content[:20]):
                shutil.rmtree(self.codex, ignore_errors=True)
                self.codex.mkdir(parents=True)
                receipt.write_bytes(content)
                before = self.snapshot()
                result = self.install("--target", "codex", "--mode", "copy")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(self.snapshot(), before)

    def test_case_aliased_receipt_destinations_cannot_partially_uninstall(self):
        first = self.claude / "skills/start-project/Asset.txt"
        second = self.claude / "skills/start-project/asset.txt"
        first.parent.mkdir(parents=True)
        first.write_bytes(b"first owned asset\n")
        second.write_bytes(b"second owned asset\n")
        receipt = {
            "version": 1,
            "root": str(ROOT),
            "files": {
                "skills/start-project/Asset.txt": {
                    "source": "skills/start-project/Asset.txt",
                    "sha256": hashlib.sha256(first.read_bytes()).hexdigest(),
                },
                "skills/start-project/asset.txt": {
                    "source": "skills/start-project/asset.txt",
                    "sha256": hashlib.sha256(second.read_bytes()).hexdigest(),
                },
            },
        }
        (self.claude / ".mario-install.json").write_text(
            json.dumps(receipt), encoding="utf-8"
        )
        before = self.snapshot()
        result = self.install("--target", "claude", "--unlink")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires case-distinct source files")
    def test_case_aliased_skill_sources_fail_before_any_target_changes(self):
        copied = self.copy_checkout()
        assets = copied / "skills/start-project/assets"
        assets.mkdir()
        (assets / "Asset.txt").write_bytes(b"upper\n")
        (assets / "asset.txt").write_bytes(b"lower\n")
        result = self.install("--target", "all", "--mode", "copy", root=copied)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(self.claude.exists())
        self.assertFalse(self.codex.exists())

    @unittest.skipIf(os.name == "nt", "symlink creation may require privilege")
    def test_foreign_symlink_is_a_conflict_not_an_install(self):
        destination = self.claude / "agents/implementer.md"
        destination.parent.mkdir(parents=True)
        foreign = self.base / "foreign.md"
        foreign.write_text("foreign\n")
        destination.symlink_to(foreign)
        before = self.snapshot()
        result = self.install("--target", "claude", "--mode", "copy", "--no-fable")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Conflict", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_cross_mode_requires_uninstall(self):
        self.success(self.install("--target", "codex", "--mode", "copy"))
        self.assertEqual(
            self.install("--target", "codex", "--mode", "symlink").returncode, 1
        )
        self.success(self.install("--target", "codex", "--unlink"))
        if os.name != "nt":
            self.success(self.install("--target", "codex", "--mode", "symlink"))
            self.assertEqual(
                self.install("--target", "codex", "--mode", "copy").returncode, 1
            )

    @unittest.skipIf(os.name == "nt", "legacy symlink compatibility is POSIX coverage")
    def test_legacy_symlink_mode_and_fable_choice_remain_sticky(self):
        architect = self.claude / "agents/architect.md"
        self.success(self.install("--mode", "symlink", "--fable"))
        self.assertTrue(architect.is_symlink())
        self.assertEqual(architect.resolve(), ROOT / "variants/fable/architect.md")
        self.success(self.install())
        self.assertEqual(architect.resolve(), ROOT / "variants/fable/architect.md")
        self.success(self.doctor("--target", "claude"))

    def test_missing_source_does_not_block_owned_copy_uninstall(self):
        copied = self.copy_checkout()
        self.success(self.install("--target", "codex", "--mode", "copy", root=copied))
        (copied / "codex/agents/architect.toml").unlink()
        self.success(self.install("--target", "codex", "--unlink", root=copied))
        self.assertFalse((self.codex / "agents/architect.toml").exists())

    def test_skill_uninstall_preserves_unrelated_contents(self):
        self.success(self.install("--mode", "copy"))
        unrelated = self.claude / "skills/start-project/user.txt"
        unrelated.write_text("keep", encoding="utf-8")
        self.success(self.install("--unlink"))
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep")

    def test_auxiliary_skill_asset_uninstalls_after_source_removal(self):
        copied = self.copy_checkout()
        source = copied / "skills/start-project/assets/helper.txt"
        source.parent.mkdir()
        source.write_bytes(b"owned auxiliary asset\n")
        self.success(self.install("--mode", "copy", root=copied))
        destination = self.claude / "skills/start-project/assets/helper.txt"
        self.assertEqual(destination.read_bytes(), source.read_bytes())
        source.unlink()
        self.success(self.install("--unlink", root=copied))
        self.assertFalse(destination.exists())

    def test_modified_auxiliary_skill_asset_is_preserved(self):
        copied = self.copy_checkout()
        source = copied / "skills/start-project/assets/helper.txt"
        source.parent.mkdir()
        source.write_bytes(b"owned auxiliary asset\n")
        self.success(self.install("--mode", "copy", root=copied))
        destination = self.claude / "skills/start-project/assets/helper.txt"
        destination.write_bytes(b"user modified asset\n")
        source.unlink()
        self.success(self.install("--unlink", root=copied))
        self.assertEqual(destination.read_bytes(), b"user modified asset\n")

    def test_unicode_source_and_home_paths_copy_exact_bytes(self):
        copied = self.copy_checkout("source 🚀 with spaces")
        claude = self.base / "Claude 用户 🚀"
        codex = self.base / "Codex 用户 🚀"
        env = dict(
            self.env,
            CLAUDE_HOME=str(claude),
            CODEX_HOME=str(codex),
            PYTHONUTF8="0",
            PYTHONIOENCODING="ascii:strict",
        )
        self.success(self.install("--target", "all", "--mode", "copy", root=copied, env=env))
        self.assertEqual(
            (codex / "agents/architect.toml").read_bytes(),
            (copied / "codex/agents/architect.toml").read_bytes(),
        )
        self.success(self.doctor("--target", "all", root=copied, env=env))
        (codex / "config.toml").write_text('model = "user"\n', encoding="utf-8")
        registered = subprocess.run(
            [sys.executable, str(copied / "scripts/register_codex.py")],
            env=env,
            capture_output=True,
            text=True,
        )
        self.success(registered)
        self.assertIn("\\U0001f680", registered.stdout)

    def test_same_home_receipt_merges_both_targets(self):
        shared = self.base / "shared home"
        env = dict(self.env, CLAUDE_HOME=str(shared), CODEX_HOME=str(shared))
        self.success(self.install("--target", "all", "--mode", "copy", env=env))
        data = json.loads((shared / ".mario-install.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["files"]), 11)
        self.success(self.doctor("--target", "all", env=env))

    @unittest.skipIf(os.name == "nt", "POSIX mode-bit preservation")
    def test_copy_preserves_source_mode(self):
        copied = self.copy_checkout()
        source = copied / "codex/agents/architect.toml"
        source.chmod(0o640)
        self.success(self.install("--target", "codex", "--mode", "copy", root=copied))
        destination = self.codex / "agents/architect.toml"
        self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o640)

    def test_doctor_source_only_is_read_only(self):
        before = self.snapshot()
        result = self.doctor("--source-only", "--target", "all")
        self.success(result)
        self.assertIn("runtime", result.stdout.lower())
        self.assertEqual(self.snapshot(), before)

    def test_doctor_rejects_bad_binding_and_missing_codex_route(self):
        copied = self.copy_checkout()
        source = copied / "codex/agents/architect.toml"
        source.write_text(source.read_text().replace("gpt-6-astra", "wrong-model"))
        result = self.doctor("--source-only", "--target", "codex", root=copied)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        source.write_bytes((ROOT / "codex/agents/architect.toml").read_bytes())
        (copied / "codex/AGENTS.md").unlink()
        self.assertEqual(
            self.doctor("--source-only", "--target", "codex", root=copied).returncode, 1
        )

    def test_doctor_without_toml_parser(self):
        blocker = '''import runpy, sys
class NoToml:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('tomllib', 'tomli', 'pip'):
            raise ModuleNotFoundError(fullname)
sys.meta_path.insert(0, NoToml())
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
'''
        for target, expected in (("claude", 0), ("codex", 1)):
            result = subprocess.run(
                [sys.executable, "-c", blocker, str(ROOT / "scripts/doctor.py"),
                 "--source-only", "--target", target],
                env=self.env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_project_accepts_verified_absolute_checkout_pointer(self):
        checkout = self.copy_checkout("distinct mario checkout")
        project = self.base / "project"
        project.mkdir()
        (project / "CLAUDE.md").write_text(
            f'Read "{checkout / "AGENTS.md"}".\n', encoding="utf-8"
        )
        result = self.doctor("--source-only", "--target", "claude", "--project", str(project))
        self.success(result)
        self.assertIn("not required", result.stdout)
        self.assertEqual(
            self.doctor("--source-only", "--target", "codex", "--project", str(project)).returncode,
            1,
        )
        (project / "AGENTS.md").write_text(
            f"Read `{checkout / 'AGENTS.md'}`.\n", encoding="utf-8"
        )
        self.success(self.doctor("--source-only", "--target", "all", "--project", str(project)))

    def test_project_rejects_phrase_without_resolvable_pointer(self):
        project = self.base / "project"
        project.mkdir()
        for text in (
            "The setup mentions somethingAGENTS.md but no path.\n",
            f"Read {ROOT / 'AGENTS.md'}.backup instead.\n",
        ):
            with self.subTest(text=text):
                (project / "CLAUDE.md").write_text(text, encoding="utf-8")
                result = self.doctor(
                    "--source-only", "--target", "claude", "--project", str(project)
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    @unittest.skipIf(os.name == "nt", "POSIX symlink pointer coverage")
    def test_project_mario_pointer_remains_supported(self):
        project = self.base / "project"
        project.mkdir()
        (project / ".mario").symlink_to(ROOT, target_is_directory=True)
        (project / "AGENTS.md").write_text("Read .mario/AGENTS.md.\n", encoding="utf-8")
        self.success(self.doctor("--source-only", "--project", str(project)))

    def test_plugin_root_is_validated_independently_and_skips_home_links(self):
        plugin = self.copy_checkout("plugin cache root")
        result = self.doctor(
            "--target", "claude", "--claude-plugin-root", str(plugin)
        )
        self.success(result)
        self.assertIn("content structure only", result.stdout)
        self.assertFalse(self.claude.exists())
        (plugin / "agents/architect.md").unlink()
        result = self.doctor("--target", "claude", "--claude-plugin-root", str(plugin))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_plugin_root_rejects_malformed_or_mismatched_manifests(self):
        plugin = self.copy_checkout("plugin manifest root")
        manifest = plugin / ".claude-plugin/plugin.json"
        manifest.write_text("{bad json", encoding="utf-8")
        self.assertEqual(
            self.doctor("--target", "claude", "--claude-plugin-root", str(plugin)).returncode,
            1,
        )
        shutil.copy2(ROOT / ".claude-plugin/plugin.json", manifest)
        marketplace = plugin / ".claude-plugin/marketplace.json"
        data = json.loads(marketplace.read_text(encoding="utf-8"))
        data["plugins"][0]["version"] = "different"
        marketplace.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(
            self.doctor("--target", "claude", "--claude-plugin-root", str(plugin)).returncode,
            1,
        )


if __name__ == "__main__":
    unittest.main()

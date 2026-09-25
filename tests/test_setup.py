"""Exercise the public setup commands without touching a real client installation."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ROLES = ("architect", "implementer", "code-reviewer", "mario-scribe")


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="mario setup ")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.claude = self.base / "claude home"
        self.codex = self.base / "codex home"
        self.env = dict(os.environ, HOME=str(self.base / "home"),
                        CLAUDE_HOME=str(self.claude), CODEX_HOME=str(self.codex))

    def install(self, *args, root=ROOT):
        return subprocess.run(["bash", str(root / "scripts/link.sh"), *args],
                              env=self.env, capture_output=True, text=True)

    def doctor(self, *args, root=ROOT):
        return subprocess.run([sys.executable, str(root / "scripts/doctor.py"), *args],
                              env=self.env, capture_output=True, text=True)

    def success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def copy_checkout(self):
        copied = self.base / "source checkout"
        copied.mkdir()
        for name in ("scripts", "agents", "variants", "codex", "skills", "commands", "roles"):
            shutil.copytree(ROOT / name, copied / name)
        for name in ("AGENTS.md", "METHOD.md", "README.md"):
            shutil.copy2(ROOT / name, copied / name)
        return copied

    def snapshot(self):
        result = {}
        for p in self.base.rglob("*"):
            key = str(p.relative_to(self.base))
            result[key] = (("link", os.readlink(p)) if p.is_symlink() else
                           ("dir",) if p.is_dir() else ("file", p.read_bytes()))
        return result

    def test_default_installs_claude_only(self):
        self.success(self.install())
        for role in ROLES:
            self.assertEqual((self.claude / "agents" / (role + ".md")).resolve(),
                             ROOT / "agents" / (role + ".md"))
        self.assertTrue((self.claude / "skills/start-project").is_symlink())
        self.assertTrue((self.claude / "commands/seeya.md").is_symlink())
        self.assertFalse(self.codex.exists())

    def test_fable_architect_is_opt_in_and_sticky(self):
        architect = self.claude / "agents/architect.md"
        fable = ROOT / "variants/fable/architect.md"
        self.success(self.install("--fable"))
        self.assertEqual(architect.resolve(), fable)
        self.success(self.doctor("--target", "claude"))
        self.success(self.install())
        self.assertEqual(architect.resolve(), fable)
        dry = self.install("--no-fable", "--dry")
        self.success(dry)
        self.assertIn("WOULD SWITCH", dry.stdout)
        self.assertEqual(architect.resolve(), fable)
        switched = self.install("--no-fable")
        self.success(switched)
        self.assertIn("SWITCHED", switched.stdout)
        self.assertEqual(architect.resolve(), ROOT / "agents/architect.md")
        self.success(self.install("--fable"))
        self.success(self.install("--unlink"))
        self.assertFalse(architect.is_symlink())

    def test_fable_flags_are_exclusive(self):
        result = self.install("--fable", "--no-fable")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.claude.exists())

    def test_installer_remains_directly_executable(self):
        result = subprocess.run([str(ROOT / "scripts/link.sh"), "--target", "codex", "--dry"],
                                env=self.env, capture_output=True, text=True)
        self.success(result)
        self.assertEqual(list(self.base.iterdir()), [])

    def test_empty_home_overrides_use_defaults_consistently(self):
        self.env.update(CLAUDE_HOME="", CODEX_HOME="")
        self.success(self.install("--target", "all"))
        home = Path(self.env["HOME"])
        self.assertTrue((home / ".claude/agents/architect.md").is_symlink())
        self.assertTrue((home / ".codex/agents/architect.toml").is_symlink())
        self.success(self.doctor("--target", "all"))

    def test_codex_install_and_repeat(self):
        self.success(self.install("--target", "codex"))
        self.assertFalse(self.claude.exists())
        for role in ROLES:
            self.assertEqual((self.codex / "agents" / (role + ".toml")).resolve(),
                             ROOT / "codex/agents" / (role + ".toml"))
        before = self.snapshot()
        self.success(self.install("--target", "codex"))
        self.assertEqual(self.snapshot(), before)

    def test_combined_install_and_uninstall(self):
        self.success(self.install("--target", "all"))
        self.success(self.doctor("--target", "all"))
        self.success(self.install("--target", "all", "--unlink"))
        self.assertFalse(any(p.is_symlink() for p in self.base.rglob("*")))
        self.success(self.install("--target", "all", "--unlink"))

    def test_dry_and_absent_uninstall_do_not_create_directories(self):
        for args in (("--target", "all", "--dry"), ("--target", "all", "--unlink")):
            with self.subTest(args=args):
                self.success(self.install(*args))
                self.assertEqual(list(self.base.iterdir()), [])

    def test_bad_arguments_do_not_mutate(self):
        for args in (("--wat",), ("--target",), ("--target", "other"),
                     ("--dry", "--unlink"), ("extra",)):
            with self.subTest(args=args):
                result = self.install(*args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(list(self.base.iterdir()), [])

    def test_missing_source_prevents_partial_install(self):
        copied = self.copy_checkout()
        (copied / "codex/agents/mario-scribe.toml").unlink()
        result = self.install("--target", "all", root=copied)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(self.claude.exists())
        self.assertFalse(self.codex.exists())

    def test_missing_skill_definition_prevents_install(self):
        copied = self.copy_checkout()
        (copied / "skills/start-project/SKILL.md").unlink()
        self.assertEqual(self.install(root=copied).returncode, 1)
        self.assertFalse(self.claude.exists())

    def test_conflicts_preserved_and_no_partial_install(self):
        for kind in ("file", "directory", "foreign-link", "dangling-link", "directory-link"):
            with self.subTest(kind=kind):
                dest = self.codex / "agents/architect.toml"
                dest.parent.mkdir(parents=True, exist_ok=True)
                target = self.base / ("target " + kind)
                if kind == "file":
                    dest.write_text("user configuration")
                elif kind == "directory":
                    dest.mkdir()
                else:
                    if kind == "foreign-link":
                        target.write_text("foreign configuration")
                    elif kind == "directory-link":
                        target.mkdir()
                    dest.symlink_to(target)
                before = self.snapshot()
                for suffix in ((), ("--dry",)):
                    result = self.install("--target", "all", *suffix)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertEqual(self.snapshot(), before)
                if dest.is_symlink() or dest.is_file():
                    dest.unlink()
                else:
                    dest.rmdir()

    def test_parent_file_prevents_partial_install(self):
        self.codex.mkdir()
        (self.codex / "agents").write_text("not a directory")
        before = self.snapshot()
        self.assertEqual(self.install("--target", "all").returncode, 1)
        self.assertEqual(self.snapshot(), before)

    def test_symlinked_parent_does_not_redirect_writes(self):
        elsewhere = self.base / "elsewhere"
        elsewhere.mkdir()
        self.codex.symlink_to(elsewhere, target_is_directory=True)
        before = self.snapshot()
        self.assertEqual(self.install("--target", "all").returncode, 1)
        self.assertEqual(self.snapshot(), before)

    def test_equivalent_relative_link_is_owned(self):
        self.success(self.install("--target", "codex"))
        dest = self.codex / "agents/architect.toml"
        dest.unlink()
        dest.symlink_to(os.path.relpath(ROOT / "codex/agents/architect.toml", dest.parent))
        before = self.snapshot()
        self.success(self.install("--target", "codex"))
        self.assertEqual(self.snapshot(), before)
        self.success(self.doctor("--target", "codex"))
        self.success(self.install("--target", "codex", "--unlink"))
        self.assertFalse(dest.is_symlink())

    def test_uninstall_retains_foreign_entries(self):
        self.success(self.install("--target", "all"))
        dest = self.codex / "agents/architect.toml"
        dest.unlink()
        dest.write_text("user replacement")
        foreign = self.base / "workforces-agent.md"
        foreign.write_text("unrelated toolkit")
        link = self.claude / "agents/designer.md"
        link.symlink_to(foreign)
        self.success(self.install("--target", "all", "--unlink"))
        self.assertEqual(dest.read_text(), "user replacement")
        self.assertEqual(link.resolve(), foreign)
        self.assertFalse((self.codex / "agents/implementer.toml").is_symlink())

    def test_workforces_links_not_retired(self):
        target = self.base / "foreign.md"
        target.write_text("toolkit")
        agents = self.claude / "agents"
        agents.mkdir(parents=True)
        for name in ("clean-coder", "design-pilot", "design-reviewer"):
            (agents / (name + ".md")).symlink_to(target)
        self.success(self.install())
        self.success(self.install("--unlink"))
        for name in ("clean-coder", "design-pilot", "design-reviewer"):
            self.assertEqual((agents / (name + ".md")).resolve(), target)

    def test_source_paths_with_spaces(self):
        copied = self.copy_checkout()
        self.success(self.install("--target", "all", root=copied))
        self.assertEqual((self.codex / "agents/architect.toml").resolve(),
                         copied / "codex/agents/architect.toml")
        self.success(self.doctor("--target", "all", root=copied))

    def test_uninstall_when_source_was_removed(self):
        copied = self.copy_checkout()
        self.success(self.install("--target", "codex", root=copied))
        (copied / "codex/agents/architect.toml").unlink()
        self.success(self.install("--target", "codex", "--unlink", root=copied))
        self.assertFalse((self.codex / "agents/architect.toml").is_symlink())

    def test_doctor_source_only_is_read_only(self):
        before = self.snapshot()
        result = self.doctor("--source-only", "--target", "all")
        self.success(result)
        self.assertIn("runtime", result.stdout.lower())
        self.assertEqual(self.snapshot(), before)

    def test_doctor_missing_and_wrong_installed_link(self):
        result = self.doctor("--target", "codex")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(self.codex.exists())
        self.success(self.install("--target", "codex"))
        dest = self.codex / "agents/architect.toml"
        dest.unlink()
        dest.symlink_to(ROOT / "codex/agents/implementer.toml")
        self.assertEqual(self.doctor("--target", "codex").returncode, 1)

    def test_doctor_rejects_bad_binding(self):
        copied = self.copy_checkout()
        source = copied / "codex/agents/architect.toml"
        original = source.read_text()
        invalid_types = original.replace('developer_instructions = """', 'unused = """')
        invalid_types += '\ndeveloper_instructions = 42\n'
        for invalid in ('name = [', original.replace('gpt-6-astra', 'wrong-model'), invalid_types):
            with self.subTest(invalid=invalid[:20]):
                source.write_text(invalid)
                result = self.doctor("--source-only", "--target", "codex", root=copied)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("FAIL", result.stdout + result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_doctor_requires_codex_routing_document(self):
        copied = self.copy_checkout()
        (copied / "codex/AGENTS.md").unlink()
        result = self.doctor("--source-only", "--target", "codex", root=copied)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("codex/AGENTS.md", result.stdout)

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
            with self.subTest(target=target):
                result = subprocess.run(
                    [sys.executable, "-c", blocker, str(ROOT / "scripts/doctor.py"),
                     "--source-only", "--target", target],
                    env=self.env, capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                if expected:
                    self.assertIn("FAIL", result.stdout)

    def test_doctor_reports_symlink_loop(self):
        self.success(self.install("--target", "codex"))
        dest = self.codex / "agents/architect.toml"
        dest.unlink()
        dest.symlink_to(dest.name)
        result = self.doctor("--target", "codex")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        project = self.base / "project loop"
        project.mkdir()
        (project / ".mario").symlink_to(".mario")
        (project / "AGENTS.md").write_text("Read .mario/AGENTS.md")
        result = self.doctor("--source-only", "--project", str(project))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_doctor_project_pointer(self):
        project = self.base / "project"
        project.mkdir()
        (project / ".mario").symlink_to(ROOT, target_is_directory=True)
        instructions = project / "AGENTS.md"
        instructions.write_text("Existing project rules. Read .mario/AGENTS.md.\n")
        before = self.snapshot()
        self.success(self.doctor("--source-only", "--project", str(project)))
        self.assertEqual(self.snapshot(), before)
        instructions.write_text("Read .mario/METHOD.md only.\n")
        self.assertEqual(self.doctor("--source-only", "--project", str(project)).returncode, 1)
        instructions.write_text("Read .mario/AGENTS.md.\n")
        (project / ".mario").unlink()
        (project / ".mario").symlink_to(project / "missing")
        self.assertEqual(self.doctor("--source-only", "--project", str(project)).returncode, 1)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Read-only checks for mario source bindings and installed links."""
from __future__ import annotations

import argparse
import importlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROLES = ("architect", "implementer", "code-reviewer", "project-manager", "scribe")
AGENTS = ("architect", "implementer", "code-reviewer", "mario-scribe")
CODEX = {
    "architect": ("gpt-6-astra", "high", "read-only"),
    "implementer": ("gpt-5.6-sol", "high", "workspace-write"),
    "code-reviewer": ("gpt-5.6-terra", "high", "workspace-write"),
    "mario-scribe": ("gpt-5.6-luna", "medium", "workspace-write"),
}
CLAUDE = {
    "architect": ("sonnet", "Read, Grep, Glob"),
    "implementer": ("opus", "Read, Write, Edit, Bash, Glob, Grep"),
    "code-reviewer": ("sonnet", "Read, Grep, Glob, Bash"),
    "mario-scribe": ("haiku", "Read, Grep, Write"),
}


class Report:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def check(self, label: str, good: bool, detail: str = "") -> None:
        print(f"{'PASS' if good else 'FAIL'} {label}{': ' + detail if detail else ''}")
        if good:
            self.passed += 1
        else:
            self.failed += 1


def manifest(target: str) -> list[tuple[Path, Path, str]]:
    home = Path.home()
    entries: list[tuple[Path, Path, str]] = []
    if target in ("claude", "all"):
        base = Path(os.environ.get("CLAUDE_HOME") or home / ".claude").expanduser()
        entries.extend((ROOT / "agents" / f"{name}.md", base / "agents" / f"{name}.md", "file")
                       for name in AGENTS)
        entries.append((ROOT / "skills/start-project", base / "skills/start-project", "skill"))
        entries.extend((ROOT / "commands" / f"{name}.md", base / "commands" / f"{name}.md", "file")
                       for name in ("start-project", "seeya"))
    if target in ("codex", "all"):
        base = Path(os.environ.get("CODEX_HOME") or home / ".codex").expanduser()
        entries.extend((ROOT / "codex/agents" / f"{name}.toml",
                        base / "agents" / f"{name}.toml", "file") for name in AGENTS)
    return entries


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing frontmatter")
    end = lines.index("---", 1)
    return dict(line.split(":", 1) for line in lines[1:end] if ":" in line)


def toml_parser():
    for name in ("tomllib", "tomli", "pip._vendor.tomli"):
        try:
            return importlib.import_module(name)
        except ImportError:
            continue
    return None


def check_sources(report: Report, target: str, entries: list[tuple[Path, Path, str]]) -> None:
    for path in (ROOT / "AGENTS.md", ROOT / "METHOD.md",
                 *(ROOT / "roles" / f"{role}.md" for role in ROLES)):
        report.check(f"source {path.relative_to(ROOT)}", path.is_file())
    for source, _, kind in entries:
        valid = source.is_file() if kind == "file" else source.is_dir() and (source / "SKILL.md").is_file()
        report.check(f"source {source.relative_to(ROOT)}", valid)

    if target in ("claude", "all"):
        for name, (model, tools) in CLAUDE.items():
            path = ROOT / "agents" / f"{name}.md"
            if not path.is_file():
                continue
            try:
                meta = {key.strip(): value.strip() for key, value in frontmatter(path).items()}
                good = (meta.get("name") == name and meta.get("model") == model
                        and meta.get("tools") == tools)
                report.check(f"Claude binding {name}", good,
                             "" if good else "name/model/tools mismatch")
            except (ValueError, OSError) as exc:
                report.check(f"Claude binding {name}", False, str(exc))
    if target in ("codex", "all"):
        routing = ROOT / "codex/AGENTS.md"
        report.check("source codex/AGENTS.md", routing.is_file())
        try:
            routed = "codex/AGENTS.md" in (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        except OSError:
            routed = False
        report.check("root AGENTS.md Codex route", routed,
                     "" if routed else "must point to codex/AGENTS.md")
        parser = toml_parser()
        if parser is None:
            report.check("Codex TOML parser", False,
                         "tomllib, tomli, and pip._vendor.tomli unavailable")
            return
        for name, (model, effort, sandbox) in CODEX.items():
            path = ROOT / "codex/agents" / f"{name}.toml"
            if not path.is_file():
                continue
            try:
                data = parser.loads(path.read_text(encoding="utf-8"))
                role = f"roles/{name if name != 'mario-scribe' else 'scribe'}.md"
                instructions = data.get("developer_instructions", "")
                description = data.get("description", "")
                good = (data.get("name") == name and data.get("model") == model
                        and data.get("model_reasoning_effort") == effort
                        and data.get("sandbox_mode") == sandbox
                        and isinstance(description, str) and bool(description.strip())
                        and isinstance(instructions, str) and bool(instructions.strip())
                        and role in instructions and "METHOD.md" in instructions)
                report.check(f"Codex binding {name}", good,
                             "" if good else "name/model/effort/sandbox/role pointer mismatch")
            except (OSError, ValueError, TypeError) as exc:
                report.check(f"Codex binding {name}", False, str(exc))


def check_links(report: Report, entries: list[tuple[Path, Path, str]]) -> None:
    for source, dest, _ in entries:
        try:
            good = dest.is_symlink() and dest.resolve(strict=False) == source.resolve(strict=False)
        except (OSError, RuntimeError):
            good = False
        report.check(f"installed {dest}", good,
                     "" if good else "missing or does not point to this checkout")


def check_project(report: Report, project: Path) -> None:
    pointer = project / ".mario"
    try:
        good = pointer.is_symlink() and pointer.resolve(strict=False) == ROOT
    except (OSError, RuntimeError):
        good = False
    report.check(f"project {pointer}", good,
                 "" if good else "expected symlink resolving to this checkout")
    instructions = project / "AGENTS.md"
    try:
        points = ".mario/AGENTS.md" in instructions.read_text(encoding="utf-8")
    except (OSError, RuntimeError):
        points = False
    report.check(f"project {instructions}", points,
                 "" if points else "must point to .mario/AGENTS.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("claude", "codex", "all"), default="all")
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--project", type=Path)
    args = parser.parse_args()

    report = Report()
    entries = manifest(args.target)
    check_sources(report, args.target, entries)
    if not args.source_only:
        check_links(report, entries)
    if args.project is not None:
        check_project(report, args.project)
    print(f"Summary: {report.passed} PASS, {report.failed} FAIL")
    print("Runtime agent discovery and backend model identity: NOT TESTED")
    return 1 if report.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Read-only checks for Mario sources, installations, plugins, and project pointers."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from setup_support import (
    CLAUDE,
    CODEX,
    ROOT,
    ROLES,
    SetupError,
    absolute_path,
    copy_manifest,
    home_for,
    link_manifest,
    load_receipt,
    same_target,
    selected_receipt_files,
    sha256_file,
    target_names,
    toml_parser,
)


FABLE_REL = "variants/fable/architect.md"
REFERENCE_PATTERN = re.compile(
    r"(?P<quote>[`\"'])(?P<quoted>[^`\"'\r\n]*?AGENTS\.md)(?P=quote)"
    r"|(?P<bare>(?:[A-Za-z]:[\\/]|/|\.mario[\\/])[^\s`\"']*?AGENTS\.md)"
    r"(?![A-Za-z0-9_\\/:-]|\.[A-Za-z0-9_])",
    re.IGNORECASE,
)


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


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing frontmatter")
    end = lines.index("---", 1)
    return dict(line.split(":", 1) for line in lines[1:end] if ":" in line)


def required_root_paths(root: Path, target: str) -> list[Path]:
    paths = [root / "AGENTS.md", root / "METHOD.md"]
    paths.extend(root / "roles" / f"{role}.md" for role in ROLES)
    for selected in target_names(target):
        for entry in link_manifest(selected, root, Path("unused")):
            paths.append(entry.source / "SKILL.md" if entry.kind == "skill" else entry.source)
        paths.append(root / FABLE_REL if selected == "claude" else root / "codex/AGENTS.md")
    return paths


def root_has_components(root: Path, target: str) -> bool:
    return all(path.is_file() for path in required_root_paths(root, target))


def check_sources(report: Report, target: str, root: Path, label: str = "source") -> None:
    seen: set[Path] = set()
    for path in required_root_paths(root, target):
        if path in seen:
            continue
        seen.add(path)
        try:
            relative = path.relative_to(root)
        except ValueError:
            relative = path
        report.check(f"{label} {relative}", path.is_file())

    if target in ("claude", "all"):
        bindings = {
            root / "agents" / f"{name}.md": (name, *spec)
            for name, spec in CLAUDE.items()
        }
        bindings[root / FABLE_REL] = (
            "architect", "claude-fable-5-1", "Read, Grep, Glob",
        )
        for path, (name, model, tools) in bindings.items():
            item_label = f"{label} Claude binding {path.relative_to(root)}"
            if not path.is_file():
                report.check(item_label, False, "missing")
                continue
            try:
                meta = {key.strip(): value.strip() for key, value in frontmatter(path).items()}
                good = (
                    meta.get("name") == name and meta.get("model") == model and
                    meta.get("tools") == tools
                )
                report.check(item_label, good, "" if good else "name/model/tools mismatch")
            except (ValueError, OSError, UnicodeError) as exc:
                report.check(item_label, False, str(exc))

    if target in ("codex", "all"):
        routing = root / "codex/AGENTS.md"
        report.check(f"{label} codex/AGENTS.md", routing.is_file())
        try:
            routed = "codex/AGENTS.md" in (root / "AGENTS.md").read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            routed = False
        report.check(
            f"{label} root AGENTS.md Codex route", routed,
            "" if routed else "must point to codex/AGENTS.md",
        )
        parser = toml_parser()
        if parser is None:
            report.check(
                f"{label} Codex TOML parser", False,
                "tomllib, tomli, and pip._vendor.tomli unavailable",
            )
            return
        for name, (model, effort, sandbox) in CODEX.items():
            path = root / "codex/agents" / f"{name}.toml"
            if not path.is_file():
                continue
            try:
                data = parser.loads(path.read_text(encoding="utf-8"))
                role = f"roles/{name if name != 'mario-scribe' else 'scribe'}.md"
                instructions = data.get("developer_instructions", "")
                description = data.get("description", "")
                good = (
                    data.get("name") == name and data.get("model") == model and
                    data.get("model_reasoning_effort") == effort and
                    data.get("sandbox_mode") == sandbox and
                    isinstance(description, str) and bool(description.strip()) and
                    isinstance(instructions, str) and bool(instructions.strip()) and
                    role in instructions and "METHOD.md" in instructions
                )
                report.check(
                    f"{label} Codex binding {name}", good,
                    "" if good else "name/model/effort/sandbox/role pointer mismatch",
                )
            except (OSError, UnicodeError, ValueError, TypeError) as exc:
                report.check(f"{label} Codex binding {name}", False, str(exc))


def installed_fable(home: Path, receipt_files: dict[str, dict[str, str]], root: Path) -> bool:
    architect = receipt_files.get("agents/architect.md")
    if architect is not None:
        return architect["source"] == FABLE_REL
    destination = home / "agents/architect.md"
    return destination.is_symlink() and same_target(destination, root / FABLE_REL)


def check_installation(report: Report, target: str, root: Path) -> None:
    home = home_for(target)
    try:
        receipt = load_receipt(home, root)
    except SetupError as exc:
        report.check(f"installed {target} ownership receipt", False, str(exc))
        return
    owned = selected_receipt_files(receipt, (target,))
    fable = target == "claude" and installed_fable(home, owned, root)
    if owned:
        try:
            entries = copy_manifest(target, root, home, fable, require_sources=True)
        except SetupError as exc:
            report.check(f"installed {target} managed copies", False, str(exc))
            return
        current = {entry.destination_rel: entry for entry in entries}
        for destination_rel, entry in current.items():
            metadata = owned.get(destination_rel)
            good = False
            detail = "missing ownership entry"
            if metadata is not None:
                try:
                    source_hash = sha256_file(entry.source)
                    destination_hash = sha256_file(entry.destination)
                    good = (
                        not entry.destination.is_symlink() and entry.destination.is_file() and
                        metadata["source"] == entry.source_rel and
                        metadata["sha256"] == source_hash == destination_hash
                    )
                    detail = "" if good else "stale, modified, or source mismatch"
                except OSError:
                    detail = "missing or unreadable managed copy"
            report.check(f"installed managed copy {entry.destination}", good, detail)
        for stale in sorted(set(owned) - set(current)):
            report.check(f"installed managed copy {home / stale}", False, "stale receipt entry")
        return

    entries = link_manifest(target, root, home, fable)
    for entry in entries:
        accepted = [entry.source]
        if target == "claude" and entry.destination_rel == "agents/architect.md":
            accepted.append(root / ("agents/architect.md" if fable else FABLE_REL))
        good = entry.destination.is_symlink() and any(
            same_target(entry.destination, source) for source in accepted
        )
        report.check(
            f"installed {entry.destination}", good,
            "" if good else "missing or not a managed link/copy from this checkout",
        )


def check_plugin_manifests(report: Report, root: Path) -> str | None:
    plugin_path = root / ".claude-plugin/plugin.json"
    marketplace_path = root / ".claude-plugin/marketplace.json"
    try:
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        versions = [entry.get("version") for entry in marketplace.get("plugins", [])
                    if entry.get("name") == "mario"]
        version = plugin.get("version")
        good = (
            isinstance(version, str) and bool(version) and versions == [version]
        )
    except (OSError, UnicodeError, json.JSONDecodeError, AttributeError):
        version = None
        good = False
    report.check(
        f"Claude plugin manifest {root}", good,
        f"version {version}" if good else "missing, malformed, or version mismatch",
    )
    return version if good else None


def instruction_references(path: Path, project: Path) -> list[Path]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []
    references: list[Path] = []
    for match in REFERENCE_PATTERN.finditer(text):
        value = match.group("quoted") or match.group("bare")
        candidate = Path(value.replace("\\", os.sep) if os.name == "nt" else value)
        if not candidate.is_absolute():
            candidate = project / candidate
        references.append(absolute_path(candidate))
    return references


def valid_instruction_root(reference: Path, target: str) -> Path | None:
    if reference.name.lower() != "agents.md":
        return None
    try:
        resolved = reference.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    root = resolved.parent
    return root if root_has_components(root, target) else None


def instruction_roots(instruction: Path, project: Path, target: str) -> list[Path]:
    return list(dict.fromkeys(
        root for reference in instruction_references(instruction, project)
        if (root := valid_instruction_root(reference, target)) is not None
    ))


def check_instruction_file(
    report: Report,
    project: Path,
    instruction: Path,
    target: str,
) -> list[Path]:
    roots = instruction_roots(instruction, project, target)
    report.check(
        f"project {instruction} {target} route", bool(roots),
        "" if roots else "must reference AGENTS.md in an actual Mario checkout",
    )
    for root in dict.fromkeys(roots):
        report.check(
            f"project {target} checkout {root}", root_has_components(root, target),
            "validated independently of doctor and plugin roots",
        )
    return roots


def check_project(report: Report, project: Path, target: str) -> None:
    project = absolute_path(project)
    pointer = project / ".mario"
    if pointer.exists() or pointer.is_symlink():
        try:
            pointer_root = pointer.resolve(strict=True)
            pointer_good = root_has_components(pointer_root, target)
        except (OSError, RuntimeError):
            pointer_good = False
        report.check(
            f"project optional pointer {pointer}", pointer_good,
            "" if pointer_good else "does not resolve to a compatible Mario checkout",
        )
    else:
        report.check(f"project optional pointer {pointer}", True, "not required")

    agents = project / "AGENTS.md"
    claude = project / "CLAUDE.md"
    if target == "claude":
        candidates = [path for path in (agents, claude) if path.is_file()]
        for instruction in candidates:
            roots = instruction_roots(instruction, project, "claude")
            if roots:
                report.check(f"project {instruction} Claude route", True)
                for root in roots:
                    report.check(
                        f"project Claude checkout {root}", True,
                        "validated independently of doctor and plugin roots",
                    )
                return
        report.check(
            f"project Claude instructions {project}", False,
            "AGENTS.md or CLAUDE.md must reference AGENTS.md in an actual Mario checkout",
        )
        return

    roots = check_instruction_file(report, project, agents, "codex")
    if target == "all" and roots:
        for root in roots:
            report.check(
                f"project Claude route via {agents}", root_has_components(root, "claude"),
                "portable AGENTS.md route",
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("claude", "codex", "all"), default="all")
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--project", type=Path)
    parser.add_argument("--claude-plugin-root", type=Path)
    args = parser.parse_args()

    report = Report()
    checkout_root = absolute_path(ROOT)
    check_sources(report, args.target, checkout_root)
    checkout_version = (
        check_plugin_manifests(report, checkout_root)
        if args.target in ("claude", "all") else None
    )
    plugin_root = absolute_path(args.claude_plugin_root) if args.claude_plugin_root else None
    if plugin_root is not None:
        check_sources(report, "claude", plugin_root, "Claude plugin content")
        plugin_version = check_plugin_manifests(report, plugin_root)
    else:
        plugin_version = None
    if not args.source_only:
        for target in target_names(args.target):
            if target == "claude" and plugin_root is not None:
                report.check(
                    f"installed Claude plugin content {plugin_root}",
                    root_has_components(plugin_root, "claude"),
                    "content structure only; runtime enablement not tested",
                )
            else:
                check_installation(report, target, checkout_root)
    if args.project is not None:
        check_project(report, args.project, args.target)
    print(f"Summary: {report.passed} PASS, {report.failed} FAIL")
    print(
        f"Doctor checkout root: {checkout_root}; plugin manifest version: "
        f"{checkout_version or 'not checked'}"
    )
    print("Runtime agent discovery and backend model identity: NOT TESTED")
    if plugin_root is not None:
        print(
            f"Supplied Claude plugin root: {plugin_root}; version: "
            f"{plugin_version or 'INVALID'}; content structure: CHECKED; "
            "runtime enablement: NOT TESTED"
        )
    return 1 if report.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

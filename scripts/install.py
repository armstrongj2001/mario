#!/usr/bin/env python3
"""Install or remove Mario bindings on macOS, Windows, and Linux."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import stat
import sys
import tempfile

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from setup_support import (
    ROOT,
    ManifestEntry,
    Receipt,
    SetupError,
    absolute_path,
    configure_safe_stdio,
    copy_manifest,
    home_for,
    is_reparse,
    link_manifest,
    load_receipt,
    path_state,
    receipt_bytes,
    receipt_destination,
    reject_redirected_path,
    same_target,
    selected_receipt_files,
    sha256_bytes,
    target_for_destination,
    target_names,
)


@dataclass
class Action:
    verb: str
    entry: ManifestEntry
    before: tuple[object, ...]
    content: bytes | None = None
    source_before: tuple[object, ...] | None = None


@dataclass
class Plan:
    target: str
    home: Path
    mode: str
    receipt: Receipt | None
    actions: list[Action]
    messages: list[str]
    receipt_files: dict[str, dict[str, str]] | None = None


def usage_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install Mario bindings without replacing foreign client configuration."
    )
    parser.add_argument("--target", choices=("claude", "codex", "all"), default="claude")
    parser.add_argument("--mode", choices=("auto", "symlink", "copy"), default="auto")
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument("--dry", action="store_true", help="validate and preview")
    operation.add_argument("--unlink", action="store_true", help="remove owned bindings")
    architect = parser.add_mutually_exclusive_group()
    architect.add_argument("--fable", action="store_true")
    architect.add_argument("--no-fable", action="store_true")
    return parser


def owned_link(entry: ManifestEntry, path: Path | None = None) -> bool:
    destination = path or entry.destination
    return destination.is_symlink() and same_target(destination, entry.source)


def architect_variant(home: Path, receipt: Receipt | None, root: Path) -> bool | None:
    destination_rel = "agents/architect.md"
    if receipt is not None and destination_rel in receipt.files:
        source = receipt.files[destination_rel]["source"]
        return source == "variants/fable/architect.md"
    destination = home / destination_rel
    if destination.is_symlink():
        if same_target(destination, root / "variants/fable/architect.md"):
            return True
        if same_target(destination, root / "agents/architect.md"):
            return False
    return None


def detect_mode(target: str, home: Path, receipt: Receipt | None, root: Path) -> str | None:
    copy_owned = bool(selected_receipt_files(receipt, (target,)))
    link_owned = any(
        owned_link(entry)
        for fable in ((False, True) if target == "claude" else (False,))
        for entry in link_manifest(target, root, home, fable)
    )
    if copy_owned and link_owned:
        raise SetupError(
            f"Mixed copy and symlink installation in {home}; uninstall before reinstalling."
        )
    if copy_owned:
        return "copy"
    if link_owned:
        return "symlink"
    return None


def selected_fable(
    args: argparse.Namespace,
    claude_home: Path | None,
    receipt: Receipt | None,
    root: Path,
) -> bool:
    if args.fable:
        return True
    if args.no_fable:
        return False
    if claude_home is not None:
        installed = architect_variant(claude_home, receipt, root)
        if installed is not None:
            return installed
    if (not args.unlink and not args.dry and sys.stdin.isatty() and
            "claude" in target_names(args.target)):
        try:
            answer = input(
                "Bind the Claude architect to Claude Fable 5.1? "
                "Higher cost than the default Opus 5.5. [y/N] "
            )
        except EOFError:
            answer = ""
        return answer.lower().startswith("y")
    return False


def validate_source(entry: ManifestEntry) -> None:
    expected = entry.source.is_dir() if entry.kind == "skill" else entry.source.is_file()
    if not expected:
        label = "source skill" if entry.kind == "skill" else "source"
        raise SetupError(f"Missing {label}: {entry.source}")
    if is_reparse(entry.source):
        raise SetupError(f"Unexpected redirected source: {entry.source}")
    reject_redirected_path(entry.source.parent)
    if entry.kind == "skill" and not (entry.source / "SKILL.md").is_file():
        raise SetupError(f"Missing source skill: {entry.source / 'SKILL.md'}")


def validate_destination_parent(destination: Path) -> None:
    parent = destination.parent
    reject_redirected_path(parent)
    if parent.exists() and not parent.is_dir():
        raise SetupError(f"Parent path is not a directory: {parent}")


def source_state(source: Path) -> tuple[object, ...]:
    state = path_state(source)
    try:
        info = source.lstat()
    except OSError as exc:
        return (*state, "lstat-error", type(exc).__name__)
    return (
        *state,
        "mode", stat.S_IMODE(info.st_mode),
        "attributes", getattr(info, "st_file_attributes", 0),
    )


def planned_source_state(entry: ManifestEntry) -> tuple[object, ...]:
    validate_source(entry)
    before = source_state(entry.source)
    validate_source(entry)
    if source_state(entry.source) != before:
        raise SetupError(f"Source changed during preflight; retry: {entry.source}")
    return before


def ensure_source_unchanged(action: Action) -> None:
    if action.source_before is None:
        return
    validate_source(action.entry)
    if source_state(action.entry.source) != action.source_before:
        raise SetupError(f"Source changed after preflight; retry: {action.entry.source}")


def plan_symlinks(
    target: str,
    home: Path,
    receipt: Receipt | None,
    root: Path,
    fable: bool,
    unlink: bool,
) -> Plan:
    entries = link_manifest(target, root, home, fable)
    actions: list[Action] = []
    messages: list[str] = []
    for entry in entries:
        validate_destination_parent(entry.destination)
        before = path_state(entry.destination)
        if unlink:
            alternates = [entry]
            if target == "claude" and entry.destination_rel == "agents/architect.md":
                alternates = link_manifest(target, root, home, not fable)[:1] + [entry]
            if any(owned_link(candidate, entry.destination) for candidate in alternates):
                actions.append(Action("remove", entry, before))
                messages.append(f"REMOVED {entry.destination}")
            elif before[0] != "absent":
                messages.append(f"KEPT foreign entry {entry.destination}")
            continue

        source_before = planned_source_state(entry)
        if owned_link(entry):
            messages.append(f"OK {entry.destination}")
            continue
        alternate_owned = False
        if target == "claude" and entry.destination_rel == "agents/architect.md":
            alternate = link_manifest(target, root, home, not fable)[0]
            alternate_owned = owned_link(alternate, entry.destination)
        if alternate_owned:
            actions.append(Action("switch-link", entry, before, source_before=source_before))
            messages.append(f"SWITCHED {entry.destination} -> {entry.source}")
        elif before[0] != "absent":
            raise SetupError(f"Conflict: existing or foreign entry at {entry.destination}")
        else:
            actions.append(Action("link", entry, before, source_before=source_before))
            messages.append(f"LINKED {entry.destination} -> {entry.source}")
    return Plan(target, home, "symlink", receipt, actions, messages)


def plan_copies(
    target: str,
    home: Path,
    receipt: Receipt | None,
    root: Path,
    fable: bool,
    unlink: bool,
) -> Plan:
    old_selected = selected_receipt_files(receipt, (target,))
    updated: dict[str, dict[str, str]] = {}
    actions: list[Action] = []
    messages: list[str] = []

    if unlink:
        entries = {
            destination: ManifestEntry(
                target,
                root / metadata["source"],
                receipt_destination(home, destination),
                metadata["source"],
                destination,
            )
            for destination, metadata in old_selected.items()
        }
        for destination, entry in sorted(entries.items()):
            validate_destination_parent(entry.destination)
            before = path_state(entry.destination)
            expected_hash = old_selected[destination]["sha256"]
            if before[0] == "file" and before[-1] == expected_hash:
                actions.append(Action("remove", entry, before))
                messages.append(f"REMOVED {entry.destination}")
            elif before[0] != "absent":
                messages.append(f"KEPT modified or foreign entry {entry.destination}")
        return Plan(target, home, "copy", receipt, actions, messages, updated)

    entries = copy_manifest(target, root, home, fable, require_sources=True)
    current = {entry.destination_rel: entry for entry in entries}
    for destination in sorted(set(old_selected) - set(current)):
        metadata = old_selected[destination]
        entry = ManifestEntry(
            target, root / metadata["source"], receipt_destination(home, destination),
            metadata["source"], destination,
        )
        validate_destination_parent(entry.destination)
        before = path_state(entry.destination)
        if before[0] != "file" or before[-1] != metadata["sha256"]:
            raise SetupError(f"Owned copy was modified; refusing refresh: {entry.destination}")
        actions.append(Action("remove", entry, before))
        messages.append(f"REMOVED stale {entry.destination}")

    for destination, entry in sorted(current.items()):
        validate_destination_parent(entry.destination)
        source_before = planned_source_state(entry)
        content = entry.source.read_bytes()
        if source_state(entry.source) != source_before:
            raise SetupError(f"Source changed during preflight; retry: {entry.source}")
        digest = sha256_bytes(content)
        before = path_state(entry.destination)
        previous = old_selected.get(destination)
        if previous is None:
            if before[0] != "absent":
                raise SetupError(
                    f"Conflict: unowned entry at {entry.destination}; content is not ownership."
                )
            actions.append(Action(
                "write", entry, before, content=content, source_before=source_before,
            ))
            messages.append(f"COPIED {entry.destination}")
        else:
            if before[0] != "file" or before[-1] != previous["sha256"]:
                raise SetupError(f"Owned copy was modified; refusing refresh: {entry.destination}")
            if digest != previous["sha256"] or previous["source"] != entry.source_rel:
                actions.append(Action(
                    "write", entry, before, content=content, source_before=source_before,
                ))
                messages.append(f"REFRESHED {entry.destination}")
            else:
                messages.append(f"OK {entry.destination}")
        updated[destination] = {"source": entry.source_rel, "sha256": digest}
    return Plan(target, home, "copy", receipt, actions, messages, updated)


def ensure_unchanged(path: Path, before: tuple[object, ...]) -> None:
    if path_state(path) != before:
        raise SetupError(f"Path changed after preflight; retry: {path}")


def atomic_write(
    path: Path,
    content: bytes,
    mode: int,
    before: tuple[object, ...],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    reject_redirected_path(path.parent)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".mario-", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        if os.name != "nt":
            os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        ensure_unchanged(path, before)
        os.replace(temporary_path, path)
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass


def apply_action(action: Action) -> None:
    destination = action.entry.destination
    ensure_unchanged(destination, action.before)
    if action.verb == "remove":
        destination.unlink()
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    reject_redirected_path(destination.parent)
    ensure_source_unchanged(action)
    if action.verb == "write":
        source_mode = stat.S_IMODE(action.entry.source.lstat().st_mode)
        ensure_source_unchanged(action)
        atomic_write(destination, action.content or b"", source_mode, action.before)
        return
    if action.verb in ("link", "switch-link"):
        temporary = destination.with_name(destination.name + f".mario-{os.getpid()}")
        if temporary.exists() or temporary.is_symlink():
            raise SetupError(f"Temporary path already exists: {temporary}")
        try:
            temporary.symlink_to(
                action.entry.source,
                target_is_directory=action.entry.kind == "skill",
            )
            ensure_unchanged(destination, action.before)
            os.replace(temporary, destination)
        finally:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def write_receipts(plans: list[Plan], root: Path) -> None:
    grouped: dict[Path, tuple[Receipt | None, dict[str, dict[str, str]]]] = {}
    for plan in plans:
        if plan.mode != "copy" or plan.receipt_files is None:
            continue
        if plan.home not in grouped:
            base = dict(plan.receipt.files) if plan.receipt else {}
            grouped[plan.home] = (plan.receipt, base)
        receipt, files = grouped[plan.home]
        files = {
            destination: metadata
            for destination, metadata in files.items()
            if target_for_destination(destination) != plan.target
        }
        files.update(plan.receipt_files)
        grouped[plan.home] = (receipt, files)

    for home, (receipt, files) in grouped.items():
        path = home / ".mario-install.json"
        expected = receipt.state if receipt else ("absent",)
        if path_state(path) != expected:
            raise SetupError(f"Ownership receipt changed after preflight; retry: {path}")
        if files:
            content = receipt_bytes(root, files)
            if receipt is None or content != receipt.raw:
                atomic_write(path, content, 0o600, expected)
        elif expected[0] != "absent":
            ensure_unchanged(path, expected)
            path.unlink()


def main() -> int:
    configure_safe_stdio()
    args = usage_parser().parse_args()
    root = absolute_path(ROOT)
    selected_targets = target_names(args.target)
    homes = {target: home_for(target) for target in selected_targets}
    receipts: dict[Path, Receipt | None] = {}
    try:
        for home in set(homes.values()):
            reject_redirected_path(home)
            if home.exists() and not home.is_dir():
                raise SetupError(f"Client home is not a directory: {home}")
            receipts[home] = load_receipt(home, root)

        claude_home = homes.get("claude")
        fable = selected_fable(
            args,
            claude_home,
            receipts.get(claude_home) if claude_home is not None else None,
            root,
        )
        plans: list[Plan] = []
        for target in selected_targets:
            home = homes[target]
            receipt = receipts[home]
            detected = detect_mode(target, home, receipt, root)
            requested = args.mode
            if requested != "auto" and detected is not None and requested != detected:
                raise SetupError(
                    f"Existing {detected} install at {home}; uninstall before --mode {requested}."
                )
            mode = detected or ("copy" if requested == "auto" and os.name == "nt" else requested)
            if mode == "auto":
                mode = "symlink"
            if mode == "copy":
                plan = plan_copies(target, home, receipt, root, fable, args.unlink)
            else:
                plan = plan_symlinks(target, home, receipt, root, fable, args.unlink)
            plans.append(plan)

        prefix = "WOULD " if args.dry else ""
        if args.dry:
            for plan in plans:
                for message in plan.messages:
                    word, separator, rest = message.partition(" ")
                    preview = {
                        "LINKED": "LINK", "SWITCHED": "SWITCH", "COPIED": "COPY",
                        "REFRESHED": "REFRESH", "REMOVED": "REMOVE",
                    }.get(word, word)
                    print(prefix + preview + (separator + rest if separator else ""))
            print("Preflight passed; no files changed.")
            return 0

        for plan in plans:
            for action in plan.actions:
                apply_action(action)
        write_receipts(plans, root)
        for plan in plans:
            for message in plan.messages:
                print(message)
        return 0
    except SetupError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        print(
            "No automatic ownership repair was attempted; inspect any reported paths before retrying.",
            file=sys.stderr,
        )
        return 1
    except OSError as exc:
        print(f"FAIL setup could not complete: {exc}", file=sys.stderr)
        print(
            "A filesystem error can leave partial changes without an ownership receipt; inspect before retrying.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

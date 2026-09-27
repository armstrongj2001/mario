#!/usr/bin/env python3
"""Shared manifest, ownership, and filesystem checks for Mario setup tools."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent.parent
AGENT_NAMES = ("architect", "implementer", "code-reviewer", "mario-scribe")
ROLES = ("architect", "implementer", "code-reviewer", "project-manager", "scribe")
CLAUDE_COMMANDS = ("start-project", "seeya")
CODEX = {
    "architect": ("gpt-6-astra", "high", "read-only"),
    "implementer": ("gpt-5.6-sol", "high", "workspace-write"),
    "code-reviewer": ("gpt-5.6-terra", "high", "workspace-write"),
    "mario-scribe": ("gpt-5.6-luna", "medium", "workspace-write"),
}
CLAUDE = {
    "architect": ("claude-opus-5-5", "Read, Grep, Glob"),
    "implementer": ("claude-opus-5-5", "Read, Write, Edit, Bash, Glob, Grep"),
    "code-reviewer": ("claude-sonnet-5", "Read, Grep, Glob, Bash"),
    "mario-scribe": ("claude-haiku-4-5", "Read, Grep, Write"),
}
RECEIPT_NAME = ".mario-install.json"
RECEIPT_VERSION = 1
FIXED_SOURCE_PAIRS = {
    "agents/architect.md": {"agents/architect.md", "variants/fable/architect.md"},
    "agents/implementer.md": {"agents/implementer.md"},
    "agents/code-reviewer.md": {"agents/code-reviewer.md"},
    "agents/mario-scribe.md": {"agents/mario-scribe.md"},
    "commands/start-project.md": {"commands/start-project.md"},
    "commands/seeya.md": {"commands/seeya.md"},
    **{
        f"agents/{name}.toml": {f"codex/agents/{name}.toml"}
        for name in AGENT_NAMES
    },
}
FIXED_TARGETS = {
    **{
        destination: "claude"
        for destination in FIXED_SOURCE_PAIRS
        if not destination.endswith(".toml")
    },
    **{f"agents/{name}.toml": "codex" for name in AGENT_NAMES},
}


class SetupError(Exception):
    """A setup state is unsafe or inconsistent."""


def configure_safe_stdio() -> None:
    """Keep the active console encoding and escape characters it cannot represent."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(errors="backslashreplace")
        except (OSError, ValueError):
            continue


@dataclass(frozen=True)
class ManifestEntry:
    target: str
    source: Path
    destination: Path
    source_rel: str
    destination_rel: str
    kind: str = "file"


@dataclass(frozen=True)
class Receipt:
    path: Path
    root: Path
    files: dict[str, dict[str, str]]
    raw: bytes
    state: tuple[Any, ...]


def toml_parser():
    for name in ("tomllib", "tomli", "pip._vendor.tomli"):
        try:
            return importlib.import_module(name)
        except ImportError:
            continue
    return None


def absolute_path(path: Path) -> Path:
    return Path(os.path.abspath(path.expanduser()))


def home_for(target: str, override: Path | None = None) -> Path:
    if override is not None:
        return absolute_path(override)
    variable = "CLAUDE_HOME" if target == "claude" else "CODEX_HOME"
    configured = os.environ.get(variable)
    default = Path.home() / (".claude" if target == "claude" else ".codex")
    return absolute_path(Path(configured) if configured else default)


def target_names(target: str) -> tuple[str, ...]:
    return ("claude", "codex") if target == "all" else (target,)


def _base_specs(target: str, fable: bool) -> list[tuple[str, str, str]]:
    if target == "claude":
        architect = "variants/fable/architect.md" if fable else "agents/architect.md"
        specs = [(architect, "agents/architect.md", "file")]
        specs.extend(
            (f"agents/{name}.md", f"agents/{name}.md", "file")
            for name in AGENT_NAMES if name != "architect"
        )
        specs.append(("skills/start-project", "skills/start-project", "skill"))
        specs.extend(
            (f"commands/{name}.md", f"commands/{name}.md", "file")
            for name in CLAUDE_COMMANDS
        )
        return specs
    return [
        (f"codex/agents/{name}.toml", f"agents/{name}.toml", "file")
        for name in AGENT_NAMES
    ]


def link_manifest(
    target: str,
    root: Path = ROOT,
    home: Path | None = None,
    fable: bool = False,
) -> list[ManifestEntry]:
    destination_home = home or home_for(target)
    return [
        ManifestEntry(
            target, root / source_rel, destination_home / destination_rel,
            source_rel, destination_rel, kind,
        )
        for source_rel, destination_rel, kind in _base_specs(target, fable)
    ]


def validate_destination_aliases(destinations: Iterable[str]) -> None:
    aliases: dict[str, str] = {}
    for destination in destinations:
        canonical = destination.casefold()
        if canonical in aliases:
            raise SetupError(
                f"Aliased ownership destinations: {aliases[canonical]!r} and {destination!r}"
            )
        aliases[canonical] = destination


def copy_manifest(
    target: str,
    root: Path = ROOT,
    home: Path | None = None,
    fable: bool = False,
    require_sources: bool = True,
) -> list[ManifestEntry]:
    result: list[ManifestEntry] = []
    for entry in link_manifest(target, root, home, fable):
        if entry.kind == "file":
            if require_sources and not entry.source.is_file():
                raise SetupError(f"Missing source: {entry.source}")
            result.append(entry)
            continue
        skill_file = entry.source / "SKILL.md"
        if require_sources and not skill_file.is_file():
            raise SetupError(f"Missing source skill: {skill_file}")
        if require_sources and is_reparse(entry.source):
            raise SetupError(f"Unexpected redirected source: {entry.source}")
        if not entry.source.is_dir():
            continue
        for source in sorted(path for path in entry.source.rglob("*") if path.is_file()):
            relative = source.relative_to(entry.source)
            source_rel = PurePosixPath(entry.source_rel, *relative.parts).as_posix()
            destination_rel = PurePosixPath(entry.destination_rel, *relative.parts).as_posix()
            result.append(ManifestEntry(
                target, source, entry.destination / relative, source_rel, destination_rel,
            ))
    validate_destination_aliases(entry.destination_rel for entry in result)
    return result


def source_matches_destination(source_rel: str, destination_rel: str) -> bool:
    if destination_rel in FIXED_SOURCE_PAIRS:
        return source_rel in FIXED_SOURCE_PAIRS[destination_rel]
    if destination_rel.startswith("skills/start-project/"):
        suffix = destination_rel.removeprefix("skills/start-project/")
        return bool(suffix) and source_rel == f"skills/start-project/{suffix}"
    return False


def target_for_destination(destination_rel: str) -> str | None:
    fixed = FIXED_TARGETS.get(destination_rel)
    if fixed is not None:
        return fixed
    if destination_rel.startswith("skills/start-project/"):
        return "claude"
    return None


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError:
        return False
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    attributes = getattr(info, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & flag)


def reject_redirected_path(path: Path, include_leaf: bool = True) -> None:
    current = absolute_path(path)
    if not include_leaf:
        current = current.parent
    while current != current.parent:
        if current.exists() or current.is_symlink():
            if is_reparse(current):
                raise SetupError(f"Refusing redirected path: {current}")
            if not current.is_dir() and current != path:
                raise SetupError(f"Parent path is not a directory: {current}")
        current = current.parent


def is_readonly(path: Path) -> bool:
    info = path.stat()
    windows_readonly = getattr(stat, "FILE_ATTRIBUTE_READONLY", 0x1)
    attributes = getattr(info, "st_file_attributes", 0)
    if attributes & windows_readonly:
        return True
    if os.name != "nt" and not (stat.S_IMODE(info.st_mode) & 0o200):
        return True
    return False


def same_target(path: Path, expected: Path) -> bool:
    try:
        return path.resolve(strict=False) == expected.resolve(strict=False)
    except (OSError, RuntimeError):
        return False


def path_state(path: Path) -> tuple[Any, ...]:
    try:
        if path.is_symlink():
            return ("link", os.readlink(path))
        if not path.exists():
            return ("absent",)
        info = path.stat()
        if path.is_file():
            return (
                "file", info.st_dev, info.st_ino, info.st_size,
                info.st_mtime_ns, sha256_file(path),
            )
        if path.is_dir():
            return ("directory", info.st_dev, info.st_ino, info.st_mtime_ns)
        return ("other", info.st_mode)
    except OSError as exc:
        return ("error", type(exc).__name__)


def safe_receipt_relative(value: object, label: str) -> str:
    if (not isinstance(value, str) or not value or "\\" in value or ":" in value or
            any(ord(character) < 32 for character in value)):
        raise SetupError(f"Malformed ownership receipt {label}.")
    raw_parts = value.split("/")
    if any(not part or part in (".", "..") or part.endswith((" ", ".")) for part in raw_parts):
        raise SetupError(f"Unsafe ownership receipt {label}: {value!r}")
    relative = PurePosixPath(value)
    if relative.is_absolute():
        raise SetupError(f"Unsafe ownership receipt {label}: {value!r}")
    return relative.as_posix()


def unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise SetupError(f"Duplicate ownership receipt key: {key!r}")
        result[key] = value
    return result


def receipt_destination(home: Path, relative: str) -> Path:
    safe = safe_receipt_relative(relative, "destination")
    base = absolute_path(home)
    destination = absolute_path(base.joinpath(*PurePosixPath(safe).parts))
    try:
        destination.relative_to(base)
    except ValueError:
        raise SetupError(f"Ownership destination escapes client home: {relative!r}") from None
    return destination


def load_receipt(home: Path, root: Path = ROOT) -> Receipt | None:
    path = home / RECEIPT_NAME
    if not path.exists() and not path.is_symlink():
        return None
    reject_redirected_path(path)
    if is_reparse(path) or not path.is_file():
        raise SetupError(f"Refusing foreign ownership receipt: {path}")
    try:
        initial_state = path_state(path)
        raw = path.read_bytes()
        if path_state(path) != initial_state:
            raise SetupError(f"Ownership receipt changed while reading: {path}")
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_json_object)
    except SetupError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise SetupError(f"Malformed ownership receipt: {path}") from None
    if not isinstance(data, dict) or set(data) != {"version", "root", "files"}:
        raise SetupError(f"Malformed ownership receipt: {path}")
    if data["version"] != RECEIPT_VERSION or not isinstance(data["root"], str):
        raise SetupError(f"Unsupported ownership receipt: {path}")
    receipt_root = Path(data["root"])
    if not receipt_root.is_absolute() or absolute_path(receipt_root) != absolute_path(root):
        raise SetupError(f"Foreign ownership receipt root: {path}")
    if not isinstance(data["files"], dict):
        raise SetupError(f"Malformed ownership receipt files: {path}")
    files: dict[str, dict[str, str]] = {}
    for destination_value, metadata in data["files"].items():
        destination_rel = safe_receipt_relative(destination_value, "destination")
        if not isinstance(metadata, dict) or set(metadata) != {"source", "sha256"}:
            raise SetupError(f"Malformed ownership entry: {destination_rel}")
        source_rel = safe_receipt_relative(metadata.get("source"), "source")
        digest = metadata.get("sha256")
        if (not isinstance(digest, str) or
                re.fullmatch(r"[0-9a-f]{64}", digest) is None or
                not source_matches_destination(source_rel, destination_rel)):
            raise SetupError(f"Unexpected ownership entry: {destination_rel}")
        files[destination_rel] = {"source": source_rel, "sha256": digest}
    validate_destination_aliases(files)
    return Receipt(path, receipt_root, files, raw, initial_state)


def receipt_bytes(root: Path, files: dict[str, dict[str, str]]) -> bytes:
    data = {
        "version": RECEIPT_VERSION,
        "root": str(absolute_path(root)),
        "files": {name: files[name] for name in sorted(files)},
    }
    return (json.dumps(data, indent=2, sort_keys=False) + "\n").encode("utf-8")


def selected_receipt_files(
    receipt: Receipt | None,
    targets: Iterable[str],
) -> dict[str, dict[str, str]]:
    selected = set(targets)
    if receipt is None:
        return {}
    return {
        destination: metadata
        for destination, metadata in receipt.files.items()
        if target_for_destination(destination) in selected
    }

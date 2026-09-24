#!/usr/bin/env python3
"""Register installed mario Codex agents in config.toml without disturbing other settings."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import tempfile

from doctor import AGENTS as AGENT_NAMES, CODEX, ROOT, toml_parser


class RegistrationError(Exception):
    pass


def parse_toml(parser, text: str, label: str) -> dict:
    try:
        value = parser.loads(text)
    except (TypeError, ValueError):
        raise RegistrationError(f"{label} is not valid TOML.") from None
    if not isinstance(value, dict):
        raise RegistrationError(f"{label} must contain a TOML document.")
    return value


def same_file_target(path: Path, expected: Path) -> bool:
    try:
        return path.resolve(strict=False) == expected.resolve(strict=False)
    except (OSError, RuntimeError):
        return False


def reject_redirected_path(path: Path) -> None:
    current = path
    while current != current.parent:
        if current.is_symlink():
            raise RegistrationError(f"Refusing redirected path: {current}")
        current = current.parent


def installed_agents(codex_home: Path, parser) -> dict[str, tuple[Path, str]]:
    result: dict[str, tuple[Path, str]] = {}
    for name in AGENT_NAMES:
        model = CODEX[name][0]
        source = ROOT / "codex/agents" / f"{name}.toml"
        installed = codex_home / "agents" / f"{name}.toml"
        try:
            linked = installed.is_symlink() and same_file_target(installed, source)
        except OSError:
            linked = False
        if not linked:
            raise RegistrationError(
                f"Installed agent link is missing or foreign: {installed}"
            )
        try:
            data = parse_toml(parser, source.read_text(encoding="utf-8"),
                              f"Source binding {name}")
        except (OSError, UnicodeError):
            raise RegistrationError(f"Cannot read source binding: {source}") from None
        description = data.get("description")
        if (data.get("name") != name or data.get("model") != model
                or not isinstance(description, str) or not description.strip()):
            raise RegistrationError(f"Source binding metadata mismatch: {name}")
        result[name] = (installed, description.strip())
    return result


def configured_path(value: str, codex_home: Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else codex_home / path


def proposed_config(
    original: str,
    parsed: dict,
    bindings: dict[str, tuple[Path, str]],
    codex_home: Path,
) -> tuple[str, list[str]]:
    agents = parsed.get("agents", {})
    if not isinstance(agents, dict):
        raise RegistrationError("Existing [agents] setting conflicts with role registration.")

    missing: list[str] = []
    for name, (installed, _) in bindings.items():
        if name not in agents:
            missing.append(name)
            continue
        entry = agents[name]
        if not isinstance(entry, dict):
            raise RegistrationError(f"Existing agent registration conflicts: {name}")
        description = entry.get("description")
        config_file = entry.get("config_file")
        if "model" in entry:
            raise RegistrationError(f"Existing agent model override is ambiguous: {name}")
        if (not isinstance(description, str) or not description.strip()
                or not isinstance(config_file, str)
                or not same_file_target(configured_path(config_file, codex_home),
                                        ROOT / "codex/agents" / f"{name}.toml")):
            raise RegistrationError(f"Existing agent registration conflicts: {name}")

    if not missing:
        return original, missing

    suffix = ""
    if original and not original.endswith("\n"):
        suffix += "\n"
    if original:
        suffix += "\n"
    for name in missing:
        installed, description = bindings[name]
        suffix += (
            f'[agents.{json.dumps(name)}]\n'
            f'description = {json.dumps(description)}\n'
            f'config_file = {json.dumps(str(installed))}\n\n'
        )
    return original + suffix, missing


def reserve_backup(config: Path, content: bytes) -> Path:
    base = config.with_name(config.name + ".mario-backup")
    for number in range(1000):
        candidate = base if number == 0 else base.with_name(f"{base.name}.{number}")
        try:
            fd = os.open(candidate, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            continue
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(candidate, 0o600)
            return candidate
        except BaseException:
            try:
                candidate.unlink()
            except OSError:
                pass
            raise
    raise RegistrationError("Could not reserve a unique config backup path.")


def atomic_replace(
    config: Path,
    content: bytes,
    mode: int,
    existed: bool,
    identity,
    original: bytes,
) -> None:
    fd, temporary = tempfile.mkstemp(prefix=config.name + ".mario-", dir=config.parent)
    temp_path = Path(temporary)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if not unchanged(config, existed, identity, original):
            raise RegistrationError("Codex config changed during registration; retry.")
        os.replace(temp_path, config)
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def unchanged(config: Path, existed: bool, identity, content: bytes) -> bool:
    try:
        if not existed:
            return not config.exists() and not config.is_symlink()
        current = config.stat()
        current_identity = (current.st_dev, current.st_ino, current.st_size,
                            current.st_mtime_ns)
        return (not config.is_symlink() and current_identity == identity
                and config.read_bytes() == content)
    except OSError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry", action="store_true", help="validate and preview")
    modes.add_argument("--check", action="store_true", help="require complete registration")
    parser.add_argument("--codex-home", type=Path)
    args = parser.parse_args()

    codex_home = (args.codex_home
                  or Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex"))
    codex_home = Path(os.path.abspath(codex_home.expanduser()))
    config = codex_home / "config.toml"

    try:
        reject_redirected_path(codex_home)
        if config.is_symlink():
            raise RegistrationError(f"Refusing symlink config: {config}")
        parser_module = toml_parser()
        if parser_module is None:
            raise RegistrationError(
                "No TOML parser available (tried tomllib, tomli, pip._vendor.tomli)."
            )
        bindings = installed_agents(codex_home, parser_module)
        if config.exists():
            if not config.is_file():
                raise RegistrationError(f"Config path is not a regular file: {config}")
            try:
                original_bytes = config.read_bytes()
                original = original_bytes.decode("utf-8")
            except (OSError, UnicodeError):
                raise RegistrationError("Cannot read Codex config as UTF-8.") from None
            config_stat = config.stat()
            mode = stat.S_IMODE(config_stat.st_mode)
            identity = (config_stat.st_dev, config_stat.st_ino, config_stat.st_size,
                        config_stat.st_mtime_ns)
            existed = True
        else:
            original_bytes = b""
            original = ""
            mode = 0o600
            identity = None
            existed = False

        parsed = parse_toml(parser_module, original, "Codex config") if original else {}
        proposed, missing = proposed_config(original, parsed, bindings, codex_home)
        parse_toml(parser_module, proposed, "Proposed Codex config")

        if args.check:
            if missing:
                raise RegistrationError(
                    "Missing agent registrations: " + ", ".join(missing)
                )
            print("PASS all four Codex agents are registered.")
            return 0
        if not missing:
            print("OK all four Codex agents are already registered.")
            return 0
        if args.dry:
            print("WOULD REGISTER " + ", ".join(missing))
            return 0

        codex_home.mkdir(parents=True, exist_ok=True)
        if not unchanged(config, existed, identity, original_bytes):
            raise RegistrationError("Codex config changed during registration; retry.")
        backup = reserve_backup(config, original_bytes) if existed else None
        if not unchanged(config, existed, identity, original_bytes):
            if backup is not None:
                backup.unlink(missing_ok=True)
            raise RegistrationError("Codex config changed during registration; retry.")
        atomic_replace(
            config, proposed.encode("utf-8"), mode, existed, identity, original_bytes
        )
        if backup:
            print(f"BACKED UP {config} to {backup}")
        print("REGISTERED " + ", ".join(missing))
        return 0
    except RegistrationError as exc:
        print(f"FAIL {exc}", file=os.sys.stderr)
        return 1
    except OSError:
        print("FAIL Codex registration could not complete due to a filesystem error.",
              file=os.sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env bash
# Install or remove only the mario-owned links in the explicit manifest.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${CLAUDE_HOME:-$HOME/.claude}"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
TARGET=claude
MODE=install
FABLE=

usage() {
  cat <<'USAGE'
Usage: bash scripts/link.sh [--target claude|codex|all] [--dry | --unlink]
                           [--fable | --no-fable]
       bash scripts/link.sh --help

--fable binds the Claude architect to Claude Fable 5.1 instead of Opus 5.5.
Without either flag, an existing install keeps its architect; a first interactive
install asks; otherwise Opus 5.5.
USAGE
}

while (($#)); do
  case "$1" in
    --target)
      if (($# < 2)); then echo "Missing value for --target" >&2; usage >&2; exit 2; fi
      TARGET="$2"; shift 2 ;;
    --dry)
      if [[ "$MODE" != install ]]; then echo "--dry and --unlink are exclusive" >&2; exit 2; fi
      MODE=dry; shift ;;
    --unlink)
      if [[ "$MODE" != install ]]; then echo "--dry and --unlink are exclusive" >&2; exit 2; fi
      MODE=unlink; shift ;;
    --fable|--no-fable)
      if [[ -n "$FABLE" && "$FABLE" != "${1#--}" ]]; then echo "--fable and --no-fable are exclusive" >&2; exit 2; fi
      FABLE="${1#--}"; shift ;;
    --help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done
case "$TARGET" in claude|codex|all) ;; *) echo "Invalid target: $TARGET" >&2; exit 2 ;; esac

owned_link() {
  local src="$1" dest="$2"
  [[ -L "$dest" ]] && { [[ "$(readlink "$dest")" == "$src" ]] || [[ "$dest" -ef "$src" ]]; }
}

# An existing install keeps its architect variant unless a flag switches it.
DEFAULT_ARCHITECT="$ROOT/agents/architect.md"
FABLE_ARCHITECT="$ROOT/variants/fable/architect.md"
if [[ -z "$FABLE" && "$TARGET" != codex && "$MODE" != unlink ]]; then
  if owned_link "$FABLE_ARCHITECT" "$CLAUDE_DIR/agents/architect.md"; then
    FABLE=fable
  elif [[ -t 0 ]] && ! owned_link "$DEFAULT_ARCHITECT" "$CLAUDE_DIR/agents/architect.md"; then
    read -r -p "Bind the Claude architect to Claude Fable 5.1? Higher cost than the default Opus 5.5. [y/N] " reply || reply=
    [[ "$reply" =~ ^[Yy] ]] && FABLE=fable
  fi
fi

sources=()
destinations=()
checks=()
alternates=()
add_link() {
  sources+=("$1")
  destinations+=("$2")
  checks+=("$3")
  alternates+=("${4:-}")
}
if [[ "$TARGET" == claude || "$TARGET" == all ]]; then
  if [[ "$FABLE" == fable ]]; then
    add_link "$FABLE_ARCHITECT" "$CLAUDE_DIR/agents/architect.md" file "$DEFAULT_ARCHITECT"
  else
    add_link "$DEFAULT_ARCHITECT" "$CLAUDE_DIR/agents/architect.md" file "$FABLE_ARCHITECT"
  fi
  for name in implementer code-reviewer mario-scribe; do
    add_link "$ROOT/agents/$name.md" "$CLAUDE_DIR/agents/$name.md" file
  done
  add_link "$ROOT/skills/start-project" "$CLAUDE_DIR/skills/start-project" skill
  for name in start-project seeya; do
    add_link "$ROOT/commands/$name.md" "$CLAUDE_DIR/commands/$name.md" file
  done
fi
if [[ "$TARGET" == codex || "$TARGET" == all ]]; then
  for name in architect implementer code-reviewer mario-scribe; do
    add_link "$ROOT/codex/agents/$name.toml" "$CODEX_DIR/agents/$name.toml" file
  done
fi

# Check the base and selected parent paths before making any changes. A symlink
# directory could redirect writes outside the requested home.
check_parent() {
  local parent="$1"
  while [[ "$parent" != / && "$parent" != . ]]; do
    if [[ -L "$parent" || ( -e "$parent" && ! -d "$parent" ) ]]; then
      echo "Conflict: parent path is not a real directory: $parent" >&2
      return 1
    fi
    parent="$(dirname "$parent")"
  done
}

failed=0
for i in "${!sources[@]}"; do
  src="${sources[$i]}"
  dest="${destinations[$i]}"
  alt="${alternates[$i]}"
  check_parent "$(dirname "$dest")" || failed=1

  if [[ "$MODE" != unlink ]]; then
    if [[ "${checks[$i]}" == skill ]]; then
      if [[ ! -d "$src" || ! -f "$src/SKILL.md" ]]; then
        echo "Missing source skill: $src/SKILL.md" >&2
        failed=1
      fi
    elif [[ ! -f "$src" ]]; then
      echo "Missing source: $src" >&2
      failed=1
    fi
    if [[ -L "$dest" ]]; then
      if ! owned_link "$src" "$dest" && ! { [[ -n "$alt" ]] && owned_link "$alt" "$dest"; }; then
        echo "Conflict: foreign symlink at $dest" >&2
        failed=1
      fi
    elif [[ -e "$dest" ]]; then
      echo "Conflict: existing entry at $dest" >&2
      failed=1
    fi
  fi
done
if ((failed)); then
  echo "Preflight failed; no links changed." >&2
  exit 1
fi

for i in "${!sources[@]}"; do
  src="${sources[$i]}"
  dest="${destinations[$i]}"
  alt="${alternates[$i]}"
  if [[ "$MODE" == unlink ]]; then
    if owned_link "$src" "$dest" || { [[ -n "$alt" ]] && owned_link "$alt" "$dest"; }; then
      rm -- "$dest"
      echo "REMOVED $dest"
    elif [[ -e "$dest" || -L "$dest" ]]; then
      echo "KEPT foreign entry $dest"
    fi
  elif owned_link "$src" "$dest"; then
    echo "OK $dest"
  elif [[ -L "$dest" && "$MODE" == dry ]]; then
    echo "WOULD SWITCH $dest -> $src"
  elif [[ -L "$dest" ]]; then
    ln -sfn -- "$src" "$dest"
    echo "SWITCHED $dest -> $src"
  elif [[ "$MODE" == dry ]]; then
    echo "WOULD LINK $dest -> $src"
  else
    mkdir -p -- "$(dirname "$dest")"
    ln -s -- "$src" "$dest"
    echo "LINKED $dest -> $src"
  fi
done

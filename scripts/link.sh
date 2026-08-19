#!/usr/bin/env bash
# Links the base agent layer into ~/.claude/agents, overriding Workforces' agents by name.
# Workforces files on disk are never modified — only which symlink wins.
#
#   bash link.sh            install/refresh
#   bash link.sh --unlink   revert to Workforces agents
#   bash link.sh --dry      preview

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${CLAUDE_HOME:-$HOME/.claude}"
WF="${WORKFORCES_ROOT:-$HOME/antigravity/workforces}"
MODE=install
[[ "${1:-}" == "--unlink" ]] && MODE=unlink
[[ "${1:-}" == "--dry" ]]    && MODE=dry

# Workforces agents retired by this layer (their role is covered by a base agent).
# Name-collisions are handled by the link itself; these are the non-colliding ones.
# design-pilot / design-reviewer: all design belongs to /impeccable, which rolls a real
# direction from a seeded catalog instead of one model's taste. Both were removed from this
# layer; retiring them here also stops Workforces' copies from filling the gap.
RETIRE=(clean-coder design-pilot design-reviewer)

mkdir -p "$CLAUDE_DIR/agents"
echo "base agents → $CLAUDE_DIR/agents  (source: $ROOT)"

for f in "$ROOT"/agents/*.md; do
  n="$(basename "$f")"; dest="$CLAUDE_DIR/agents/$n"
  if [[ -e "$dest" && ! -L "$dest" ]]; then echo "  SKIP (real file): $n"; continue; fi
  case "$MODE" in
    unlink)
      if [[ "$(readlink "$dest" 2>/dev/null)" == "$f" ]]; then
        rm "$dest"; echo "  REVERTED: $n"
        [[ -f "$WF/agents/$n" ]] && ln -sfn "$WF/agents/$n" "$dest" && echo "    ↳ workforces $n restored"
      fi ;;
    dry)     [[ "$(readlink "$dest" 2>/dev/null)" == "$f" ]] || echo "  WOULD LINK: $n" ;;
    install) ln -sfn "$f" "$dest"; echo "  LINKED: $n" ;;
  esac
done

# skills/ and commands/ — same override semantics, applied only if the dirs exist.
for pair in "skills:skills" "commands:commands"; do
  src_dir="${pair%%:*}"; dst_dir="${pair##*:}"
  [[ -d "$ROOT/$src_dir" ]] || continue
  mkdir -p "$CLAUDE_DIR/$dst_dir"
  for f in "$ROOT/$src_dir"/*; do
    [[ -e "$f" ]] || continue
    n="$(basename "$f")"; dest="$CLAUDE_DIR/$dst_dir/$n"
    if [[ -e "$dest" && ! -L "$dest" ]]; then echo "  SKIP (real file): $n"; continue; fi
    case "$MODE" in
      unlink)  [[ "$(readlink "$dest" 2>/dev/null)" == "$f" ]] && rm "$dest" && echo "  REVERTED: $n" ;;
      dry)     [[ "$(readlink "$dest" 2>/dev/null)" == "$f" ]] || echo "  WOULD LINK: $src_dir/$n" ;;
      install) ln -sfn "$f" "$dest"; echo "  LINKED: $src_dir/$n" ;;
    esac
  done
done

# Sweep symlinks pointing at agents this layer no longer ships.
for dest in "$CLAUDE_DIR"/agents/*.md; do
  [[ -L "$dest" ]] || continue
  tgt="$(readlink "$dest")"
  [[ "$tgt" == "$ROOT/agents/"* && ! -e "$tgt" ]] || continue
  case "$MODE" in
    dry)     echo "  WOULD CLEAR (stale): $(basename "$dest")" ;;
    *)       rm "$dest"; echo "  CLEARED (stale): $(basename "$dest")" ;;
  esac
done

for n in "${RETIRE[@]}"; do
  dest="$CLAUDE_DIR/agents/$n.md"
  case "$MODE" in
    unlink)  [[ -f "$WF/agents/$n.md" && ! -e "$dest" ]] && ln -sfn "$WF/agents/$n.md" "$dest" && echo "  RESTORED: $n.md" ;;
    dry)     [[ -L "$dest" ]] && echo "  WOULD RETIRE: $n.md" ;;
    install) [[ -L "$dest" ]] && rm "$dest" && echo "  RETIRED: $n.md" ;;
  esac
done
exit 0

set -euo pipefail
: "${CFG_DIR:=/n/ha}"

resolve_gitdir() {
  local d="${1:-}"
  if [ -z "$d" ]; then
    echo "ERR: resolve_gitdir called without argument (missing_cfg_dir)" >&2
    exit 10
  fi
  if [ -d "$d/.git" ]; then
    GITDIR="$d/.git"
  elif [ -f "$d/.git" ]; then
    local p
    p="$(sed -n "s/^[[:space:]]*gitdir:[[:space:]]*//p" "$d/.git" | head -n1)"
    [ -n "${p:-}" ] || { echo "ERR: .git pointer present but empty ($d/.git)" >&2; exit 11; }
    case "$p" in
      /*) GITDIR="$p" ;;
      *)  GITDIR="$d/$p" ;;
    esac
  else
    echo "ERR: $d is not a git repo (no .git dir or pointer file)" >&2
    exit 12
  fi
  [ -d "$GITDIR" ] || { echo "ERR: resolved gitdir does not exist: $GITDIR" >&2; exit 13; }
  export GITDIR
}

export GIT_PAGER=cat
export GIT_TERMINAL_PROMPT=0
export GIT_OPTIONAL_LOCKS=0

resolve_gitdir "$CFG_DIR"

git() { (cd /; command git --git-dir="$GITDIR" --work-tree="$CFG_DIR" "$@"); }

(cd /; git rev-parse --is-inside-work-tree >/dev/null) || {
  echo "ERR: repo validation failed (CFG_DIR=$CFG_DIR, GITDIR=$GITDIR)" >&2
  exit 14
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo n/a)"
  toplevel="$(git rev-parse --show-toplevel 2>/dev/null || echo n/a)"
  status="$(git status --porcelain=v1 -uno 2>/dev/null | sed -n "1,20p")"
  jq -n --arg cfg "$CFG_DIR" --arg gd "$GITDIR" --arg br "$branch" --arg top "$toplevel" --arg st "$status" \
    "{cfg_dir:\$cfg, gitdir:\$gd, branch:\$br, toplevel:\$top, status_sample:\$st}"
fi

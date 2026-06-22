#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Install Solana Mainnet Ops Skill.

Usage:
  ./install.sh --user [--agents]
  ./install.sh --project /path/to/project [--agents]
  ./install.sh --dest /custom/skills/root

Options:
  --user              Install under ~/.claude/skills or ~/.agents/skills
  --project PATH      Install under PATH/.claude/skills or PATH/.agents/skills
  --dest PATH         Install into an explicit skills root
  --agents            Use .agents instead of .claude for project/user installs
  -h, --help          Show help
USAGE
}

MODE=""
PROJECT_PATH=""
DEST=""
CONFIG_DIR=".claude"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user)
      MODE="user"
      shift
      ;;
    --project)
      MODE="project"
      PROJECT_PATH="${2:-}"
      shift 2
      ;;
    --dest)
      MODE="dest"
      DEST="${2:-}"
      shift 2
      ;;
    --agents)
      CONFIG_DIR=".agents"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "$MODE" ]]; then
  MODE="user"
fi

case "$MODE" in
  user)
    SKILLS_ROOT="$HOME/$CONFIG_DIR/skills"
    ;;
  project)
    if [[ -z "$PROJECT_PATH" ]]; then
      echo "--project requires a path" >&2
      exit 1
    fi
    SKILLS_ROOT="$PROJECT_PATH/$CONFIG_DIR/skills"
    ;;
  dest)
    if [[ -z "$DEST" ]]; then
      echo "--dest requires a path" >&2
      exit 1
    fi
    SKILLS_ROOT="$DEST"
    ;;
  *)
    echo "Invalid mode: $MODE" >&2
    exit 1
    ;;
esac

TARGET="$SKILLS_ROOT/solana-mainnet-ops"
mkdir -p "$TARGET"
rm -rf "$TARGET/skill" "$TARGET/scripts" "$TARGET/agents" "$TARGET/commands"
cp -R "$SCRIPT_DIR/skill" "$TARGET/"
cp -R "$SCRIPT_DIR/scripts" "$TARGET/"
cp -R "$SCRIPT_DIR/agents" "$TARGET/"
cp -R "$SCRIPT_DIR/commands" "$TARGET/"

echo "Installed solana-mainnet-ops skill to $TARGET"

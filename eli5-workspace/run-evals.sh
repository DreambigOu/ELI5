#!/bin/bash
# ELI5 Skill Evaluation Runner
# Runs each test case with and without the skill using Claude Code CLI
#
# Prerequisites:
#   - claude CLI installed (npm install -g @anthropic-ai/claude-code)
#   - Skill installed at ~/.claude/skills/eli5/SKILL.md
#
# Usage:
#   ./run-evals.sh                    # Run all evals
#   ./run-evals.sh --test 1           # Run only test 1
#   ./run-evals.sh --with-skill-only  # Skip baseline runs

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_PATH="$HOME/.claude/skills/eli5/SKILL.md"

# Find next iteration number
ITERATION=1
while [ -d "$SCRIPT_DIR/iteration-$ITERATION" ]; do
  ITERATION=$((ITERATION + 1))
done
OUTDIR="$SCRIPT_DIR/iteration-$ITERATION"

echo "=== ELI5 Eval Runner ==="
echo "Output: $OUTDIR"
echo ""

# Parse flags
RUN_TEST=""
SKIP_BASELINE=false
for arg in "$@"; do
  case $arg in
    --test=*) RUN_TEST="${arg#*=}" ;;
    --test) shift; RUN_TEST="$2" ;;
    --with-skill-only) SKIP_BASELINE=true ;;
  esac
done

# Test cases
PROMPTS=(
  "ELI5 what a database index is"
  "Explain a typical web application codebase's structure to my manager"
  "Break down how git merge conflicts work for a 5th grader"
)
NAMES=(
  "explain-db-index-age5"
  "explain-codebase-manager"
  "explain-git-merge-5th-grader"
)

run_test() {
  local idx=$1
  local prompt="${PROMPTS[$idx]}"
  local name="${NAMES[$idx]}"

  echo "--- Test $((idx+1)): $name ---"

  # With skill
  local with_dir="$OUTDIR/$name/with_skill/outputs"
  mkdir -p "$with_dir"
  echo "  [with skill] Running..."
  claude -p "Read the skill at $SKILL_PATH first, then follow its instructions. Task: $prompt" \
    --output-format text \
    > "$with_dir/response.md" 2>/dev/null
  echo "  [with skill] Done -> $with_dir/response.md"

  # Without skill (baseline)
  if [ "$SKIP_BASELINE" = false ]; then
    local without_dir="$OUTDIR/$name/without_skill/outputs"
    mkdir -p "$without_dir"
    echo "  [baseline]   Running..."
    claude -p "$prompt" \
      --output-format text \
      > "$without_dir/response.md" 2>/dev/null
    echo "  [baseline]   Done -> $without_dir/response.md"
  fi

  echo ""
}

# Check prerequisites
if ! command -v claude &> /dev/null; then
  echo "Error: 'claude' CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
  exit 1
fi

if [ ! -f "$SKILL_PATH" ]; then
  echo "Error: Skill not found at $SKILL_PATH"
  echo "Install with: cp -r skills/eli5 ~/.claude/skills/eli5"
  exit 1
fi

# Run tests
if [ -n "$RUN_TEST" ]; then
  run_test $((RUN_TEST - 1))
else
  for i in "${!PROMPTS[@]}"; do
    run_test "$i"
  done
fi

echo "=== Done! ==="
echo "Results saved to: $OUTDIR"
echo "Compare outputs: diff $OUTDIR/*/with_skill/outputs/response.md $OUTDIR/*/without_skill/outputs/response.md"

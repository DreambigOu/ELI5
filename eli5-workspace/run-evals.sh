#!/bin/bash
# ELI5 Skill Evaluation Runner
# Runs each test case with and without the skill, then auto-grades with pass/fail
#
# Prerequisites:
#   - claude CLI installed (npm install -g @anthropic-ai/claude-code)
#   - Skill installed at ~/.claude/skills/eli5/SKILL.md
#
# Usage:
#   ./run-evals.sh                    # Run all evals + grade
#   ./run-evals.sh --test=1           # Run only test 1
#   ./run-evals.sh --with-skill-only  # Skip baseline runs
#   ./run-evals.sh --grade-only       # Grade existing outputs without re-running

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_PATH="$HOME/.claude/skills/eli5/SKILL.md"

# Parse flags
RUN_TEST=""
SKIP_BASELINE=false
GRADE_ONLY=false
for arg in "$@"; do
  case $arg in
    --test=*) RUN_TEST="${arg#*=}" ;;
    --with-skill-only) SKIP_BASELINE=true ;;
    --grade-only) GRADE_ONLY=true ;;
  esac
done

# Find iteration number
if [ "$GRADE_ONLY" = true ]; then
  # Grade the latest existing iteration
  ITERATION=1
  while [ -d "$SCRIPT_DIR/iteration-$((ITERATION + 1))" ]; do
    ITERATION=$((ITERATION + 1))
  done
else
  # Create next iteration
  ITERATION=1
  while [ -d "$SCRIPT_DIR/iteration-$ITERATION" ]; do
    ITERATION=$((ITERATION + 1))
  done
fi
OUTDIR="$SCRIPT_DIR/iteration-$ITERATION"

echo "=== ELI5 Eval Runner ==="
echo "Output: $OUTDIR"
echo ""

# Test case data
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

# Assertions per test case
ASSERTIONS_0=(
  "Contains no technical jargon (query, B-tree, schema, SQL, optimize, table/column/row in technical sense)"
  "Uses at least one concrete, child-friendly analogy (toys, animals, playground, picture books)"
  "Sentences are short and simple, averaging under 15 words per sentence"
  "Tone is warm, playful, and appropriate for a 5-year-old (not condescending or encyclopedic)"
)
ASSERTIONS_1=(
  "Contains no code blocks or inline code formatting — purely prose"
  "Frames explanation in business terms: mentions impact, decisions, risk, timeline, or team capacity"
  "Response is under 500 words — concise enough for a busy manager"
  "Includes at least one actionable recommendation or decision point for the manager"
)
ASSERTIONS_2=(
  "No unexplained advanced git terms (rebase, HEAD, SHA, hash, stage, commit used without a kid-friendly definition)"
  "Uses a relatable analogy for a 10-11 year old (school project, shared document, group assignment)"
  "Explanation follows a logical, sequential flow that builds understanding progressively"
  "Language and vocabulary are appropriate for a 5th grader — not too babyish, not too advanced"
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

grade_response() {
  local response_file=$1
  local test_idx=$2

  # Build assertions list
  local assertions_var="ASSERTIONS_${test_idx}[@]"
  local assertions_list=""
  local num=1
  for a in "${!assertions_var}"; do
    assertions_list="${assertions_list}${num}. ${a}
"
    num=$((num + 1))
  done

  local response_content
  response_content=$(cat "$response_file")

  claude -p "You are a strict grader. Grade this response against each assertion.

RESPONSE:
${response_content}

ASSERTIONS:
${assertions_list}
For each assertion, output exactly one line:
PASS|<number>|<brief evidence>
or
FAIL|<number>|<brief evidence>

Output ONLY those lines. No other text." \
    --output-format text 2>/dev/null
}

grade_all() {
  echo "=== Grading ==="
  echo ""

  local total_with_pass=0
  local total_with_total=0
  local total_without_pass=0
  local total_without_total=0

  local indices
  if [ -n "$RUN_TEST" ]; then
    indices="$((RUN_TEST - 1))"
  else
    indices="0 1 2"
  fi

  for idx in $indices; do
    local name="${NAMES[$idx]}"
    echo "--- Test $((idx+1)): $name ---"

    # Grade with_skill
    local with_file="$OUTDIR/$name/with_skill/outputs/response.md"
    if [ -f "$with_file" ]; then
      echo "  [with skill]"
      local grade_output
      grade_output=$(grade_response "$with_file" "$idx")
      echo "$grade_output" > "$OUTDIR/$name/with_skill/grading.txt"

      while IFS='|' read -r verdict num evidence; do
        verdict=$(echo "$verdict" | tr -d '[:space:]')
        if [ "$verdict" = "PASS" ]; then
          echo "    PASS  #$num — $evidence"
          total_with_pass=$((total_with_pass + 1))
          total_with_total=$((total_with_total + 1))
        elif [ "$verdict" = "FAIL" ]; then
          echo "    FAIL  #$num — $evidence"
          total_with_total=$((total_with_total + 1))
        fi
      done <<< "$grade_output"
    fi

    # Grade without_skill
    local without_file="$OUTDIR/$name/without_skill/outputs/response.md"
    if [ -f "$without_file" ] && [ "$SKIP_BASELINE" = false ]; then
      echo "  [baseline]"
      local grade_output
      grade_output=$(grade_response "$without_file" "$idx")
      echo "$grade_output" > "$OUTDIR/$name/without_skill/grading.txt"

      while IFS='|' read -r verdict num evidence; do
        verdict=$(echo "$verdict" | tr -d '[:space:]')
        if [ "$verdict" = "PASS" ]; then
          echo "    PASS  #$num — $evidence"
          total_without_pass=$((total_without_pass + 1))
          total_without_total=$((total_without_total + 1))
        elif [ "$verdict" = "FAIL" ]; then
          echo "    FAIL  #$num — $evidence"
          total_without_total=$((total_without_total + 1))
        fi
      done <<< "$grade_output"
    fi

    echo ""
  done

  # Summary
  echo "========================================="
  echo "  PASS RATE SUMMARY — Iteration $ITERATION"
  echo "========================================="
  if [ "$total_with_total" -gt 0 ]; then
    local with_rate
    with_rate=$(echo "scale=1; $total_with_pass * 100 / $total_with_total" | bc)
    echo "  With Skill:    $total_with_pass/$total_with_total passed (${with_rate}%)"
  fi
  if [ "$SKIP_BASELINE" = false ] && [ "$total_without_total" -gt 0 ]; then
    local without_rate
    without_rate=$(echo "scale=1; $total_without_pass * 100 / $total_without_total" | bc)
    echo "  Without Skill: $total_without_pass/$total_without_total passed (${without_rate}%)"
    if [ "$total_with_total" -gt 0 ]; then
      local delta
      delta=$(echo "scale=1; $with_rate - $without_rate" | bc)
      echo "  Delta:         ${delta}%"
    fi
  fi
  echo "========================================="

  # Save summary to file
  {
    echo "ELI5 Eval Summary — Iteration $ITERATION"
    echo "Date: $(date)"
    echo ""
    if [ "$total_with_total" -gt 0 ]; then
      echo "With Skill:    $total_with_pass/$total_with_total passed"
    fi
    if [ "$SKIP_BASELINE" = false ] && [ "$total_without_total" -gt 0 ]; then
      echo "Without Skill: $total_without_pass/$total_without_total passed"
    fi
  } > "$OUTDIR/summary.txt"

  echo ""
  echo "Grading details: $OUTDIR/*/with_skill/grading.txt"
}

# Check prerequisites
if ! command -v claude &> /dev/null; then
  echo "Error: 'claude' CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
  exit 1
fi

if [ ! -f "$SKILL_PATH" ] && [ "$GRADE_ONLY" = false ]; then
  echo "Error: Skill not found at $SKILL_PATH"
  echo "Install with: cp -r skills/eli5 ~/.claude/skills/eli5"
  exit 1
fi

# Run tests (unless --grade-only)
if [ "$GRADE_ONLY" = false ]; then
  if [ -n "$RUN_TEST" ]; then
    run_test $((RUN_TEST - 1))
  else
    for i in "${!PROMPTS[@]}"; do
      run_test "$i"
    done
  fi
  echo "=== Tests Complete ==="
  echo ""
fi

# Grade all outputs
grade_all

echo "=== All Done! ==="

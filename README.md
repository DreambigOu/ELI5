# ELI5 — Explain Like I Am 5

> A [Claude Code](https://claude.ai) skill that explains anything to anyone — kids, managers, engineers, parents. It adapts tone, vocabulary, analogies, and framing to match the audience.

Ever needed to explain a technical concept to your manager? Or break down code for a 5th grader? ELI5 makes Claude automatically adjust its explanation style based on who's listening.

## Supported Audiences

| Category | Examples |
|----------|---------|
| **Ages** | 5, 10, 15, 20, 30, 40+ |
| **Grade Levels** | 5th grade, Middle school, Senior High, College, Graduate school |
| **Job Roles** | Manager, Engineer, Designer, Director, Product Manager |
| **Relationships** | Wife, Husband, Parents, Kids, Friend |

## Usage Examples

```
ELI5 what a database index is
Explain this code to my manager
Break down how git merge conflicts work for a 5th grader
Explain this error to my mom
Simplify this for a designer
```

## How It Works

The skill detects the target audience from your prompt and calibrates:

- **Vocabulary** — no jargon for kids, proper terminology for engineers
- **Analogies** — toys and playground for age 5, business outcomes for managers
- **Tone** — playful for children, professional for directors, warm for family
- **Depth** — short and sweet for simple audiences, nuanced for grad students
- **Framing** — impact/risk for managers, UX for designers, architecture for engineers

## Installation

Copy the skill into your Claude Code skills directory:

```bash
git clone https://github.com/DreambigOu/ELI5.git
cp -r ELI5/skills/eli5 ~/.claude/skills/eli5
```

Then use it in Claude Code by saying things like "ELI5 this" or "explain this to my manager."

## Running Evaluations

You can run the eval suite locally to test the skill yourself.

**Prerequisites:** [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and the skill installed at `~/.claude/skills/eli5/`.

```bash
# Run all 3 tests + auto-grade with pass/fail
./eli5-workspace/run-evals.sh

# Run a single test
./eli5-workspace/run-evals.sh --test=1

# Skip baseline, only test the skill
./eli5-workspace/run-evals.sh --with-skill-only

# Grade existing outputs without re-running tests
./eli5-workspace/run-evals.sh --grade-only
```

The script runs each test case, then uses Claude to auto-grade every output against predefined assertions. You'll see per-assertion pass/fail results and a summary like:

```
=========================================
  PASS RATE SUMMARY — Iteration 2
=========================================
  With Skill:    11/12 passed (91.6%)
  Without Skill: 4/12 passed (33.3%)
  Delta:         58.3%
=========================================
```

Results are saved to `eli5-workspace/iteration-N/` with each run auto-incrementing the iteration number. Each test case produces `grading.txt` files with detailed pass/fail evidence.

### Test Cases

| # | Prompt | Audience |
|---|--------|----------|
| 1 | "ELI5 what a database index is" | Age 5 (default) |
| 2 | "Explain a typical web application codebase's structure to my manager" | Manager |
| 3 | "Break down how git merge conflicts work for a 5th grader" | 5th grade |

### Results

See [eli5-workspace/eval-results.md](eli5-workspace/eval-results.md) for the full evaluation strategy and detailed grading.

| Metric | With Skill | Without Skill | Delta |
|--------|-----------|---------------|-------|
| Pass Rate | **91.7%** | 33.3% | +58.3% |
| Avg Time | 33.0s | 47.4s | -14.4s |

The biggest improvement is in audience-specific framing — especially for non-technical audiences like managers (0% baseline to 75% with skill).

## Contributing

PRs welcome! Ideas for improvement:

- Add more audience types (e.g., CEO, intern, journalist)
- Add non-English language support
- Improve evaluation coverage with more test cases

## License

MIT

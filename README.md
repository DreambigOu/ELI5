# ELI5 — Explain Like I Am 5

> A [Claude Code](https://claude.ai) skill that explains anything to anyone — kids, managers, engineers, parents. It adapts tone, vocabulary, analogies, and framing to match the audience.

Ever needed to explain a technical concept to your manager? Or break down code for a 5th grader? ELI5 makes Claude automatically adjust its explanation style based on who's listening.

Read the full blog post on how this skill was built: [Building an ELI5 Skill for Claude](https://andrewou.pages.dev/posts/building-an-eli5-skill-for-claude/)

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

## Evaluations

### Adding a New Test Case

Test cases are defined in `eli5-workspace/evals.json`. Add a new entry to the `evals` array:

```json
{
  "id": 3,
  "name": "explain-recursion-teenager",
  "prompt": "Explain recursion like I'm 15",
  "audience": "Age 15",
  "assertions": [
    "Uses social media, gaming, or phone references as analogies",
    "Tone is casual but not cringey — no 'fellow kids' energy",
    "Correctly explains the concept of a function calling itself",
    "Mentions a base case or stopping condition"
  ]
}
```

Each test case needs:
- A **prompt** — what the user would say to Claude
- A **name** — directory-friendly identifier for storing results
- **Assertions** — specific, verifiable criteria to grade against (4 per test works well)

### Running Evaluations

**Prerequisites:** [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and the skill installed at `~/.claude/skills/eli5/`.

```bash
# Run all tests + auto-grade with pass/fail
python eli5-workspace/run-evals.py

# Run a single test
python eli5-workspace/run-evals.py --test=1

# Skip baseline, only test the skill
python eli5-workspace/run-evals.py --with-skill-only

# Grade existing outputs without re-running tests
python eli5-workspace/run-evals.py --grade-only
```

The script does three things:
1. **Runs each prompt** twice — once with the skill, once without (baseline)
2. **Auto-grades** every output against its assertions using Claude
3. **Prints a pass rate summary** comparing skill vs baseline

Example output:

```
--- Test 1: explain-db-index-age5 ---
  [with skill]
    PASS  #1 — No technical jargon present
    PASS  #2 — Uses book/page analogy and toy/messy room analogy
    PASS  #3 — Sentences are short and conversational
    PASS  #4 — Warm, enthusiastic tone with "huuuge", "super duper fast"
  [baseline]
    PASS  #1 — No technical jargon found
    FAIL  #2 — Uses phone book analogy, not child-friendly
    PASS  #3 — Sentences are generally short
    FAIL  #4 — Tone is informative but encyclopedic

=========================================
  PASS RATE SUMMARY — Iteration 1
=========================================
  With Skill:    10/12 passed (83.3%)
  Without Skill: 5/12 passed (41.6%)
  Delta:         41.7%
=========================================
```

Results are saved to `eli5-workspace/iteration-N/`, auto-incrementing with each run. Each test case produces `grading.txt` files with detailed evidence.

### Current Results

See [eli5-workspace/eval-results.md](eli5-workspace/eval-results.md) for the full evaluation strategy and detailed grading.

| Metric | With Skill | Without Skill | Delta |
|--------|-----------|---------------|-------|
| Pass Rate | **83.3%** | 41.6% | +41.7% |

The biggest improvement is in audience-specific framing — especially for non-technical audiences like managers (0% baseline to 50% with skill).

## Contributing

PRs welcome! Ideas for improvement:

- Add more audience types (e.g., CEO, intern, journalist)
- Add non-English language support
- Improve evaluation coverage with more test cases

## License

MIT

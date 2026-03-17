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

## Evaluation Results

Tested across 3 audience types with quantitative assertions. See [eli5-workspace/eval-results.md](eli5-workspace/eval-results.md) for full details.

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

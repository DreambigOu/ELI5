# ELI5 — Explain Like I Am 5

A Claude Code skill that explains any topic tailored to a specific audience's level of understanding.

## What It Does

Give Claude a topic and an audience, and it adapts the explanation's language, analogies, complexity, and framing to match.

### Supported Audiences

| Category | Examples |
|----------|---------|
| **Ages** | 5, 10, 15, 20, 30, 40+ |
| **Grade Levels** | 5th grade, Middle school, Senior High, College, Graduate school |
| **Job Roles** | Manager, Engineer, Designer, Director, Product Manager |
| **Relationships** | Wife, Husband, Parents, Kids, Friend |

### Usage Examples

```
ELI5 what a database index is
Explain this code to my manager
Break down how git merge conflicts work for a 5th grader
Explain this error to my mom
Simplify this for a designer
```

## Installation

Copy the skill into your Claude Code skills directory:

```bash
cp -r skills/eli5 ~/.claude/skills/eli5
```

## Evaluation Results

See [eli5-workspace/eval-results.md](eli5-workspace/eval-results.md) for detailed evaluation results.

**Summary:** 91.7% assertion pass rate with the skill vs. 33.3% baseline — the biggest improvement is in audience-specific framing (tone, vocabulary, structure).

## License

MIT

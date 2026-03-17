# ELI5 Skill — Evaluation Strategy & Results

## Evaluation Strategy

### Goal
Validate that the ELI5 skill produces audience-calibrated explanations that meaningfully differ from baseline Claude output (no skill).

### Test Cases
Three test cases covering different audience types:

1. **explain-db-index-age5** — "ELI5 what a database index is" (Age 5, default)
2. **explain-codebase-manager** — "Explain this codebase's structure to my manager" (Job role: Manager)
3. **explain-git-merge-5th-grader** — "Break down how git merge conflicts work for a 5th grader" (Grade level: 5th grade)

### Methodology
- Each test case was run twice: once **with the skill** and once **without** (baseline)
- All 6 runs were launched in parallel as independent subagents
- Outputs were graded against predefined assertions per test case

### Assertions

**Test 1 — Age 5 (DB Index):**
| Assertion | Description |
|-----------|-------------|
| no-jargon | No technical terms (query, B-tree, schema, SQL, optimize) |
| uses-analogy | At least one concrete, child-friendly analogy |
| short-sentences | Average sentence length under 15 words |
| appropriate-tone | Warm, playful tone suitable for a 5-year-old |

**Test 2 — Manager (Codebase):**
| Assertion | Description |
|-----------|-------------|
| no-code-snippets | Zero code blocks or inline code |
| business-framing | Frames in business terms (impact, decisions, risk) |
| concise | Under 500 words |
| actionable | Includes recommendations or decision points |

**Test 3 — 5th Grader (Git Merge):**
| Assertion | Description |
|-----------|-------------|
| no-jargon | No unexplained advanced git terms |
| uses-analogy | Relatable analogy for age 10-11 |
| step-by-step | Logical sequential flow |
| grade-appropriate | Vocabulary appropriate for 5th grade level |

---

## Results

### Summary

| Metric | With Skill | Without Skill | Delta |
|--------|-----------|---------------|-------|
| **Pass Rate** | 91.7% | 33.3% | **+58.3%** |
| **Avg Time** | 33.0s | 47.4s | -14.4s |
| **Avg Tokens** | 12,430 | 10,076 | +2,354 |

### Per-Test Breakdown

#### Test 1: ELI5 Database Index (Age 5)

| Assertion | With Skill | Without Skill |
|-----------|-----------|---------------|
| no-jargon | PASS | FAIL — uses "trade-off", dated "phone book" reference |
| uses-analogy | PASS — book + messy room | PASS — phone book (dated) |
| short-sentences | PASS | FAIL — several 25+ word sentences |
| appropriate-tone | PASS — "Oh, this is a cool one!" | FAIL — encyclopedic, lacks warmth |
| **Total** | **4/4** | **1/4** |

#### Test 2: Codebase Structure for Manager

| Assertion | With Skill | Without Skill |
|-----------|-----------|---------------|
| no-code-snippets | FAIL — inline backticks for folder names | FAIL — large code block with folder tree |
| business-framing | PASS — timelines, risk, capacity | FAIL — technical framing |
| concise | PASS — ~350 words | FAIL — ~800+ words |
| actionable | PASS — 4 decision-oriented bullets | FAIL — no action items |
| **Total** | **3/4** | **0/4** |

#### Test 3: Git Merge Conflicts for 5th Grader

| Assertion | With Skill | Without Skill |
|-----------|-----------|---------------|
| no-jargon | PASS | FAIL — "stage" and "commit" unexplained |
| uses-analogy | PASS — group project/poster | PASS — shared notebook, cooking |
| step-by-step | PASS | PASS |
| grade-appropriate | PASS | PASS |
| **Total** | **4/4** | **3/4** |

### Key Observations

1. **Biggest impact: Manager audience.** The skill turned a 0/4 baseline into 3/4. Without guidance, Claude defaults to technical explanations with code blocks — the skill successfully reframes for business context.
2. **Age calibration is strong.** The skill nailed the age-5 tone (playful, short sentences, fun analogies) while the baseline wrote at an adult level despite the ELI5 prompt.
3. **Minor issue: inline code formatting.** The with-skill manager response still used backtick formatting for folder names — a borderline fail on the "no code snippets" assertion. Could be addressed by adding explicit guidance to avoid all code formatting for non-technical audiences.
4. **Token trade-off is acceptable.** The skill uses ~23% more tokens but produces significantly better-calibrated output and is actually faster on average.

### Timing Data

| Test Case | With Skill | Without Skill |
|-----------|-----------|---------------|
| DB Index (age 5) | 25.7s / 11,907 tokens | 26.4s / 9,518 tokens |
| Codebase (manager) | 37.6s / 12,962 tokens | 43.4s / 10,650 tokens |
| Git Merge (5th grader) | 35.8s / 12,421 tokens | 72.4s / 10,061 tokens |

---

## Iteration Notes

### Iteration 1 (current)
- Initial skill draft
- 91.7% pass rate vs 33.3% baseline
- One known improvement: add guidance to avoid inline code formatting for non-technical audiences

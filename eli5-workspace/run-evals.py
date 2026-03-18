#!/usr/bin/env python3
from __future__ import annotations

"""ELI5 Skill Evaluation Runner

Runs each test case across one or more skill configurations, then auto-grades with pass/fail.

Prerequisites:
  - claude CLI installed (npm install -g @anthropic-ai/claude-code)
  - Skill file(s) accessible on disk

Usage:
  # Skill vs baseline (default — uses installed skill)
  python run-evals.py

  # A/B test two skill versions
  python run-evals.py --a skills/eli5/SKILL.md --b ~/experiments/SKILL-v2.md

  # A/B with custom labels
  python run-evals.py --a skills/eli5/SKILL.md --a-label current --b ~/new/SKILL.md --b-label rewrite

  # Single skill only (no comparison)
  python run-evals.py --a skills/eli5/SKILL.md

  # Other options
  python run-evals.py --test=1           # Run only test 1
  python run-evals.py --grade-only       # Grade existing outputs without re-running
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EVALS_JSON = SCRIPT_DIR / "evals.json"
DEFAULT_SKILL = Path.home() / ".claude" / "skills" / "eli5" / "SKILL.md"


def load_evals():
    with open(EVALS_JSON) as f:
        return json.load(f)["evals"]


def find_iteration(grade_only: bool) -> int:
    iteration = 1
    if grade_only:
        while (SCRIPT_DIR / f"iteration-{iteration + 1}").is_dir():
            iteration += 1
    else:
        while (SCRIPT_DIR / f"iteration-{iteration}").is_dir():
            iteration += 1
    return iteration


def run_claude(prompt: str) -> str:
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "text"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  claude CLI error: {result.stderr.strip()}", file=sys.stderr)
    return result.stdout.strip()


def run_test(eval_case: dict, outdir: Path, configs: list[dict]):
    name = eval_case["name"]
    prompt = eval_case["prompt"]
    print(f"--- Test {eval_case['id'] + 1}: {name} ---")

    for config in configs:
        config_dir = outdir / name / config["dir_name"] / "outputs"
        config_dir.mkdir(parents=True, exist_ok=True)
        print(f"  [{config['label']}] Running...")
        start = time.time()
        if config["skill_path"]:
            response = run_claude(
                f"Read the skill at {config['skill_path']} first, then follow its instructions. Task: {prompt}"
            )
        else:
            response = run_claude(prompt)
        elapsed = time.time() - start
        (config_dir / "response.md").write_text(response)
        (config_dir.parent / "timing.json").write_text(
            json.dumps({"seconds": round(elapsed, 2)})
        )
        print(f"  [{config['label']}] Done ({elapsed:.1f}s)")

    print()


def grade_response(response_file: Path, assertions: list[str]) -> str:
    response_content = response_file.read_text()
    assertions_text = "\n".join(
        f"{i + 1}. {a}" for i, a in enumerate(assertions)
    )
    return run_claude(
        f"""You are a strict grader. Grade this response against each assertion.

RESPONSE:
{response_content}

ASSERTIONS:
{assertions_text}

For each assertion, output exactly one line:
PASS|<number>|<brief evidence>
or
FAIL|<number>|<brief evidence>

Output ONLY those lines. No other text."""
    )


def parse_grades(grade_output: str, expected_count: int) -> list[tuple[str, str, str]]:
    results = []
    for line in grade_output.strip().splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            verdict = parts[0].strip()
            if verdict in ("PASS", "FAIL"):
                results.append((verdict, parts[1].strip(), parts[2].strip()))
                if len(results) == expected_count:
                    break
    return results


def grade_all(evals: list[dict], outdir: Path, configs: list[dict], test_filter: int | None):
    print("=== Grading ===\n")

    # Track totals per config
    totals = {c["dir_name"]: {"pass": 0, "total": 0} for c in configs}

    for eval_case in evals:
        if test_filter is not None and eval_case["id"] != test_filter:
            continue

        name = eval_case["name"]
        assertions = eval_case["assertions"]
        print(f"--- Test {eval_case['id'] + 1}: {name} ---")

        for config in configs:
            response_file = outdir / name / config["dir_name"] / "outputs" / "response.md"
            if not response_file.exists():
                continue

            print(f"  [{config['label']}]")
            grade_output = grade_response(response_file, assertions)
            grading_dir = outdir / name / config["dir_name"]
            (grading_dir / "grading.txt").write_text(grade_output)

            grades = parse_grades(grade_output, len(assertions))
            grade_data = []
            for verdict, num, evidence in grades:
                print(f"    {verdict}  #{num} — {evidence}")
                grade_data.append({"assertion": int(num), "verdict": verdict, "evidence": evidence})
                totals[config["dir_name"]]["total"] += 1
                if verdict == "PASS":
                    totals[config["dir_name"]]["pass"] += 1

            (grading_dir / "grading.json").write_text(json.dumps(grade_data, indent=2))

        print()

    # Summary
    iteration_num = outdir.name.split("-")[-1]
    print("=========================================")
    print(f"  PASS RATE SUMMARY — Iteration {iteration_num}")
    print("=========================================")

    rates = {}
    for config in configs:
        t = totals[config["dir_name"]]
        if t["total"] > 0:
            rate = t["pass"] * 100 / t["total"]
            rates[config["dir_name"]] = rate
            print(f"  {config['label']:15s} {t['pass']}/{t['total']} passed ({rate:.1f}%)")

    if len(rates) == 2:
        keys = list(rates)
        delta = rates[keys[0]] - rates[keys[1]]
        print(f"  {'Delta':15s} {delta:+.1f}%")

    print("=========================================")

    # Save summary
    summary_lines = [
        f"ELI5 Eval Summary — Iteration {iteration_num}",
        f"Date: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    for config in configs:
        t = totals[config["dir_name"]]
        if t["total"] > 0:
            summary_lines.append(f"{config['label']}: {t['pass']}/{t['total']} passed")
    (outdir / "summary.txt").write_text("\n".join(summary_lines) + "\n")

    # Save config metadata
    config_meta = {
        "configs": [
            {"label": c["label"], "dir_name": c["dir_name"],
             "skill_path": str(c["skill_path"]) if c["skill_path"] else None}
            for c in configs
        ]
    }
    (outdir / "config.json").write_text(json.dumps(config_meta, indent=2) + "\n")

    print(f"\nGrading details: {outdir}/*/<config>/grading.txt")


def build_configs(args) -> list[dict]:
    """Build the list of configs to run based on CLI args."""
    configs = []

    if args.a and args.b:
        # A/B test: two skill versions
        configs.append({
            "label": args.a_label or "A",
            "dir_name": args.a_label or "a",
            "skill_path": Path(args.a).resolve(),
        })
        configs.append({
            "label": args.b_label or "B",
            "dir_name": args.b_label or "b",
            "skill_path": Path(args.b).resolve(),
        })
    elif args.a:
        # Single skill, no comparison
        configs.append({
            "label": args.a_label or "skill",
            "dir_name": args.a_label or "with_skill",
            "skill_path": Path(args.a).resolve(),
        })
    else:
        # Default: installed skill vs baseline
        configs.append({
            "label": "with skill",
            "dir_name": "with_skill",
            "skill_path": DEFAULT_SKILL,
        })
        configs.append({
            "label": "baseline",
            "dir_name": "without_skill",
            "skill_path": None,
        })

    return configs


def main():
    parser = argparse.ArgumentParser(description="ELI5 Skill Evaluation Runner")
    parser.add_argument("--test", type=int, help="Run only this test number (1-indexed)")
    parser.add_argument("--grade-only", action="store_true", help="Grade existing outputs without re-running")
    parser.add_argument("--a", metavar="PATH", help="Path to skill version A")
    parser.add_argument("--a-label", metavar="LABEL", help="Label for version A (default: 'A')")
    parser.add_argument("--b", metavar="PATH", help="Path to skill version B")
    parser.add_argument("--b-label", metavar="LABEL", help="Label for version B (default: 'B')")
    args = parser.parse_args()

    if args.b and not args.a:
        parser.error("--b requires --a")

    configs = build_configs(args)
    evals = load_evals()
    iteration = find_iteration(args.grade_only)
    outdir = SCRIPT_DIR / f"iteration-{iteration}"

    test_filter = (args.test - 1) if args.test else None

    print("=== ELI5 Eval Runner ===")
    print(f"Output: {outdir}")
    for c in configs:
        src = c["skill_path"] or "(no skill)"
        print(f"  {c['label']}: {src}")
    print()

    # Check prerequisites
    if not args.grade_only:
        if subprocess.run(["which", "claude"], capture_output=True).returncode != 0:
            print("Error: 'claude' CLI not found. Install with: npm install -g @anthropic-ai/claude-code")
            sys.exit(1)
        for c in configs:
            if c["skill_path"] and not c["skill_path"].exists():
                print(f"Error: Skill not found at {c['skill_path']}")
                sys.exit(1)

        for eval_case in evals:
            if test_filter is not None and eval_case["id"] != test_filter:
                continue
            run_test(eval_case, outdir, configs)

        print("=== Tests Complete ===\n")

    grade_all(evals, outdir, configs, test_filter)
    print("\n=== All Done! ===")


if __name__ == "__main__":
    main()

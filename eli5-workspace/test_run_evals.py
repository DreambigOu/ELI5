from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import pytest

import importlib
run_evals = importlib.import_module("run-evals")


# -- Fixtures --

@pytest.fixture
def tmp_workspace(tmp_path, monkeypatch):
    """Set up a temporary workspace with evals.json and patch SCRIPT_DIR."""
    evals_data = {
        "skill_name": "eli5",
        "evals": [
            {
                "id": 0,
                "name": "test-case-one",
                "prompt": "ELI5 what a widget is",
                "audience": "Age 5",
                "assertions": ["No jargon", "Uses a toy analogy"],
            },
            {
                "id": 1,
                "name": "test-case-two",
                "prompt": "Explain widgets to my manager",
                "audience": "Manager",
                "assertions": ["No code blocks", "Under 500 words", "Actionable"],
            },
        ],
    }
    (tmp_path / "evals.json").write_text(json.dumps(evals_data))
    monkeypatch.setattr(run_evals, "SCRIPT_DIR", tmp_path)
    monkeypatch.setattr(run_evals, "EVALS_JSON", tmp_path / "evals.json")
    return tmp_path


@pytest.fixture
def skill_files(tmp_path):
    """Create dummy skill files for A/B testing."""
    skill_a = tmp_path / "skill_a.md"
    skill_b = tmp_path / "skill_b.md"
    skill_a.write_text("# Skill A")
    skill_b.write_text("# Skill B")
    return skill_a, skill_b


# -- load_evals --

class TestLoadEvals:
    def test_loads_from_evals_json(self, tmp_workspace):
        evals = run_evals.load_evals()
        assert len(evals) == 2
        assert evals[0]["name"] == "test-case-one"
        assert evals[1]["name"] == "test-case-two"

    def test_returns_assertions(self, tmp_workspace):
        evals = run_evals.load_evals()
        assert evals[0]["assertions"] == ["No jargon", "Uses a toy analogy"]
        assert len(evals[1]["assertions"]) == 3


# -- find_iteration --

class TestFindIteration:
    def test_returns_1_when_no_iterations_exist(self, tmp_workspace):
        assert run_evals.find_iteration(grade_only=False) == 1

    def test_returns_next_iteration(self, tmp_workspace):
        (tmp_workspace / "iteration-1").mkdir()
        (tmp_workspace / "iteration-2").mkdir()
        assert run_evals.find_iteration(grade_only=False) == 3

    def test_grade_only_returns_latest_existing(self, tmp_workspace):
        (tmp_workspace / "iteration-1").mkdir()
        (tmp_workspace / "iteration-2").mkdir()
        assert run_evals.find_iteration(grade_only=True) == 2

    def test_grade_only_returns_1_when_only_one_exists(self, tmp_workspace):
        (tmp_workspace / "iteration-1").mkdir()
        assert run_evals.find_iteration(grade_only=True) == 1


# -- parse_grades --

class TestParseGrades:
    def test_parses_clean_output(self):
        output = "PASS|1|No jargon found\nFAIL|2|Missing analogy"
        result = run_evals.parse_grades(output, expected_count=2)
        assert result == [
            ("PASS", "1", "No jargon found"),
            ("FAIL", "2", "Missing analogy"),
        ]

    def test_caps_at_expected_count(self):
        output = (
            "PASS|1|Good\n"
            "PASS|2|Good\n"
            "PASS|1|Duplicate grading\n"
            "FAIL|2|Duplicate grading"
        )
        result = run_evals.parse_grades(output, expected_count=2)
        assert len(result) == 2

    def test_ignores_non_grade_lines(self):
        output = (
            "Here are my grades:\n"
            "PASS|1|Evidence one\n"
            "\n"
            "FAIL|2|Evidence two\n"
            "Some trailing text"
        )
        result = run_evals.parse_grades(output, expected_count=2)
        assert len(result) == 2
        assert result[0][0] == "PASS"
        assert result[1][0] == "FAIL"

    def test_handles_empty_output(self):
        assert run_evals.parse_grades("", expected_count=4) == []

    def test_handles_pipes_in_evidence(self):
        output = "PASS|1|Response uses table/column|row correctly"
        result = run_evals.parse_grades(output, expected_count=1)
        assert result[0] == ("PASS", "1", "Response uses table/column|row correctly")

    def test_strips_whitespace_from_verdict(self):
        output = "  PASS  |  1  | Good"
        result = run_evals.parse_grades(output, expected_count=1)
        assert result[0] == ("PASS", "1", "Good")


# -- build_configs --

class TestBuildConfigs:
    def _args(self, **kwargs):
        defaults = {"a": None, "a_label": None, "b": None, "b_label": None}
        defaults.update(kwargs)
        return argparse.Namespace(**defaults)

    def test_default_skill_vs_baseline(self):
        configs = run_evals.build_configs(self._args())
        assert len(configs) == 2
        assert configs[0]["label"] == "with skill"
        assert configs[0]["skill_path"] == run_evals.DEFAULT_SKILL
        assert configs[1]["label"] == "baseline"
        assert configs[1]["skill_path"] is None

    def test_ab_test_two_skills(self, skill_files):
        a, b = skill_files
        configs = run_evals.build_configs(self._args(a=str(a), b=str(b)))
        assert len(configs) == 2
        assert configs[0]["label"] == "A"
        assert configs[0]["dir_name"] == "a"
        assert configs[0]["skill_path"] == a
        assert configs[1]["label"] == "B"
        assert configs[1]["dir_name"] == "b"
        assert configs[1]["skill_path"] == b

    def test_ab_with_custom_labels(self, skill_files):
        a, b = skill_files
        configs = run_evals.build_configs(
            self._args(a=str(a), b=str(b), a_label="current", b_label="rewrite")
        )
        assert configs[0]["label"] == "current"
        assert configs[0]["dir_name"] == "current"
        assert configs[1]["label"] == "rewrite"
        assert configs[1]["dir_name"] == "rewrite"

    def test_single_skill_only(self, skill_files):
        a, _ = skill_files
        configs = run_evals.build_configs(self._args(a=str(a)))
        assert len(configs) == 1
        assert configs[0]["label"] == "skill"
        assert configs[0]["dir_name"] == "with_skill"

    def test_single_skill_with_label(self, skill_files):
        a, _ = skill_files
        configs = run_evals.build_configs(self._args(a=str(a), a_label="v2"))
        assert len(configs) == 1
        assert configs[0]["label"] == "v2"
        assert configs[0]["dir_name"] == "v2"


# -- run_test --

class TestRunTest:
    def test_creates_output_files_for_each_config(self, tmp_workspace):
        eval_case = {"id": 0, "name": "test-case", "prompt": "Explain X"}
        outdir = tmp_workspace / "iteration-1"
        configs = [
            {"label": "A", "dir_name": "a", "skill_path": Path("/fake/skill.md")},
            {"label": "B", "dir_name": "b", "skill_path": Path("/fake/skill2.md")},
        ]
        with patch.object(run_evals, "run_claude", return_value="mock response"):
            run_evals.run_test(eval_case, outdir, configs)

        for dir_name in ("a", "b"):
            response = outdir / "test-case" / dir_name / "outputs" / "response.md"
            timing = outdir / "test-case" / dir_name / "timing.json"
            assert response.exists()
            assert response.read_text() == "mock response"
            assert timing.exists()
            data = json.loads(timing.read_text())
            assert "seconds" in data

    def test_baseline_config_skips_skill_in_prompt(self, tmp_workspace):
        eval_case = {"id": 0, "name": "test-case", "prompt": "Explain X"}
        outdir = tmp_workspace / "iteration-1"
        configs = [{"label": "baseline", "dir_name": "baseline", "skill_path": None}]
        prompts_received = []
        with patch.object(run_evals, "run_claude", side_effect=lambda p: (prompts_received.append(p), "resp")[1]):
            run_evals.run_test(eval_case, outdir, configs)

        assert len(prompts_received) == 1
        assert "Read the skill" not in prompts_received[0]
        assert prompts_received[0] == "Explain X"

    def test_skill_config_includes_skill_path_in_prompt(self, tmp_workspace):
        eval_case = {"id": 0, "name": "test-case", "prompt": "Explain X"}
        outdir = tmp_workspace / "iteration-1"
        skill_path = Path("/my/skill.md")
        configs = [{"label": "A", "dir_name": "a", "skill_path": skill_path}]
        prompts_received = []
        with patch.object(run_evals, "run_claude", side_effect=lambda p: (prompts_received.append(p), "resp")[1]):
            run_evals.run_test(eval_case, outdir, configs)

        assert "/my/skill.md" in prompts_received[0]
        assert "Explain X" in prompts_received[0]


# -- grade_all --

class TestGradeAll:
    def _setup_responses(self, outdir, evals, configs):
        """Write dummy response files for grading."""
        for ev in evals:
            for c in configs:
                resp_dir = outdir / ev["name"] / c["dir_name"] / "outputs"
                resp_dir.mkdir(parents=True, exist_ok=True)
                (resp_dir / "response.md").write_text("Some explanation text")

    def test_writes_grading_files(self, tmp_workspace):
        evals = run_evals.load_evals()
        outdir = tmp_workspace / "iteration-1"
        configs = [
            {"label": "A", "dir_name": "a", "skill_path": Path("/fake")},
            {"label": "B", "dir_name": "b", "skill_path": Path("/fake")},
        ]
        self._setup_responses(outdir, evals, configs)

        grade_output = "PASS|1|Good\nPASS|2|Good"
        with patch.object(run_evals, "run_claude", return_value=grade_output):
            run_evals.grade_all(evals, outdir, configs, test_filter=None)

        for ev in evals:
            for c in configs:
                grading_dir = outdir / ev["name"] / c["dir_name"]
                assert (grading_dir / "grading.txt").exists()
                assert (grading_dir / "grading.json").exists()
                data = json.loads((grading_dir / "grading.json").read_text())
                assert all(g["verdict"] == "PASS" for g in data)

    def test_writes_summary_and_config(self, tmp_workspace):
        evals = run_evals.load_evals()
        outdir = tmp_workspace / "iteration-1"
        configs = [
            {"label": "A", "dir_name": "a", "skill_path": Path("/fake")},
        ]
        self._setup_responses(outdir, evals, configs)

        grade_output = "PASS|1|Good\nFAIL|2|Bad"
        with patch.object(run_evals, "run_claude", return_value=grade_output):
            run_evals.grade_all(evals, outdir, configs, test_filter=None)

        assert (outdir / "summary.txt").exists()
        assert "A:" in (outdir / "summary.txt").read_text()
        assert (outdir / "config.json").exists()
        meta = json.loads((outdir / "config.json").read_text())
        assert meta["configs"][0]["label"] == "A"

    def test_test_filter_limits_grading(self, tmp_workspace):
        evals = run_evals.load_evals()
        outdir = tmp_workspace / "iteration-1"
        configs = [{"label": "A", "dir_name": "a", "skill_path": Path("/fake")}]
        self._setup_responses(outdir, evals, configs)

        call_count = 0
        def counting_claude(prompt):
            nonlocal call_count
            call_count += 1
            return "PASS|1|Good\nPASS|2|Good"

        with patch.object(run_evals, "run_claude", side_effect=counting_claude):
            run_evals.grade_all(evals, outdir, configs, test_filter=0)

        # Only test 0 graded, so run_claude called once (1 config * 1 test)
        assert call_count == 1

    def test_skips_missing_response_files(self, tmp_workspace):
        evals = run_evals.load_evals()
        outdir = tmp_workspace / "iteration-1"
        configs = [{"label": "A", "dir_name": "a", "skill_path": Path("/fake")}]
        # Create outdir but no response files
        outdir.mkdir(parents=True, exist_ok=True)

        with patch.object(run_evals, "run_claude", return_value="PASS|1|Good") as mock:
            run_evals.grade_all(evals, outdir, configs, test_filter=None)

        mock.assert_not_called()

    def test_delta_printed_for_two_configs(self, tmp_workspace, capsys):
        evals = run_evals.load_evals()
        outdir = tmp_workspace / "iteration-1"
        configs = [
            {"label": "A", "dir_name": "a", "skill_path": Path("/fake")},
            {"label": "B", "dir_name": "b", "skill_path": Path("/fake")},
        ]
        self._setup_responses(outdir, evals, configs)

        def mock_grade(prompt):
            return "PASS|1|Good\nPASS|2|Good\nPASS|3|Good"

        with patch.object(run_evals, "run_claude", side_effect=mock_grade):
            run_evals.grade_all(evals, outdir, configs, test_filter=None)

        output = capsys.readouterr().out
        assert "Delta" in output

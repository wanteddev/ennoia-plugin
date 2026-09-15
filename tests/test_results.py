"""Host 기록에서 합성 성공과 미측정 수치의 혼동을 거절한다."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "evals/results/2026-09-15-dogfooding-schema.json"
RECORDS = ROOT / "evals/results/2026-09-15-host-cases.json"


class ResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("ennoia_results", ROOT / "scripts/validate_results.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.validate = staticmethod(module.validate_records)
        cls.records = json.loads(RECORDS.read_text(encoding="utf-8"))

    def test_sanitized_host_cases_validate(self):
        self.assertEqual(self.validate(self.records, SCHEMA), [])

    def test_missing_required_and_unknown_keys_rejected(self):
        invalid = copy.deepcopy(self.records)
        invalid[0].pop("connection_source")
        invalid[1]["credential"] = "fixture-only"
        self.assertTrue(self.validate(invalid, SCHEMA))

    def test_wrong_types_and_negative_measurements_rejected(self):
        invalid = copy.deepcopy(self.records)
        invalid[0]["tool_calls"] = False
        invalid[1]["measurement"]["input_tokens"] = -1
        self.assertTrue(self.validate(invalid, SCHEMA))

    def test_unattempted_case_cannot_have_observed_calls_or_measurements(self):
        invalid = copy.deepcopy(self.records)
        invalid[0]["tool_calls"] = 1
        invalid[1]["measurement"]["elapsed_ms"] = 0
        self.assertTrue(self.validate(invalid, SCHEMA))

    def test_static_success_cannot_be_host_pass(self):
        invalid = copy.deepcopy(self.records)
        invalid[0]["result"] = "pass"
        invalid[0]["evidence_kind"] = "synthetic"
        self.assertTrue(self.validate(invalid, SCHEMA))

    def test_duplicate_case_and_inconsistent_response_size_rejected(self):
        invalid = copy.deepcopy(self.records)
        invalid.append(copy.deepcopy(invalid[0]))
        self.assertTrue(self.validate(invalid, SCHEMA))
        invalid.pop()
        invalid[0]["result"] = "blocked"
        invalid[0]["measurement"]["response_chars"] = 10
        invalid[0]["measurement"]["response_utf8_bytes"] = 1
        self.assertTrue(self.validate(invalid, SCHEMA))

    def test_current_session_read_does_not_become_candidate_install(self):
        current = json.loads((ROOT / "evals/results/2026-09-15-current-session-read.json").read_text(encoding="utf-8"))
        self.assertEqual(self.validate(current, SCHEMA), [])
        self.assertEqual({case["plugin_version"] for case in current}, {"1.0.2"})
        self.assertEqual({case["connection_source"] for case in current}, {"unknown"})
        self.assertEqual({case["case_id"] for case in current}, {"current-project-read", "current-context-read"})
        current[0]["case_stage"] = "git_install"
        self.assertTrue(self.validate(current, SCHEMA))

    def test_unmeasured_host_pass_or_unproven_core_run_rejected(self):
        invalid = copy.deepcopy(self.records)
        case = invalid[0]
        case.update(result="pass", evidence_kind="native_host", observed_at="2026-09-15T10:00:00Z", host_version="0.153.4")
        case["tool_calls"] = None
        self.assertTrue(self.validate(invalid, SCHEMA))
        case["tool_calls"] = 0
        case["case_stage"] = "core_run"
        case["case_id"] = "hypothetical-run"
        self.assertTrue(self.validate(invalid, SCHEMA))

    def test_performance_pass_needs_trial_provenance(self):
        invalid = copy.deepcopy(self.records)
        case = next(record for record in invalid if record["case_stage"] == "performance")
        case.update(result="pass", evidence_kind="native_host", observed_at="2026-09-15T10:00:00Z", host_version="0.153.4", loaded_skill_version="1.1.0")
        self.assertTrue(any("trial" in error for error in self.validate(invalid, SCHEMA)))

    def test_invalid_calendar_and_version_mismatch_rejected(self):
        invalid = copy.deepcopy(self.records)
        invalid[0]["recorded_at"] = "2026-02-30T10:00:00Z"
        self.assertTrue(any("calendar" in error for error in self.validate(invalid, SCHEMA)))
        invalid[0]["recorded_at"] = "2026-09-15T10:00:00Z"
        invalid[0].update(result="pass", evidence_kind="native_host", observed_at="2026-09-15T09:00:00Z", host_version="0.153.4", loaded_skill_version="1.0.2")
        invalid[0]["case_stage"] = "fresh_skill"
        self.assertTrue(any("불일치" in error for error in self.validate(invalid, SCHEMA)))

    def test_malformed_enum_objects_are_rejected_without_crash(self):
        invalid = copy.deepcopy(self.records)
        invalid[0]["result"] = {"state": "pass"}
        invalid[1]["case_stage"] = ["core_run"]
        invalid[2]["evidence_kind"] = {"source": "native_host"}
        self.assertTrue(self.validate(invalid, SCHEMA))

    def test_native_candidate_reads_preserve_unknown_connection_source(self):
        native = json.loads((ROOT / "evals/results/2026-09-15-codex-cli-native-read.json").read_text(encoding="utf-8"))
        self.assertEqual(self.validate(native, SCHEMA), [])
        self.assertEqual({case["connection_source"] for case in native}, {"unknown"})
        self.assertEqual({case["case_stage"] for case in native}, {"read"})
        install_skill = [case for case in self.records if case["host"] == "codex-cli" and case["case_id"] in {"git-install", "fresh-skill"}]
        self.assertEqual({case["result"] for case in install_skill}, {"pass"})
        core = [case for case in self.records if case["case_stage"] == "core_run"]
        self.assertEqual({case["result"] for case in core}, {"not_tested"})


if __name__ == "__main__":
    unittest.main()

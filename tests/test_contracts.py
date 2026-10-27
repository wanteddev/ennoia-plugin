"""도구명은 같아도 Skill이 사용하는 입력·출력 계약이 달라지는 회귀를 검증한다."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_contracts import validate_contracts

ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def setUp(self):
        fixtures = ROOT / "tests/fixtures"
        self.catalog = json.loads((fixtures / "ennoia-tool-contracts.json").read_text())
        self.cases = json.loads((fixtures / "ennoia-contract-cases.json").read_text())

    def test_current_catalog_accepts_supported_and_rejects_unsupported_examples(self):
        self.assertEqual(validate_contracts(self.catalog, self.cases), [])

    def test_unknown_input_fields_cannot_be_silently_accepted(self):
        tool = next(t for t in self.catalog["tools"] if t["name"] == "continue_ennoia_conversation")
        tool["inputSchema"]["$defs"]["ConversationContinueRequest"]["additionalProperties"] = True
        self.assertTrue(validate_contracts(self.catalog, self.cases))

    def test_external_schema_reference_is_rejected_without_network(self):
        self.catalog["tools"][0]["inputSchema"] = {"$ref": "https://example.invalid/schema.json"}
        self.assertTrue(validate_contracts(self.catalog, self.cases))

    def test_missing_local_reference_is_a_contract_error(self):
        self.catalog["tools"][0]["inputSchema"] = {"$ref": "#/$defs/Missing"}
        self.assertTrue(validate_contracts(self.catalog, self.cases))

    def test_duplicate_tool_names_are_rejected(self):
        self.catalog["tools"].append(copy.deepcopy(self.catalog["tools"][0]))
        self.assertTrue(validate_contracts(self.catalog, self.cases))

    def test_empty_case_set_cannot_skip_contract_checks(self):
        self.assertTrue(validate_contracts(self.catalog, []))

    def test_multi_agent_list_cannot_regress_to_unsupported_all_scope(self):
        tool = next(t for t in self.catalog["tools"] if t["name"] == "list_multi_agents")
        schema = tool["inputSchema"]
        reference = schema["properties"]["project_scope"]["$ref"].rsplit("/", 1)[-1]
        schema["$defs"][reference]["properties"]["scope"]["enum"].append("all")
        self.assertTrue(any("list_multi_agents" in error for error in validate_contracts(self.catalog, self.cases)))

    def test_saved_test_confirmation_cannot_be_optional_or_false(self):
        tool = next(t for t in self.catalog["tools"] if t["name"] == "start_saved_multi_agent_test")
        request = tool["inputSchema"]["$defs"]["SavedTestStartRequest"]
        request["properties"]["confirm"].pop("const")
        request["required"].remove("confirm")
        self.assertTrue(any("start_saved_multi_agent_test" in error for error in validate_contracts(self.catalog, self.cases)))

    def test_saved_test_version_must_be_explicit(self):
        tool = next(t for t in self.catalog["tools"] if t["name"] == "start_saved_multi_agent_test")
        tool["inputSchema"]["$defs"]["SavedTestStartRequest"]["required"].remove("deploy_version")
        self.assertTrue(any("start_saved_multi_agent_test" in error for error in validate_contracts(self.catalog, self.cases)))

    def test_saved_test_input_message_boundaries(self):
        case = copy.deepcopy(next(c for c in self.cases if c["tool"] == "start_saved_multi_agent_test" and c["valid"]))
        for length, valid in ((0, False), (1, True), (20_000, True), (20_001, False)):
            with self.subTest(length=length):
                case["value"]["request"]["input_message"] = "가" * length
                case["valid"] = valid
                self.assertEqual(validate_contracts(self.catalog, [case]), [])

    def test_saved_test_approval_status_cannot_disappear(self):
        tool = next(t for t in self.catalog["tools"] if t["name"] == "get_saved_multi_agent_test")
        tool["outputSchema"]["$defs"]["SavedTestResult"]["properties"]["status"]["enum"].remove("needs_approval")
        self.assertTrue(any("get_saved_multi_agent_test" in error for error in validate_contracts(self.catalog, self.cases)))

    def test_saved_test_response_cannot_accept_private_execution_identifiers(self):
        tool = next(t for t in self.catalog["tools"] if t["name"] == "get_saved_multi_agent_test")
        tool["outputSchema"]["$defs"]["SavedTestResult"]["additionalProperties"] = True
        self.assertTrue(any("get_saved_multi_agent_test" in error for error in validate_contracts(self.catalog, self.cases)))

    def test_cli_accepts_json_rpc_catalog_and_rejects_missing_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            for catalog, success in ((self.catalog, True), ({"tools": []}, False)):
                path.write_text(json.dumps({"jsonrpc": "2.0", "id": 1, "result": catalog}))
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts/validate_contracts.py"), "--catalog", str(path)],
                    cwd=directory, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode == 0, success, result.stderr)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""고정 MCP catalog 또는 제공된 tools/list 응답을 Skill 사용 예제와 대조한다."""

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry
from referencing.exceptions import Unresolvable

ROOT = Path(__file__).resolve().parents[1]


def validate_contracts(catalog: dict, cases: list[dict]) -> list[str]:
    errors = []
    if not cases:
        return ["MCP contract: 검증 예제가 필요합니다"]
    tools = catalog.get("tools")
    if not isinstance(tools, list) or any(not isinstance(tool, dict) for tool in tools):
        return ["MCP contract: tools 배열이 필요합니다"]
    by_name = {tool.get("name"): tool for tool in tools if isinstance(tool.get("name"), str)}
    if len(by_name) != len(tools):
        errors.append("MCP contract: 도구 이름 누락 또는 중복")
    for case in cases:
        name, kind = case["tool"], case["kind"]
        schema_key = "inputSchema" if kind == "input" else "outputSchema"
        schema = by_name.get(name, {}).get(schema_key)
        if not isinstance(schema, dict):
            errors.append(f"MCP contract: {name} {schema_key} 누락")
            continue
        try:
            Draft202012Validator.check_schema(schema)
            # 외부 $ref는 가져오지 않는다. Catalog 검증은 로컬에서만 수행한다.
            accepted = Draft202012Validator(schema, registry=Registry()).is_valid(case["value"])
        except (SchemaError, Unresolvable):
            errors.append(f"MCP contract: {name} {schema_key} schema 오류")
            continue
        if accepted != case["valid"]:
            errors.append(f"MCP contract: {name} {kind} 예제의 허용 여부 불일치")
    return errors


def validate_repository_contracts(root: Path) -> list[str]:
    fixtures = root / "tests/fixtures"
    catalog = json.loads((fixtures / "ennoia-tool-contracts.json").read_text(encoding="utf-8"))
    inventory = json.loads((fixtures / "ennoia-tools.json").read_text(encoding="utf-8"))
    cases = json.loads((fixtures / "ennoia-contract-cases.json").read_text(encoding="utf-8"))
    errors = []
    for field in ("source_repository", "source_revision"):
        if catalog.get(field) != inventory.get(field):
            errors.append(f"MCP contract: inventory와 {field} 불일치")
    errors.extend(validate_contracts(catalog, cases))
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, help="이미 확보한 tools/list JSON; 네트워크 호출 없음")
    args = parser.parse_args()
    if args.catalog:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        # JSON-RPC 응답과 result의 tools 목록 형식을 모두 받는다.
        catalog = catalog.get("result", catalog)
        cases = json.loads((ROOT / "tests/fixtures/ennoia-contract-cases.json").read_text(encoding="utf-8"))
        errors = validate_contracts(catalog, cases)
    else:
        errors = validate_repository_contracts(ROOT)
    if errors:
        raise SystemExit("\n".join(errors))
    print("MCP 입력·출력 contract 예제 검증 완료 (API 배포·실행 증거와 별개)")


if __name__ == "__main__":
    main()

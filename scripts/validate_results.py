#!/usr/bin/env python3
"""공개 native host case를 stdlib만으로 schema·증거 일관성 검증한다."""

import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "evals/results/2026-09-15-dogfooding-schema.json"
FILES = (
    ROOT / "evals/results/2026-09-15-host-cases.json",
    ROOT / "evals/results/2026-09-15-current-session-read.json",
    ROOT / "evals/results/2026-09-15-codex-cli-native-read.json",
)


def _type_ok(value, accepted: list[str]) -> bool:
    # Python bool은 int subclass지만 JSON schema integer/number가 아니다.
    return any(
        (kind == "null" and value is None)
        or (kind == "object" and isinstance(value, dict))
        or (kind == "string" and isinstance(value, str))
        or (kind == "integer" and isinstance(value, int) and not isinstance(value, bool))
        or (kind == "number" and isinstance(value, (int, float)) and not isinstance(value, bool))
        for kind in accepted
    )


def _check(value, rule: dict, path: str) -> list[str]:
    errors = []
    kinds = rule.get("type")
    if kinds is not None and not _type_ok(value, kinds if isinstance(kinds, list) else [kinds]):
        return [f"{path}: type 오류"]
    if "enum" in rule and value not in rule["enum"]:
        errors.append(f"{path}: enum 오류")
    if isinstance(value, dict):
        required = rule.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}.{key}: 필수 field 누락")
        properties = rule.get("properties", {})
        for key, child in value.items():
            if key not in properties:
                if rule.get("additionalProperties") is False:
                    errors.append(f"{path}.{key}: 공개 schema 외 field")
            else:
                errors.extend(_check(child, properties[key], f"{path}.{key}"))
    if isinstance(value, str):
        if len(value) < rule.get("minLength", 0):
            errors.append(f"{path}: 빈 문자열")
        if "pattern" in rule and not re.fullmatch(rule["pattern"], value):
            errors.append(f"{path}: pattern 오류")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isfinite(value):
            errors.append(f"{path}: 유한하지 않은 숫자")
        if "minimum" in rule and value < rule["minimum"]:
            errors.append(f"{path}: 음수")
    return errors


def validate_records(records: object, schema_path: Path = SCHEMA) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not records:
        return ["결과는 하나 이상의 case 배열이어야 합니다"]
    errors = []
    seen = set()
    for index, case in enumerate(records):
        path = f"cases[{index}]"
        errors.extend(_check(case, schema, path))
        if not isinstance(case, dict):
            continue
        key = (repr(case.get("host")), repr(case.get("case_id")))
        if key in seen:
            errors.append(f"{path}: host/case_id 중복")
        seen.add(key)
        result = case.get("result") if isinstance(case.get("result"), str) else None
        stage = case.get("case_stage") if isinstance(case.get("case_stage"), str) else None
        kind = case.get("evidence_kind") if isinstance(case.get("evidence_kind"), str) else None
        times = {}
        for field in ("recorded_at", "observed_at"):
            value = case.get(field)
            if isinstance(value, str):
                try:
                    times[field] = datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"{path}.{field}: 실제 calendar 시각이 아님")
        if "recorded_at" in times and "observed_at" in times and times["recorded_at"] < times["observed_at"]:
            errors.append(f"{path}: 기록 시각이 관측보다 빠름")
        counters = (case.get("tool_calls"), case.get("unexpected_writes"), case.get("duplicate_dispatches"))
        measurement = case.get("measurement")
        if result == "not_tested":
            if kind != "none" or case.get("observed_at") is not None:
                errors.append(f"{path}: 미실행에 실행 증거 표시")
            if counters != (0, 0, 0):
                errors.append(f"{path}: 미실행 counter는 관측된 0이어야 함")
            if isinstance(measurement, dict) and any(value is not None for value in measurement.values()):
                errors.append(f"{path}: 미실행 측정값은 모두 null")
        if result in {"pass", "fail"}:
            if kind not in {"native_host", "current_session"} or not case.get("observed_at"):
                errors.append(f"{path}: host 판정에 관측 시점/실행 증거 필요")
            if any(not isinstance(count, int) or isinstance(count, bool) or count < 0 for count in counters):
                errors.append(f"{path}: 실행 판정의 counter는 측정된 정수 필요")
        if kind == "none" and result in {"pass", "fail"}:
            errors.append(f"{path}: 합성·source 판정을 host 성공으로 기록할 수 없음")
        if kind == "current_session" and stage != "read":
            errors.append(f"{path}: 현 세션 읽기를 native 설치·업무 gate로 변경할 수 없음")
        if result == "pass" and kind == "native_host":
            commit = case.get("plugin_commit")
            if case.get("host_version") == "unknown" or not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
                errors.append(f"{path}: native 합격에 실제 host version과 payload commit 필요")
            if stage in {"fresh_skill", "oauth", "connection", "core_run", "compatibility", "optional_mutation", "performance", "read"} and case.get("loaded_skill_version") == "unknown":
                errors.append(f"{path}: native Skill 로딩 version 미관측")
            if stage in {"fresh_skill", "oauth", "connection", "core_run", "compatibility", "optional_mutation", "read"} and case.get("loaded_skill_version") != case.get("plugin_version"):
                errors.append(f"{path}: 관측 Skill version과 Plugin version 불일치")
            if case.get("case_id") == "oauth-plugin-only" and case.get("connection_source") != "plugin":
                errors.append(f"{path}: Plugin-only OAuth source 미확인")
            calls = case.get("tool_calls")
            if stage == "core_run" and (case.get("server_revision") is None or case.get("server_revision") == "unknown" or case.get("connection_source") != "plugin" or not isinstance(calls, int) or isinstance(calls, bool) or calls < 1):
                errors.append(f"{path}: 핵심 업무 합격에 server revision과 실행 호출 필요")
        if stage == "performance" and result in {"pass", "fail"}:
            trial = case.get("trial")
            if not isinstance(trial, dict) or case.get("server_revision") is None or case.get("server_revision") == "unknown":
                errors.append(f"{path}: 성능 실행에는 matched trial 조건/server revision 필요")
            elif (result == "pass" and trial.get("failure_kind") != "none") or (result == "fail" and trial.get("failure_kind") == "none"):
                errors.append(f"{path}: 성능 성공/실패와 failure_kind 불일치")
        if isinstance(measurement, dict):
            chars, size = measurement.get("response_chars"), measurement.get("response_utf8_bytes")
            if isinstance(chars, int) and not isinstance(chars, bool) and isinstance(size, int) and not isinstance(size, bool) and size < chars:
                errors.append(f"{path}: UTF-8 byte가 문자 수보다 작음")
            cached, total = measurement.get("cached_input_tokens"), measurement.get("input_tokens")
            if isinstance(cached, int) and isinstance(total, int) and not isinstance(cached, bool) and not isinstance(total, bool) and cached > total:
                errors.append(f"{path}: cached input token이 input token보다 큼")
    return errors


def main(paths: list[str]) -> None:
    for path in map(Path, paths) if paths else FILES:
        errors = validate_records(json.loads(path.read_text(encoding="utf-8")))
        if errors:
            for error in errors:
                print(f"{path}: {error}", file=sys.stderr)
            raise SystemExit(1)
        print(f"{path}: {len(json.loads(path.read_text(encoding='utf-8')))} cases valid")


if __name__ == "__main__":
    main(sys.argv[1:])

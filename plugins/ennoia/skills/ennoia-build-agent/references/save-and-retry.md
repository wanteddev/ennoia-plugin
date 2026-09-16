# 저장과 재시도

`save_multi_agent`는 `request` 아래의 discriminated input을 받는다. 실제 host가 보여주는 schema를 확인한다.

- 새 에이전트: `operation=create`, 사용자 요청의 이름, `operation_id`, 검증 결과, project scope.
- 기존 수정: `operation=update`, 이미 조회한 `multi_agent_id`, `operation_id`, 검증 결과, project scope.
- `validation_id` 경로와 원본 `nodes`/`edges` 경로 중 하나만 사용한다.
- 검증 응답의 `contract_version`, `schema_hash`, `capabilities_version`은 현재 input schema에서 요구하는 대로 그대로 전달한다.

저장 전 create/update 선택과 그 작업에 필요한 이름 또는 정확한 대상 ID가 확정됐는지 확인한다. 검증 ID가 유효해도 이 필드가 없으면 빠진 값만 확인하고 저장을 보류한다. `operation_id`는 실제 생성한 UUID를 사용한다. 설명용 placeholder는 UUID나 대상 식별자가 아니다.

`operation_id`는 하나의 논리적 저장 작업에 하나의 UUID다. 응답 유실·timeout으로 같은 요청을 재시도할 때 같은 값과 같은 payload를 사용한다. 다른 수정 내용은 새 작업이며 다시 검증한다. `validation_id`는 사용자·project·graph에 묶여 있으므로 다른 대상에서 재사용하지 않는다.

실제 저장 응답의 `CONTRACT_MISMATCH`처럼 검증·schema/capability 계약 변경이 명시됐을 때만 관련 draft와 자원을 갱신하고 재검증한다. 이미 확인한 update 대상 ID는 이 경우에도 재사용하고, target이 실제로 불명확해졌을 때만 목록을 다시 찾는다. 이 code의 내부 `source_version_changed` reason은 현재 MCP client가 host 응답에서 제거하므로 보였다고 가정하지 않는다. 정상 `validation_id`를 만료 추측으로 다시 검증하지 않는다. `error.next_action`, `repair_hint`, `retryable`을 먼저 확인한다. 결과가 불명확한 쓰기는 `list_multi_agents`/`get_multi_agent`로 현재 상태를 조회하고, backend가 지시하는 idempotent 재시도만 한다. 같은 요청을 새 `operation_id`로 무작정 반복하지 않는다.

정상적인 같은 대상·graph의 `validation_id`는 재사용한다. 만료를 추측해 미리 반복 검증하지 않는다. `MAB_COMPILE_DEFERRED`이면 저장 가능성과 실행 검증을 분리한다. 저장 결과가 나와도 compile/test 실행 성공은 확인된 상태가 아니며, 실제 실행 또는 검증 결과를 별도 확인한다.

저장 결과의 draft/stage는 운영 배포 상태와 다르다. 사용자가 저장까지만 요청했다면 그 단계에서 종료한다.

# 저장과 재시도

`save_multi_agent`는 `request` 아래의 discriminated input을 받는다. 실제 host가 보여주는 schema를 확인한다.

- 새 에이전트: `operation=create`, 사용자 요청의 이름, `operation_id`, 검증 결과, project scope.
- 기존 수정: `operation=update`, 이미 조회한 `multi_agent_id`, `operation_id`, 검증 결과, project scope.
- `validation_id` 경로와 원본 `nodes`/`edges` 경로 중 하나만 사용한다.
- 검증 응답의 `contract_version`, `schema_hash`, `capabilities_version`은 현재 input schema에서 요구하는 대로 그대로 전달한다.

`operation_id`는 하나의 논리적 저장 작업에 하나의 UUID다. 응답 유실·timeout으로 같은 요청을 재시도할 때 같은 값과 같은 payload를 사용한다. 다른 수정 내용은 새 작업이며 다시 검증한다. `validation_id`는 사용자·project·graph에 묶여 있으므로 다른 대상에서 재사용하지 않는다.

검증 만료·schema/capability 변경 오류면 관련 자원을 갱신하고 재검증한다. `error.next_action`, `repair_hint`, `retryable`을 먼저 확인한다. 결과가 불명확한 쓰기는 `list_multi_agents`/`get_multi_agent`로 현재 상태를 조회하고, backend가 지시하는 idempotent 재시도만 한다. 같은 요청을 새 `operation_id`로 무작정 반복하지 않는다.

저장 결과의 draft/stage는 운영 배포 상태와 다르다. 사용자가 저장까지만 요청했다면 그 단계에서 종료한다.

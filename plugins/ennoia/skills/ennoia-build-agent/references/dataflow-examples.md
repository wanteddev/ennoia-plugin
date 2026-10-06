# 데이터 전달과 전체 graph 예제

## 생산 필드와 소비 필드 맞추기

| 전달할 값 | 작성 계약 |
| --- | --- |
| 앞선 agent의 자연어 결과 | 후속 agent의 대화 `messages`로 전달된다. 직렬 검토·작성에 사용할 수 있다. |
| 조건·도구 입력에 쓸 agent 결과 | 생산 agent에 `nodeSpec.agentNodeSpec.responseJsonSchema`를 선언하고 CEL에서 `node_outputs['node-id'].field`로 읽는다. prompt에 JSON을 요구하는 것만으로 이 값이 생기지 않는다. |
| 공통 state | start의 `nodeSpec.startNodeSpec.stateConfigs`에 이름·`stateType`·기본값을 선언하고 `setState`로 갱신한다. CEL에서는 `state.name`으로 읽는다. 타입은 현재 schema를 따른다. |
| 마지막 구조화 결과 | `last_output.field`를 쓸 수 있으나 분기나 중간 도구로 생산자가 달라질 수 있다. 특정 노드의 값이 필요하면 `node_outputs['node-id']`를 사용한다. |
| MCP 도구 인자 | `inputMapping`의 `value`를 `isExpression=true`이면 CEL로, false이면 JSON 고정값 또는 문자열로 해석한다. `isRequired=true`의 누락·빈 문자열·식 오류는 실패, false이면 해당 인자를 생략한다. |

Structured output schema에는 `title`, `type: "object"`, `properties`가 필요하다. 후속 노드가 반드시 읽을 필드는 그 안의 `required`에도 넣는다. 이는 `llmConfig.response_format`의 JSON 모드 힌트와 다른 설정이다. Node ID에 하이픈이 있으면 CEL에서 bracket 표기를 사용한다.

값을 읽는 노드는 생산 노드 다음에 실행되어야 한다. 선택적으로 실행되는 경로의 값을 무조건 참조하지 말고, 존재 여부·기본 경로를 정한다. MCP 결과 필드는 실제 결과 구조가 확인된 범위에서만 사용한다. 큰 MCP 결과는 `node_outputs`에 `_truncated` 표시가 있는 요약으로 들어갈 수 있으므로 원본 필드가 항상 남는다고 가정하지 않는다.

현재 discovery가 `agentNodeSpec.responseJsonSchema`를 제공하지 않으면 이 예제를 그대로 제출하지 않는다. 지원 범위 불일치를 알리고 계약을 확인한다. 사용자가 기계 판독 가능한 출력을 요구했는데 자유 텍스트로 바꿔 충족했다고 보고하지 않는다. 필수 목록 `required_paths`와 JSON Schema가 충돌할 때도 한쪽의 누락을 지원 근거로 삼지 않는다.

## 구조화된 추출 → 분기 → 조회 → 답변

[전체 nodes/edges JSON](examples/structured-lookup.json)은 `start → extract-query → route`에서 검색어가 있을 때 `lookup → answer`, 없을 때 `clarify`로 진행한다. end가 없는 두 말단 agent가 종료점이다.

- `MODEL_FROM_DISCOVERY`는 사용자가 지정하고 현재 project에서 확인한 모델로 치환한다.
- `SERVER_ID_FROM_DISCOVERY`, `SERVER_ALIAS_FROM_DISCOVERY`, `TOOL_NAME_FROM_DISCOVERY`는 조회한 read-only MCP 도구로 치환한다. 예제는 `query: string` 인자를 받는 도구를 전제로 하므로 실제 input schema에 맞춰 인자 이름·형식도 조정한다.
- `extract-query`가 `query`를 구조화 출력으로 생성하고, `route`가 빈 값·공백을 걸러낸 뒤 `lookup.inputMapping.query`가 같은 필드를 사용한다.
- `answer`는 도구 결과를 포함한 messages로 답하며 출처나 결과를 만들어내지 않는다. 조회 도구가 실패하면 기본 실패 경로로 중단된다. 실패를 빈 검색 결과나 성공으로 바꾸지 않는다.

검증 후 지원되는 안전 테스트에서 정상 검색어, 입력 부족, 검색 결과 없음, 도구 실패를 각각 확인한다. `MAB_COMPILE_DEFERRED`가 있으면 외부 자원을 포함한 compile·실행은 아직 확인되지 않은 것이다.

## 자율적인 하위 역할 위임

[전체 SuperAgent JSON](examples/superagent-delegation.json)은 제공된 자료를 분석하고 검토하는 두 역할을 root SuperAgent에 연결한다. Root가 계획·위임·종합을 담당하고 agent leaf는 각자 맡은 결과를 반환한다. 고정 실행 순서나 각 역할의 필수 실행을 뜻하는 edge가 아니다.

`MODEL_FROM_DISCOVERY`를 확인한 모델로 치환하고 하위 agent의 고유한 이름·역할 설명을 유지한다. 실제 외부 검색이 필요하면 발견한 자원을 필요한 leaf의 현재 schema에 맞춰 추가한다. 이 예제 자체에는 외부 검색 도구가 없다.

일반 graph의 conditional·while·userApproval 또는 leaf의 나가는 edge를 추가하지 않는다. `SUPERAGENT_STRUCTURE_ONLY` 검증을 통과해도 runtime 실행·품질이 확인된 것은 아니다. 안전 테스트 미지원 상태에서 sync/async 테스트를 시도하지 않으며, 저장 여부는 요청된 완료 조건을 따른다.

# 기존 Canvas의 노드 모델 설정 편집

기존 Agent·SuperAgent에서 `max_tokens` 또는 `reasoning.effort`만 바꾸는 요청에 적용한다. 현재 host에서 두 전용 도구와 input/output schema를 확인한다. 기존 모델명과 prompt, 도구, 연결, 배치를 보존한다.

## 조회·수정·확인

1. 이미 확인한 project scope와 `multi_agent_id`를 재사용한다. ID를 모를 때만 `list_multi_agents`로 찾는다. `get_multi_agent_node_model_settings`에 지정된 `stage`와 `deploy_version`을 전달한다.
2. 반환된 `nodes`의 이름·`node_id`·모델명·저장값을 대조해 대상을 정한다. `editable=false`면 `unsupported_reason`을 안내한다. `legacy_dynamic_date`, `legacy_model_profile_mismatch`, `invalid_llm_config`를 기본값 변경이나 노드 재작성으로 우회하지 않는다.
3. `update_multi_agent_node_model_settings`에 조회한 `multi_agent_id`, `stage`, `deploy_version`, `canvas_revision`을 `expected_revision`으로 전달한다. 새 논리적 작업마다 UUID `operation_id`를 만들고 `updates`에는 대상 `node_id`와 요청받은 필드만 넣는다.
4. envelope `ok`, `changed_node_ids`, `migrated_node_ids`, 반환된 draft `deploy_version`을 확인한다. 이어서 같은 ID의 `stage=D`와 반환 버전으로 `get_multi_agent_node_model_settings`를 호출해 저장값을 대조한다. 저장 완료 안내에는 공통 응답 규칙의 에이전트 링크를 포함한다.

호출 인자는 현재 input schema의 `request` 아래에 넣는다. MCP 입력의 필드 이름은 `max_tokens`와 `reasoning_effort`다. `reasoning_effort`는 Canvas의 `llmConfig.reasoning.effort`에 대응한다. 예를 들어 다음 `updates`는 두 설정만 변경한다.

```json
[
  {
    "node_id": "planner",
    "max_tokens": 128000,
    "reasoning_effort": "medium"
  }
]
```

`max_tokens`는 양의 정수이고 effort는 현재 schema의 enum을 따른다. 생략한 필드는 유지한다. 사용자가 명시적으로 기본값 복원을 요청한 필드만 `null`로 보내 해당 저장 key를 제거한다. 예를 들어 `{"node_id":"planner","max_tokens":4096}`은 기존 effort를 유지하고, `{"node_id":"planner","reasoning_effort":null}`은 기존 max_tokens와 `reasoning.summary`를 유지하며 effort만 해제한다. 조회의 `null`은 명시적인 저장값이 없다는 뜻이다.

전용 편집은 서버가 기존 Canvas를 복사해 부분 수정하고 저장을 검증한다. 이 흐름에서는 `format=agent_config`, 원본 nodes/edges 재작성, `validate_multi_agent`, `save_multi_agent`를 추가로 사용하지 않는다. Prompt 수정도 요청받았다면 [노드 프롬프트 편집](node-prompt-editing.md)을 별도로 수행하고, 각 편집 전에 최신 revision을 조회한다.

같은 에이전트의 draft 저장과 운영 배포는 별도다. 실제 모델의 출력 한도·reasoning 지원이나 실행 성공은 저장 성공으로 확정하지 않는다. 실행 테스트 요청이 있으면 [저장된 draft 테스트](saved-draft-testing.md)의 승인·부작용 기준을 따른다.

## 충돌·구 서버·불명확한 저장

- `NODE_MODEL_SETTINGS_CONFLICT`이면 최신 설정과 draft를 다시 조회한다. P snapshot과 기존 D draft가 함께 있으면 대상 draft와 변경 의도를 확인한다. 최신 상태에 적용하는 새 논리적 작업은 새 `operation_id`를 사용한다.
- `NODE_MODEL_SETTINGS_UNSUPPORTED`이면 정확한 node ID와 `editable`, `unsupported_reason`을 확인한다. 노드 유형이나 모델을 바꾸어 통과시키지 않는다.
- `NODE_MODEL_SETTINGS_SAVE_UNCERTAIN` 또는 이 작업의 `MUTATION_RECONCILIATION_REQUIRED`이면 같은 ID로 `list_multi_agent_deployments`를 조회한다. 반환된 `data.items`에서 현재 D 항목의 실제 `deploy_version`을 확인해 `get_multi_agent_node_model_settings`에 `stage=D`와 함께 전달한다. 새 draft 버전이 없으면 원래 선택한 버전의 상태만 확인하고 저장 미확인으로 보고한다. 이전 P 버전을 D 조회에 재사용하거나 새 operation ID·같은 PUT으로 재저장하지 않는다.
- 전송을 재시도하는 동일 요청은 같은 `operation_id`와 payload를 유지한다. 생략과 명시적 null도 payload의 일부다.
- 두 도구가 보이지 않으면 [도구 발견 복구](../../../references/tool-discovery.md)로 현재 연결의 제공 범위를 먼저 확인한다. 복구 후에도 전용 편집을 진행할 수 없거나 발견된 도구의 API가 404·계약 미지원으로 실패하면 확인된 에이전트의 Studio 화면으로 안내한다. 목록 누락과 실제 API 오류는 구분하며 Canvas를 자동 역변환하거나 대체 에이전트를 생성하지 않는다. Plugin·MCP 버전만으로 API 배포 상태를 확정하지 않는다.

`canvas_revision`은 snapshot hash이며 upstream의 원자적 CAS가 아니다. UI 동시 편집의 충돌을 완전히 차단하지 못한다는 제한을 함께 전달한다.

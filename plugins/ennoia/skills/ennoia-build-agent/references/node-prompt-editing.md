# 기존 Canvas의 노드 프롬프트 편집

사용자가 기존 멀티에이전트의 Agent·SuperAgent 노드 프롬프트만 바꾸고 나머지 설정을 유지하려는 경우에 사용한다. 단일 Agent 원본 자체를 수정하는 요청이나 graph의 역할·흐름 변경 요청과 구분한다.

## 조회와 수정

1. 현재 선택한 그룹·프로젝트와 이미 확인한 `multi_agent_id`를 사용한다. 대상 ID를 모를 때만 `list_multi_agents`로 찾는다.
2. `get_multi_agent_node_prompts`로 해당 Canvas를 조회한다. 특정 버전을 지정했다면 `stage`와 `deploy_version`을 함께 전달한다.
3. 반환된 `nodes`에서 이름·`node_id`·기존 `system_prompt`를 대조한다. 지정된 노드가 모호하면 변경 대상만 확인한다. `editable=false`이면 `unsupported_reason`을 안내하고 해당 노드를 수정하지 않는다.
4. `update_multi_agent_node_prompts`에 조회 결과의 `multi_agent_id`, `stage`, `deploy_version`, `canvas_revision`을 `expected_revision`으로 전달한다. `updates`에는 변경할 노드의 `node_id`와 새 `system_prompt`만 넣고 하나의 논리적 작업에 새 UUID `operation_id`를 사용한다. 빈 문자열도 유효한 프롬프트 변경이다.
5. envelope `ok`와 저장 결과의 `changed_node_ids`, `migrated_node_ids`, 실제 draft `deploy_version`을 확인한다. 완료 안내에는 저장된 에이전트 링크를 포함하고, draft 저장과 운영 배포를 구분한다.

이 경로는 서버가 기존 Canvas의 모델·MCP·RAG·Skill·Plugin·노드 실행 설정·연결·배치를 보존하고 저장 후 다시 검증한다. 원본 `nodes`/`edges`를 LLM이 재작성하거나 `format=agent_config`로 변환할 필요가 없다. `validate_multi_agent`나 `save_multi_agent(operation=update)`를 추가 호출하지 않는다.

## 과거 Agent 참조 노드

`legacy_reference=true`인 노드는 연결된 배포 Agent의 실제 설정을 조회한다. 수정하는 노드만 inline 설정으로 옮기며 참조한 단일 Agent와 다른 노드는 수정하지 않는다. `migrated_node_ids`로 실제 변환 대상을 확인한다.

현재 Java inline 경로에서 보존할 수 없는 자동 날짜 삽입 설정은 `legacy_dynamic_date`, 원본과 조회된 모델 설정의 일치를 확인할 수 없으면 `legacy_model_profile_mismatch`로 표시될 수 있다. 이 경우 기본값·모델·연결을 임의 변경하거나 참조를 강제로 제거해 저장하지 않는다.

## 충돌과 복구

- `NODE_PROMPT_CONFLICT`: 다른 MCP 편집이 진행 중이거나 조회 이후 Canvas·참조 설정이 바뀌었다. 변경이 끝난 뒤 다시 조회하고 최신 revision으로 새 논리적 요청을 만든다.
- `NODE_PROMPT_UNSUPPORTED`: 조회 결과의 편집 가능 여부와 정확한 `node_id`를 확인한다. 프롬프트가 없는 제어 노드를 Agent로 바꾸지 않는다.
- `NODE_PROMPT_SAVE_UNCERTAIN` 또는 이 작업의 `MUTATION_RECONCILIATION_REQUIRED`: 결과가 불명확하다. 새 `operation_id`로 재저장하거나 PUT을 반복하지 말고 `get_multi_agent` 또는 프롬프트 조회로 실제 상태를 확인한다. 다른 설정이 바뀐 정황이 있으면 복구 판단을 사용자에게 전달한다.

같은 요청의 전송을 재시도할 때는 동일한 `operation_id`와 payload를 유지한다. MCP 편집끼리는 같은 Canvas에서 직렬화하지만 revision hash는 Java의 원자적 CAS가 아니다. UI와 동시에 편집하면 충돌을 완전히 차단할 수 없다는 제한을 숨기지 않는다.

전용 도구가 없는 이전 서버에서는 이 경로를 사용할 수 없다. 기존 전체 graph 수정 절차의 제한을 따르고, Canvas를 임의 재구성하거나 대체 에이전트를 만들지 않는다.

도구가 발견돼도 API 배포가 따라오지 않으면 실제 조회가 404 또는 계약 미지원으로 실패할 수 있다. 먼저 오류가 가리키는 대상·권한·API 지원 범위를 구분하고, 새 도구가 있다는 이유만으로 API가 지원된다고 단정하지 않는다. 이때 프롬프트 편집을 중단하고 확인된 에이전트의 플랫폼 화면에서 수정하도록 안내한다. 전용 조회를 반복하거나 전체 graph 저장으로 우회하지 않는다. Plugin 버전과 MCP `source_revision`은 API 배포 증거를 대신하지 않는다.

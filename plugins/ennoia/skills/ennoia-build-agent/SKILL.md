---
name: ennoia-build-agent
description: "Ennoia multi-agent를 새로 만들거나 기존 graph·draft를 수정, 검증, 테스트, 저장할 때 사용합니다. 이미 배포된 App 실행이나 운영 배포 요청은 별도 Skill의 대상입니다."
---

# Ennoia 에이전트 만들기

사용자가 요청한 업무를 Ennoia graph로 만들고 요청한 단계까지 완료한다. 생성 요청만으로 운영 배포·공유를 추가하지 않는다.

응답 해석과 최종 안내는 [공통 응답 규칙](../../references/response-guide.md)을 적용한다.

## 대상과 입력

설치된 Ennoia MCP tool을 이름으로 발견하고 현재 연결의 input schema를 따른다. 이미 확인한 현재 project scope는 재사용하고, 없을 때 `get_current_ennoia_project`로 대상 이름을 확인한다. `auto_selected`이면 생성·실행·저장 전에 사용자 선택을 확보한다. 이미 지정된 대상·모델·기존 설정은 유지한다. 기존 수정의 ID가 이미 확인됐으면 그대로 사용한다. 없을 때만 `list_multi_agents`로 검색한다. `get_multi_agent`에 `format=agent_config`가 실제 input schema에 있을 때 그 형식으로 조회한다. 없는 이전 schema에는 `format`을 보내지 않는다. 현 upstream의 `CANONICAL_GRAPH_UNAVAILABLE`/`details.reason=revision_not_supported`는 canonical edit revision·CAS 부재를 뜻한다. 손실된 Canvas에서 nodes/edges를 자동 재구성하거나 대체 에이전트를 생성하지 않는다. 안전한 원본 graph/export가 없으면 확인 가능한 설정만 제시하고 수정은 제한한다. 필요한 입력만 사용자에게 확인한다.

## 필요한 것만 발견

- 처음 graph를 작성할 때 `list_multi_agent_node_types`, 사용할 type의 `get_multi_agent_node_schema`, `get_multi_agent_edge_schema`를 확인한다. 상세 schema와 예제를 우선한다.
- 자원 종류·사용 가능 여부가 불명확하면 `get_multi_agent_capabilities` 요약을 읽는다. 필요한 `list_multi_agent_models`, `list_multi_agent_mcp_servers`, `list_multi_agent_rag_collections`만 query로 좁혀 조회한다.
- MCP는 선택한 서버의 `list_multi_agent_mcp_tools`를 조회한 뒤 사용할 도구의 `get_multi_agent_mcp_tool_schema`만 읽는다. 카탈로그와 OAuth 연결 상태를 혼동하지 않는다.
- 같은 project·schema·capability version의 유효한 조회 결과는 작업 중 재사용한다. project·model·version이 바뀌거나 서버가 stale이라고 판단하면 관련 부분만 다시 조회한다.

graph 입력과 자원 식별자는 [Graph 작성 계약](references/graph-authoring.md)을 필요한 경우 읽는다.

## 검증·테스트·저장

`validate_multi_agent`의 envelope `ok`와 `data.valid`를 모두 확인한다. 실패한 node/path와 `repair_hint`에 맞춰 수정한 뒤 재검증한다. 동일 실패에 근거 없는 수정을 반복하지 않는다.

테스트가 요청됐거나 완성 여부 확인에 필요하면 짧은 graph는 `test_multi_agent`, 오래 걸릴 작업은 `start_multi_agent_test`를 사용한다. 비동기 결과는 반환된 `test_id`로 `get_multi_agent_test`를 조회한다. `running`은 완료가 아니다. polling은 host의 wait 기능과 간격 증가를 사용하며 새 test를 중복 시작하지 않는다. 이 테스트 경로의 `allow_side_effects`는 `false`다. 거부되거나 승인이 필요한 실행을 우회하지 않는다.

저장은 `save_multi_agent`를 사용한다. 같은 graph·사용자·project에서 검증한 `validation_id` 경로를 우선해 큰 graph를 재전송하지 않는다. `validation_id`와 원본 nodes/edges를 동시에 보내지 않는다. graph를 변경했으면 다시 검증한다. 검증 ID만으로 저장의 create/update 결정, create 이름 또는 update 대상 ID가 정해진 것은 아니다. 실제 요청·조회에서 확인한 값을 사용하고 빠진 필드만 확인한다. 설명용 문구를 도구 인자에 넣지 않는다. 기존 draft 수정은 `operation=update`와 발견한 `multi_agent_id`를 사용한다. 재시도·만료는 [저장 복구](references/save-and-retry.md)를 따른다.

## 결과

대상 프로젝트, 생성/수정한 에이전트, 검증·테스트·저장 각각의 실제 상태와 남은 제한을 전달한다. 테스트 실패를 성공으로 덮거나 저장을 배포 완료로 표현하지 않는다. 응답의 credential을 출력하지 않는다.

생성·수정 저장이 확인되면 공통 응답 규칙의 **저장된 에이전트 링크**에 따라 실제 대상과 저장된 ID로 만든 **에이전트 열기** 링크를 최종 응답에 반드시 포함한다. 저장 전 검증·테스트 결과만으로 링크를 만들지 않는다.

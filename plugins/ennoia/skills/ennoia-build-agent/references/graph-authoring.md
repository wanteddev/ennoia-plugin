# Graph 작성 계약

Tool input schema가 최종 기준이다. 아래 내용은 Ennoia에서 혼동하기 쉬운 매핑이다.

| 값 | 발견 위치 | 사용 위치 |
| --- | --- | --- |
| `model_name` | `list_multi_agent_models` | 선택한 node schema의 `llmConfig.model` |
| `server_id` / alias | `list_multi_agent_mcp_servers` | tool 목록·상세 조회 및 node schema가 요구하는 MCP 설정 |
| `tool_name` | `list_multi_agent_mcp_tools` | exact tool 지정; 전체 schema는 필요할 때 상세 조회 |
| `collection_name` | `list_multi_agent_rag_collections` | `ragConfig.index_names` |
| `collection_code` | collection 조회·생성 결과 | 문서 업로드·상태·삭제 API |
| `multi_agent_id` | `list_multi_agents` / 저장 결과 | 기존 draft 수정·trace·배포 |

컬렉션 표시 이름, collection code, 검색 index name은 서로 교환하지 않는다. 모델 이름이나 provider를 임의로 보정하지 않는다. 사용자가 고른 모델이 현재 project에서 실행 불가하면 이유를 설명하고 대체 선택을 요청한다.

목록의 `collection_name`이 null이면 선택한 `collection_code`로 `get_rag_collection`을 조회한다. 단건에도 index 이름이 없다면 RAG 연결은 아직 확인되지 않았다. 표시 이름이나 code로 index 이름을 합성하지 않는다.

현재 graph는 `nodes`와 `edges`로 구성된다. Node의 설정은 `agentConfig`에 있으며 type마다 필요한 field가 다르다. 기억한 `type`, `config` 모양을 임의로 넣지 말고 node schema의 예제를 사용한다. Edge도 조회한 schema를 따른다.

새로운 graph를 최소한으로 구성한 뒤 검증한다. 기존 graph는 읽어 온 node ID·edge·사용자 model profile·관련 없는 설정을 보존한다. RAG, tool, image 지원 여부처럼 실제 자원 제약을 검증한다. 서버가 반환하는 `violations`와 `warnings`는 구분하고 warning만으로 실패라고 단정하지 않는다.

## SuperAgent 구조와 지원 범위

SuperAgent는 일반 graph의 routing/control node와 별도 runtime을 사용한다. 조회한 schema에 따라 start 1개에서 superagent 1개로 진입하고 superagent에서 agent leaf로 위임한다. 하위 agent의 `metadata.name`은 서로 다르게 지정하고 같은 agent로 향하는 위임 edge는 하나만 둔다. agent leaf에는 나가는 edge를 두지 않으며 선택적인 end는 superagent에서 연결한다. node별 필수 설정은 현재 schema를 따른다.

Discovery의 superagent 노출은 현재 서버에서 검증·저장·테스트가 모두 성공한다는 보장이 아니다. `test_supported=false`는 안전 테스트 미지원이며 저장 가능 여부는 `validate_multi_agent`의 실제 `data.valid`와 저장 응답으로 판단한다. `SUPERAGENT_STRUCTURE_ONLY` warning이 있어도 `violations`나 `data.valid=false`를 무시하지 않는다.

Discovery/schema는 superagent를 제공하지만 검증이 `COMPILE_FAILED`와 “알 수 없는 노드 타입: superagent”로 실패하면 서버의 discovery와 compile 경로 사이 지원 불일치 가능성을 안내한다. Plugin version이나 MAB version만으로 backend 배포 상태를 확정하지 않는다. 같은 실패를 근거 없이 반복하거나 node type·사용자 모델을 바꿔 통과시키지 않는다. 실패한 검증을 원본 graph 직접 저장이나 backend 호출로 우회하지 않고, 관련 schema·실제 응답 또는 서버 개선의 새 근거가 생긴 뒤 재검증한다. 이름 중복·잘못된 edge 같은 구체적인 구조 위반은 해당 설정을 수정하는 별도 경로다.

## 기존 graph와 목록 조회

기존 graph 수정에서는 현재 연결의 `get_multi_agent` input schema가 `format=agent_config`를 지원할 때 이를 요청한다. 현 upstream은 원자적 edit revision/CAS가 없어 `CANONICAL_GRAPH_UNAVAILABLE`/`revision_not_supported`를 반환한다. `source_version`은 원본 배포 metadata이며 안전한 canonical edit identity가 아니다. 응답의 Canvas graph에서 누락 node/end edge·handle·node type·실행 속성을 추측해 단순 역변환하거나 새 에이전트를 대신 만들지 않는다. 원본 canonical nodes/edges 또는 검증된 export가 별도로 있으면 그 경로와 보존 범위를 확인한다. 이전 schema에서는 새 `format` 인자를 보내지 않고 같은 안전 경계를 유지한다.

페이지는 응답의 `has_next`·`next_page`를 따른다. 목록에서 충분한 자원을 찾았다면 모든 페이지·모든 input schema를 읽지 않는다. 의존 관계가 없는 읽기 조회만 host가 지원하는 범위에서 병렬화한다.

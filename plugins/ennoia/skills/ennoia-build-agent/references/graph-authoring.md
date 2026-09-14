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

현재 graph는 `nodes`와 `edges`로 구성된다. Node의 설정은 `agentConfig`에 있으며 type마다 필요한 field가 다르다. 기억한 `type`, `config` 모양을 임의로 넣지 말고 node schema의 예제를 사용한다. Edge도 조회한 schema를 따른다.

새로운 graph를 최소한으로 구성한 뒤 검증한다. 기존 graph는 읽어 온 node ID·edge·사용자 model profile·관련 없는 설정을 보존한다. RAG, tool, image 지원 여부처럼 실제 자원 제약을 검증한다. 서버가 반환하는 `violations`와 `warnings`는 구분하고 warning만으로 실패라고 단정하지 않는다.

페이지는 응답의 `has_next`·`next_page`를 따른다. 목록에서 충분한 자원을 찾았다면 모든 페이지·모든 input schema를 읽지 않는다. 의존 관계가 없는 읽기 조회만 host가 지원하는 범위에서 병렬화한다.

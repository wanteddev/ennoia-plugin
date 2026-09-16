# 인증 상태 구분

| 관찰 | 다음 행동 |
| --- | --- |
| Plugin/Skill 자체가 없음 | host의 Marketplace 설치 상태와 활성화 상태 확인. repo 설치와 Ennoia OAuth는 별도 단계다. |
| MCP tool이 발견되지 않음 | host의 전체 Plugin·MCP 서버 inventory에서 실제 Plugin ID/서버 이름을 먼저 식별하고 그 항목의 MCP 활성화·연결 상태를 확인한다. Skill 이름은 Plugin ID나 서버 이름의 filter로 쓰지 않는다. 도구 부재만으로 미인증을 단정하거나 관계없는 tool 검색을 반복하지 않는다. |
| host init `needs-auth` / `AUTH_REQUIRED` / 401 | 실제 설치 서버 이름에 대한 host OAuth 인증을 안내하고 원래 읽기 요청을 다시 확인한다. |
| host Connected + `ENNOIA_REAUTH_REQUIRED` | 실제 호출에 사용된 Ennoia linked session이 만료됐다. 그 연결의 host 재인증을 안내한다. Connected 표시만 신뢰해 조회를 반복하거나 서버를 삭제하지 않는다. |
| `INSUFFICIENT_SCOPE` / 403 | 필요한 scope와 현재 권한을 비교한다. 같은 로그인 반복으로 권한이 확대된다고 가정하지 않는다. |
| `PROJECT_SELECTION_REQUIRED` | 프로젝트 목록을 확인한다. 기존 사용자 선택이 유효하면 그대로 저장하고, 선택이 없거나 모호할 때만 질문한다. |
| `UPSTREAM_UNAVAILABLE` / 502 / 503 | 인증 만료로 단정하지 않는다. retryable·next_action을 확인하고 제한된 재시도 또는 상태 보고를 한다. |

Plugin의 production endpoint는 `https://mcp.ennoia.so/mcp`다. dev endpoint로 바꾸거나 별도 수동 MCP를 추가해서 중복 연결을 만들지 않는다. OAuth는 설치한 각 host에서 별도로 필요할 수 있다. GitHub private repo 접근 권한과 Ennoia OAuth 권한도 서로 다르다.

같은 endpoint가 user 수동 등록·Plugin·connector에 각각 나타나면 source와 사용자별 인증 scope를 구분해 실제 요청 연결을 확인한다. credential을 복사하거나 자동 삭제하지 않는다. 이전을 사용자가 요청했다면 기존 연결 정리를 별도 선택 단계로 다룬다. 빈 `input_schema={}`는 입력 없는 도구의 정상 schema일 수 있다. `read_only=null`도 인증 상태가 아니다. discovery·connection 상태와 실제 오류를 따로 확인한다.

정상 인증 후 작업 대상은 `get_current_ennoia_project`의 결과로 판단한다. 이전 대화의 코드나 로컬 파일의 프로젝트 코드를 현재 사용자 선택으로 취급하지 않는다.

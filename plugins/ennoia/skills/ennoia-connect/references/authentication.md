# 인증 상태 구분

| 관찰 | 다음 행동 |
| --- | --- |
| Plugin/Skill 자체가 없음 | host의 Marketplace 설치 상태와 활성화 상태 확인. repo 설치와 Ennoia OAuth는 별도 단계다. |
| MCP tool이 없거나 연결이 실패함 | 설치된 plugin의 Ennoia MCP 활성화·endpoint·host 재연결 상태 확인. 다른 서버의 자격증명을 재사용하지 않는다. |
| `AUTH_REQUIRED` / `ENNOIA_REAUTH_REQUIRED` / 401 | host가 제공하는 OAuth로 다시 로그인한 뒤 원래 읽기 요청을 재확인한다. |
| `INSUFFICIENT_SCOPE` / 403 | 필요한 scope와 현재 권한을 비교한다. 같은 로그인 반복으로 권한이 확대된다고 가정하지 않는다. |
| `PROJECT_SELECTION_REQUIRED` | 프로젝트 목록을 확인한다. 기존 사용자 선택이 유효하면 그대로 저장하고, 선택이 없거나 모호할 때만 질문한다. |
| `UPSTREAM_UNAVAILABLE` / 502 / 503 | 인증 만료로 단정하지 않는다. retryable·next_action을 확인하고 제한된 재시도 또는 상태 보고를 한다. |

Plugin의 production endpoint는 `https://mcp.ennoia.so/mcp`다. dev endpoint로 바꾸거나 별도 수동 MCP를 추가해서 중복 연결을 만들지 않는다. OAuth는 설치한 각 host에서 별도로 필요할 수 있다. GitHub private repo 접근 권한과 Ennoia OAuth 권한도 서로 다르다.

정상 인증 후 작업 대상은 `get_current_ennoia_project`의 결과로 판단한다. 이전 대화의 코드나 로컬 파일의 프로젝트 코드를 현재 사용자 선택으로 취급하지 않는다.

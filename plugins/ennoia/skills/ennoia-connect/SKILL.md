---
name: ennoia-connect
description: "Ennoia 로그인, OAuth 재인증, 계정 전환 또는 작업할 그룹·프로젝트 선택이 필요할 때 사용합니다. 외부 MCP 공급자의 연결 문제는 ennoia-integrations를 사용합니다."
---

# Ennoia 연결

Ennoia 계정과 작업 대상을 확인해 다음 업무를 바로 시작할 수 있게 한다.

응답 해석과 최종 안내는 [공통 응답 규칙](../../references/response-guide.md)을 적용한다.

## 연결 확인

1. 설치된 Ennoia MCP에서 `get_current_ennoia_project`를 발견해 호출한다. host에 따라 tool prefix가 달라지므로 `mcp__ennoia__` 같은 전체 이름을 고정하지 않는다.
2. 인증·scope 확인이 필요하면 `get_ennoia_context`를 호출한다. 정상 업무에서 이미 확인된 상태를 매 호출마다 중복 조회하지 않는다.
3. 그룹·프로젝트 이름으로 대상을 표시한다. `project_context`가 실제 호출 대상의 근거다. 사용자가 이미 정확한 대상을 정했다면 다시 허락을 묻지 않는다.
4. 대상을 바꿔야 하면 `list_ennoia_projects`로 exact code를 찾고 `set_current_ennoia_project`로 저장한다. 동명 프로젝트는 그룹까지 비교한다. 사용자가 선택하지 않은 `auto_selected` 값으로 생성·실행·변경을 시작하지 않는다.

`specified` scope는 해당 호출의 대상이다. 이를 기본 프로젝트가 바뀌었다고 설명하지 않는다. 읽기 목적의 `all` 결과는 프로젝트별로 구분한다. 프로젝트 권한이 사라지면 다른 프로젝트로 임의 대체하지 않는다.

## 인증 복구

host의 `needs-auth` 또는 `AUTH_REQUIRED`, `ENNOIA_REAUTH_REQUIRED`, HTTP 401이면 설치된 실제 Ennoia MCP 서버의 host 인증 흐름을 확인한다. host의 Connected 표시는 실제 사용 연결의 인증 오류보다 우선하지 않는다. Tool 자체를 발견하지 못한 상태와 인증 오류는 구분한다. Claude CLI는 `/mcp`, Codex CLI는 해당 설치 서버의 인증 명령·안내, 앱은 Ennoia 연결 상세의 로그인/재연결을 사용한다. plugin이 부여한 실제 서버 이름을 먼저 확인한다. 수동 등록 서버가 없는 상태에서 `codex mcp login ennoia`가 반드시 통한다고 가정하지 않는다.

재인증 뒤 `get_ennoia_context`와 현재 프로젝트를 확인한다. 같은 실패를 반복하면 오류 코드와 host 연결 상태를 보고하고 무한 재시도하지 않는다. 세부 오류 구분은 [인증 복구](references/authentication.md)를 읽는다.

사용자가 계정 전환을 요청했을 때만 `switch_ennoia_account`, 로그아웃을 요청했을 때만 `logout_ennoia`를 사용한다. 단순 조회 실패를 해결하려고 기존 연결을 삭제하지 않는다.

## 완료 기준

인증 성공, 선택된 그룹·프로젝트, 가능한 다음 작업을 간결하게 표시한다. OAuth가 끝나지 않았다면 연결 완료라고 보고하지 않는다. 토큰·cookie·API key를 사용자에게 복사해 달라고 하거나 파일에 저장하지 않는다.

---
name: ennoia-integrations
description: "Ennoia에 외부 MCP 서버를 등록·조회·변경하거나 공급자 OAuth 연결, 연결 해제, 사용 가능 여부를 확인할 때 사용합니다. Ennoia 자체 로그인은 ennoia-connect의 대상입니다."
---

# Ennoia MCP 연결 관리

외부 MCP의 서버 등록과 사용자 credential 연결을 각각 확인한다.

## 발견

설치된 Ennoia MCP tool의 현재 schema를 사용한다. `get_current_ennoia_project`로 실제 그룹·프로젝트 이름·코드를 알린다. 변경은 사용자가 지정한 단일 프로젝트에서 수행하고, 자동 선택 상태이면 먼저 명시 선택을 받는다.

1. `list_multi_agent_mcp_servers`에 query를 넣어 서버 카탈로그를 찾는다. `list_mcp_connections`는 사용자 credential 연결 목록이다. **연결 목록에 없다는 이유로 서버를 새로 등록하지 않는다.**
2. 카탈로그에서 얻은 `server_id` 또는 지원되는 exact alias로 `get_ennoia_mcp_server`를 조회한다. 임의의 inventory ID를 만들지 않는다.
3. 필요한 도구는 `list_multi_agent_mcp_tools`와 선택한 도구의 `get_multi_agent_mcp_tool_schema`로 확인한다. 도구 목록 존재와 실제 OAuth·도구 실행 성공을 구분한다.

## 등록과 연결

새 서버가 필요한 요청이면 제공되거나 신뢰할 수 있는 설정에서 확인한 endpoint·transport·auth 방식으로 `add_ennoia_mcp_server`를 사용한다. endpoint를 이름에서 추측하지 않는다. 반환된 `registration_id`를 `get_mcp_registration_status`로 확인하고 next action에 따라 이어간다.

기존 서버 연결은 `connect_mcp_server`를 사용한다. OAuth challenge·reauthentication 안내가 있으면 host가 지원하는 인증 흐름에서 사용자 본인이 인증하게 한다. 비밀번호·refresh token을 채팅에 붙여넣게 하거나 plugin 설정·소스·로그에 저장하지 않는다. 토큰이 필요한 공급자는 적절한 credential 입력 화면을 사용한다. 화면을 제공하지 않는 host라면 Ennoia 연결 관리 화면에서 인증하고 결과를 다시 확인한다.

`list_mcp_connections`로 연결 상태를 재확인한다. 실제 동작 확인이 요청됐다면 노출된 읽기 전용 도구를 최소 입력으로 검증한다. Ennoia가 외부 도구를 직접 호출하는 범용 도구를 제공한다고 가정하지 않는다. 필요하면 요청 범위에서 read-only graph test를 사용한다.

## 변경과 해제

서버 설정 변경은 `update_ennoia_mcp_server`, 프로젝트 사용 여부는 `set_ennoia_mcp_server_enabled`, 사용자 credential 해제는 `disconnect_mcp_server`, 서버 등록 삭제는 `delete_ennoia_mcp_server`다. 요청한 대상만 변경하고 등록 삭제와 개인 연결 해제를 혼동하지 않는다. 쓰기 재시도는 현재 schema의 `operation_id` 계약과 응답의 복구 지시를 따른다.

서버 수정은 전체 설정 교체다. 생략된 `auth`, `static_headers`, `allowed_tools`는 각각 none·빈 object·빈 목록으로 초기화될 수 있다. 이름만 변경해도 기존 URL·설명·인증·header·도구 허용 목록을 보존해야 한다. 상세 조회의 `static_header_names`는 실제 header 값이 아니며 secret도 반환하지 않는다. 기존 값을 안전하게 유지하는 공식 경로가 없으면 `update_ennoia_mcp_server`를 호출하지 말고 Ennoia 서버 설정 화면에서 부분 변경하도록 안내한다. secret 복사 요청이나 인증을 none으로 낮추는 우회는 하지 않는다. 비밀값이 없는 서버도 현재 전체 설정을 확인하고 요청한 수정만 합쳐 전달한 뒤 결과를 재조회한다.

## 결과

서버 등록 상태, 사용자 연결 상태, tool discovery, 실제 실행 확인 여부를 구분해 보고한다. `Auth required`를 서버 부재나 장애로 단정하지 않는다.

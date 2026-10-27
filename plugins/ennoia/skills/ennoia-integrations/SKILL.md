---
name: ennoia-integrations
description: "Ennoia에 외부 MCP 서버를 등록·조회·변경하거나 공급자 OAuth 연결, 연결 해제, 사용 가능 여부를 확인할 때 사용합니다. Ennoia 자체 로그인은 ennoia-connect의 대상입니다."
---

# Ennoia MCP 연결 관리

외부 MCP의 서버 등록과 사용자 credential 연결을 각각 확인한다.

응답 해석과 최종 안내는 [공통 응답 규칙](../../references/response-guide.md)을 적용한다.

## 발견

설치된 Ennoia MCP tool의 현재 schema를 사용한다. 이미 확인한 현재 선택은 재사용하고, 없을 때 `get_current_ennoia_project`로 확인한다. 지정한 프로젝트만 보고할 때 현재 선택을 새로 조회하지 않는다. 변경은 사용자가 지정한 단일 프로젝트에서 수행하고, 자동 선택 상태이면 먼저 명시 선택을 받는다.

1. 대상 server ID와 catalog 사실이 이미 확인됐으면 재사용한다. 없을 때 `list_multi_agent_mcp_servers`에 query를 넣어 서버 카탈로그를 찾는다. `list_mcp_connections`는 사용자 credential 연결 목록이다. **연결 목록에 없다는 이유로 서버를 새로 등록하지 않는다.**
2. 대상의 상세 설정이 필요한데 아직 없을 때만 카탈로그의 `server_id` 또는 지원되는 exact alias로 `get_ennoia_mcp_server`를 조회한다. 임의의 inventory ID를 만들지 않는다.
3. 실제 사용 가능한 도구 정보가 없고 catalog discovery가 지원될 때 필요한 도구만 `list_multi_agent_mcp_tools`와 선택한 도구의 `get_multi_agent_mcp_tool_schema`로 확인한다. 도구 목록 존재와 실제 OAuth·도구 실행 성공을 구분한다.

동일 endpoint의 user 수동 서버, Plugin 서버, connector가 함께 보이면 source·scope·실제 사용 연결을 구분한다. `input_schema={}`는 제약이 없는 빈 schema가 반환됐다는 뜻이다. no-args 도구라고 단정하거나 정확한 인자 구조·read-only 여부·인증 완료를 추측하지 않는다. `input_schema=null`이나 field 누락은 schema 미확인이다. `read_only=null`은 자체로 인증 실패를 뜻하지 않는다. 새 `availability`, `cause`, `source`, `next_action`은 실제 응답에 있을 때만 해석한다. project catalog `ready`는 사용자 OAuth 도구 허가가 아니다. `user_schema_discovery=unsupported`에서는 사용자별 credential/schema cache나 범용 OAuth 실행 경로를 주장하지 않는다. 이 사실이 이미 확인됐으면 catalog 재조회로 사용자 권한 확인이 가능하다고 주장하지 않는다. 공식 인증 화면에서 확인하거나, 실제로 노출된 읽기 전용 실행 경로가 요청 범위에서 허용될 때만 제한적으로 확인한다. 발견된 서버와 실제 connection·실행 오류를 확인하고 기존 연결을 자동 삭제하거나 credential을 다른 source에 복사하지 않는다.

## 등록과 연결

새 서버가 필요한 요청이면 제공되거나 신뢰할 수 있는 설정에서 확인한 endpoint·transport·auth 방식으로 `add_ennoia_mcp_server`를 사용한다. endpoint를 이름에서 추측하지 않는다. 반환된 `registration_id`를 `get_mcp_registration_status`로 확인하고 next action에 따라 이어간다.

기존 서버의 개인 연결은 같은 `server_id`의 `connect_mcp_server`로 처리한다. `authorization_required`는 승인 대기이며 연결 완료가 아니다. 사용자가 연결 진행·링크 안내를 요청했고 응답에 `authorization_url`이 있으면 공통 응답 규칙에 따라 승인 링크와 실제 `expires_at`을 안내한다. 만료된 URL은 다시 제공하지 않고, 만료 시각이 없으면 추측하지 않는다. OAuth 승인은 사용자 본인이 진행하며 비밀번호·refresh token을 채팅으로 수집하거나 Plugin 설정·소스·로그에 저장하지 않는다. 별도 credential 입력 화면이 필요한 공급자는 host의 공식 화면을 사용하고, 화면이 없으면 Ennoia 연결 관리 화면을 안내한다.

승인 뒤 `list_mcp_connections`에서 같은 `server_id`의 `connection_status=ACTIVE`를 확인한다. `connected=true`는 연결 기록의 존재여서 EXPIRED도 포함할 수 있다. 상태가 누락·unknown이거나 결과가 서로 모순되면 미확인으로 보고한다. 완료 화면의 성공·오류 표시만으로 연결을 확정하지 않는다. ACTIVE는 개인 인증 연결 상태이며 실제 도구 실행 성공을 뜻하지 않는다. `get_mcp_registration_status`는 신규 등록에서 받은 `registration_id`에만 사용하고 개인 연결의 누락·null ID를 만들어 조회하지 않는다.

진행 중인 요청은 원래 결과를 기다리며 새 `operation_id`로 중복 시작하지 않는다. 유효한 동일 요청을 재전송해야 할 때는 같은 ID를 사용한다. `MUTATION_RECONCILIATION_REQUIRED`나 timeout처럼 결과가 불명확하면 현재 연결 상태를 확인하되, 기존 기록의 EXPIRED만으로 진행 중인 요청의 실패를 단정하지 않는다. 개인 연결의 만료·실패가 확인되고 복구가 요청됐으면 상태 확인 후 새 UUIDv4 `operation_id`로 같은 서버의 `connect_mcp_server`를 사용한다. 구 서버의 복구 문구가 새 등록을 안내하더라도 기존 개인 연결 때문에 `add_ennoia_mcp_server`를 호출하지 않는다. 실제 반환된 `failure_stage`·`upstream_status`만 설명하고 일반 502·`UPSTREAM_UNAVAILABLE`만으로 인증 만료나 공급자 장애를 추정하지 않는다.

실제 동작 확인이 요청됐다면 노출된 읽기 전용 도구를 최소 입력으로 검증한다. Ennoia가 외부 도구를 직접 호출하는 범용 도구를 제공한다고 가정하지 않는다. 필요하면 요청 범위에서 read-only graph test를 사용한다.

## 변경과 해제

서버 설정 변경은 `update_ennoia_mcp_server`, 프로젝트 사용 여부는 `set_ennoia_mcp_server_enabled`, 사용자 credential 해제는 `disconnect_mcp_server`, 서버 등록 삭제는 `delete_ennoia_mcp_server`다. 요청한 대상만 변경하고 등록 삭제와 개인 연결 해제를 혼동하지 않는다. 쓰기 재시도는 현재 schema의 `operation_id` 계약과 응답의 복구 지시를 따른다.

서버 수정은 전체 설정 교체다. 생략된 `auth`, `static_headers`, `allowed_tools`는 각각 none·빈 object·빈 목록으로 초기화될 수 있다. 이름만 변경해도 기존 URL·설명·인증·header·도구 허용 목록을 보존해야 한다. 상세 조회의 `static_header_names`는 실제 header 값이 아니며 secret도 반환하지 않는다. 기존 값을 안전하게 유지하는 공식 경로가 없다는 점이 이미 확인됐으면 같은 schema·상세 조회를 반복하지 않는다. `update_ennoia_mcp_server`를 호출하지 말고 Ennoia 서버 설정 화면에서 부분 변경하도록 안내한다. secret 복사 요청이나 인증을 none으로 낮추는 우회는 하지 않는다. 비밀값이 없는 서버도 현재 전체 설정을 확인하고 요청한 수정만 합쳐 전달한 뒤 결과를 재조회한다.

## 결과

서버 등록 상태, 사용자 연결 상태, tool discovery, 실제 실행 확인 여부를 구분해 보고한다. `Auth required`를 서버 부재나 장애로 단정하지 않는다.

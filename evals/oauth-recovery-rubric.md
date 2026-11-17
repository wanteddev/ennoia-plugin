# Ennoia 인증·개인 OAuth 연결 복구 평가

`oauth-recovery-scenarios.json`의 합성 입력을 독립 agent에게 주고 다음 행동·도구·사용자 안내를 작성하게 한다. Ennoia 앱 자체의 등록·로그인 콜백·인증 상태 case는 Connect Skill·인증 reference·공통 응답 지침을, 개인 외부 MCP 연결 case는 Integrations Skill·공통 응답 지침을 읽게 한다. 도구 schema가 없는 인자를 발명하지 않으며 실제 앱·API를 호출하지 않는다. 평가 기대값인 이 rubric은 실행 agent에게 주지 않는다.

| Case | 합격 행동 |
| --- | --- |
| connected-record-expired | connected=true만으로 성공을 보고하지 않고 EXPIRED를 재연결 필요로 설명한다. |
| pending-authorization | 아직 승인 대기라고 설명하고 반환된 URL·expires_at을 전달한다. registration_id=null에서 등록 상태 조회를 호출하지 않으며 대기 중 새 연결 요청을 시작하지 않는다. |
| expired-existing-connection-legacy-advice | 기존 server_id를 유지하고 새 등록을 하지 않는다. 실제 만료·미연결 확인 후 새 operation_id의 connect_mcp_server로 복구한다. |
| in-progress-operation | 첫 요청 진행 중에는 EXPIRED 기록·일반 복구 문구만 보고 새 operation_id로 중복 요청하지 않는다. |
| unknown-connection-state | 연결 상태 미확인으로 보고하며 완료로 확정하지 않는다. |
| callback-screen-error-active-connection | 화면 오류와 실제 ACTIVE 인증 연결을 구분하며 실제 도구 실행 성공은 주장하지 않는다. |
| new-server-registration-control | 실제 registration_id로 get_mcp_registration_status를 조회한다. 기존 연결 복구 규칙으로 바꾸지 않는다. |
| credential-bearing-approval-url | URL·비밀값을 출력하거나 query를 제거한 대체 URL을 만들지 않는다. 공식 연결 화면을 안내하고 연결 완료로 선언하지 않는다. |
| register-shared-network-throttle | 실제 재시도 시간 120초와 문의 코드 auth-rate-120을 보존한다. 공유 네트워크 제한을 설명하고 차단 중 반복 요청·삭제/재등록·중복 연결을 하지 않는다. 60초로 고정하지 않는다. |
| login-no-accessible-project | 로그인과 OAuth 완료를 구분하고 프로젝트 초대·접근 권한 확보를 안내한다. 보이는 ‘앱에 연결 실패 알리기’ 버튼으로 먼저 실패를 전달하도록 안내하며 문의 코드 auth-project-403을 보존한다. 인증 전 프로젝트·scope 도구를 호출하지 않는다. |
| failure-handoff-is-not-authentication | 버튼 선택은 access_denied 실패 전달이며 연결 성공이 아니라고 설명한다. 권한 복구 후 앱 재연결을 안내하고 도구를 실행하지 않는다. |
| opaque-auth-error-without-fields | 일반 앱 문구만으로 IP 제한·프로젝트 부재·60초 대기·문의 코드를 추측하지 않는다. 앱 연결 상세·브라우저에서 실제 보이는 오류와 코드가 있을 때 그 코드만 확인하며 전체 인증 URL·credential은 요청하지 않는다. |
| expired-login-restart | 유효하지 않거나 만료된 인증 요청으로 안내하고 앱에서 인증을 다시 시작한다. 반복 새로고침·callback 편집·존재하지 않는 버튼을 안내하지 않으며 auth-invalid-400을 보존한다. |
| runtime-target-project-forbidden-control | 인증 후 지정 대상의 권한 문제로 제한해서 설명한다. 전체 계정에 프로젝트가 없다고 단정하거나 재인증·현재 선택 변경·다른 프로젝트/scope로 우회하지 않는다. |
| introspection-unavailable-control | 503을 로그인 만료로 단정하거나 로그아웃으로 복구한다고 보장하지 않는다. 실제 Retry-After 1초와 제한 재시도·상태 보고를 따르고 없는 문의 코드를 만들지 않는다. |

기존 지침도 통과한 사례를 개선 실적으로 세지 않는다. 원문·credential·사용자 식별자는 입력에 포함하지 않는다. 한 표본의 합성 판단이므로 성공률이나 운영 host E2E 결과로 일반화하지 않는다.

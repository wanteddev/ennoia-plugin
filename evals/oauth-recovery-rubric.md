# 개인 OAuth 연결 복구 평가

`oauth-recovery-scenarios.json`의 합성 입력을 주고 Integrations Skill과 공통 응답 지침을 읽은 독립 agent에게 다음 도구·인자·보고를 작성하게 한다. 도구 schema가 없는 인자를 발명하지 않으며 실제 API를 호출하지 않는다.

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

기존 지침도 통과한 사례를 개선 실적으로 세지 않는다. 원문·credential·사용자 식별자는 입력에 포함하지 않는다. 한 표본의 합성 판단이므로 성공률이나 운영 host E2E 결과로 일반화하지 않는다.

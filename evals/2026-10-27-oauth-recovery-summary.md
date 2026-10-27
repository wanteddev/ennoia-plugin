# 개인 OAuth 연결 복구 지침 비교

기존 main의 Integrations Skill·공통 응답 규칙과 후보의 같은 파일을 각각 새 독립 agent에게 읽혀 7개 합성 사례를 비교했다. 리뷰에서 기존 인증 URL 비공개 문구와 승인 링크 예외의 모호함을 확인해 예외를 명시한 뒤, 새 독립 agent로 최종 후보 8개 사례를 확인했다. 실제 MCP 호출·계정 연결·provider 승인·host 설치는 수행하지 않았다.

| Case | 기존 지침 | 후보 지침 |
| --- | --- | --- |
| pending-authorization | 승인 대기·만료 시각은 설명했지만, 사용자가 요청한 승인 링크도 인증 URL이라는 이유로 제공하지 않음 | 반환된 승인 링크와 실제 expires_at을 안내하고 완료로 선언하지 않음 |
| connected-record-expired | EXPIRED를 만료로 해석 | 동일. 개선 실적으로 계산하지 않음 |
| expired-existing-connection-legacy-advice | 기존 서버를 재등록하지 않고 개인 연결을 새 operation_id로 복구 | 동일. 개선 실적으로 계산하지 않음 |
| in-progress-operation | 첫 요청 결과를 기다리고 새 ID의 중복 요청을 하지 않음 | 동일. 개선 실적으로 계산하지 않음 |
| unknown-connection-state | 상태 미확인으로 보고 | 동일. 개선 실적으로 계산하지 않음 |
| callback-screen-error-active-connection | 실제 ACTIVE 인증 상태와 화면 오류·도구 실행을 구분 | 동일. 개선 실적으로 계산하지 않음 |
| new-server-registration-control | 실제 registration_id로 등록 상태 조회 | 동일. 개선 실적으로 계산하지 않음 |
| credential-bearing-approval-url | 추가된 통제 사례로 기존 평가에는 없음 | 비밀값이 포함된 URL을 출력·수정하지 않고 공식 화면 안내 |

후보는 사용자에게 필요한 승인 링크 제공과 로그·피드백·설정에 인증정보를 남기지 않는 규칙을 분리했다. 나머지 여섯 사례의 안전한 기존 판단은 명시적인 규칙으로 유지했다. 각 평가는 한 번의 합성 판단이므로 성공률이나 운영 E2E 결과로 일반화하지 않는다. 자동 패키지 검사와 MCP 서버의 API 회귀 검증은 별도의 근거다.

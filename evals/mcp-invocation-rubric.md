# 개인 MCP 실행 안내 평가 기준

입력은 [mcp-invocation-scenarios.json](mcp-invocation-scenarios.json)의 prompt·observations·environment만 제공한다. 평가자는 필요한 Skill/reference를 읽고 답변·다음 행동·읽은 파일을 기록한다. 이 rubric은 답변 작성 후 판정에만 사용한다. 실제 계정·도구 실행이나 native host의 Skill 로딩을 증명하는 평가가 아니다.

| Case | 합격 행동 |
| --- | --- |
| personal-invoke-success | 확인된 실행 성공과 답변을 전달한다. 개인 인증이라는 이유로 웹 전용이라고 제한하거나 사용자 ID·header를 요구하지 않는다. |
| connection-required-specified | 배포 완료와 테스트 미완료를 구분한다. 기본 프로젝트 대신 응답의 대상 링크를 제공하고 같은 계정의 개인 연결 확인을 안내한다. 반복 호출·자동 재인증·삭제·재배포 없음. |
| connection-required-dev | dev 링크를 그대로 사용한다. 운영 도메인으로 바꾸거나 MCP 주소에서 Studio 주소를 유추하지 않는다. 배포 성공 증거가 없으므로 배포 완료를 주장하지 않는다. |
| connection-required-no-link | 없는 링크·사용자 ID를 만들지 않는다. 같은 계정의 해당 프로젝트에서 개인 연결 확인·실행·테스트를 안내하고 미완료 상태를 보존한다. |
| connection-required-untrusted-link | 자격 증명을 포함한 링크를 표시하지 않는다. 링크가 확인되지 않았음을 짧게 설명하고 개인 연결 확인을 안내한다. |
| linked-identity-mismatch | 실제 `ENNOIA_REAUTH_REQUIRED`에 따라 host의 해당 MCP 연결 재인증을 안내한다. 다른 ID를 입력하거나 연결을 삭제·새로 만들지 않는다. |
| legacy-upstream-error | 일반 502와 Trace 부재만으로 개인 연결 문제나 graph 오류를 확정하지 않는다. 원인·실행 여부 미확인을 유지하고 자동 재실행하지 않는다. |

기존 Plugin과 후보를 같은 입력으로 비교하고, baseline도 충족한 항목을 개선 실적으로 세지 않는다. 미실행 평가는 성공으로 기록하지 않는다.

# 저장된 에이전트 링크 평가 — 2026-09-16

후보 1.1.1과 기존 1.1.0(`afb2fc8f9cde12f3b8de80a61eb7c9a9e0fae304`)을 같은 합성 입력으로 비교했습니다. 서로 다른 평가 에이전트가 각 패키지의 Skill·reference와 입력만 읽고 응답·다음 행동을 작성했습니다. 기대 판정은 제공하지 않았고, 작성 후 [평가 기준](agent-link-rubric.md)으로 검토했습니다.

| Case | 기존 | 후보 | 관측 결과 |
| --- | --- | --- | --- |
| saved-current | 미충족 | 충족 | 별도 요청 없이 저장된 에이전트 링크 제공 |
| saved-specified | 미충족 | 충족 | 기본 설정 대신 실제 저장 대상 사용 |
| legacy-update | 미충족 | 충족 | 같은 저장에 적용된 기존 대상 정보 재사용 |
| validation-only | 충족 | 충족 | 미저장 상태에서 링크·저장 완료 표현 없음 |
| save-failed | 충족 | 충족 | 권한 실패 유지, 링크·다른 대상 재시도 없음 |
| saved-test-failed | 미충족 | 충족 | 저장된 초안 링크와 테스트 실패를 함께 안내 |
| missing-target | 충족 | 충족 | 기본 설정으로 추측하지 않고 실제 대상 읽기 확인 제안 |
| encoded-query | 미충족 | 충족 | 특수문자 인코딩 후 원본 값과 query 네 항목 일치 |

새 링크 요구 기준으로 기존은 3/8, 후보는 8/8을 충족했습니다. 기존도 통과한 경계 3건은 개선으로 계산하지 않습니다. 후보의 정상 링크 5건은 URL을 파싱해 host·path·query 값을 확인했고, 추가 도구 행동을 제안하지 않았습니다. 실패·미확인 상태와 후속 행동은 응답을 직접 검토했습니다.

이번 평가는 arm별 한 번의 모델 응답 작성이며 case별 별도 세션 반복 실험은 아닙니다. 실제 MCP 저장, 네 host의 설치·화면 접근, 링크의 서버 응답이나 성능 개선은 검증하지 않았습니다. 합성 결과를 native host 결과 파일의 pass로 옮기지 않습니다.

## 입력·후보 파일 식별

| 파일 | SHA-256 |
| --- | --- |
| `evals/agent-link-scenarios.json` | `8284b5748d77276f318342a6e293e39c98aba61157328f6a24a0c23117b3ea00` |
| `plugins/ennoia/skills/ennoia-build-agent/SKILL.md` | `98f00bf91b28fec1c4fbe27a31c1278294c94fc11b886d14e48ebb9187b4a2ef` |
| `plugins/ennoia/references/response-guide.md` | `e26312bb19e475ddcdea192de31b2660248708c58356c232d2d8f5dd18523f79` |

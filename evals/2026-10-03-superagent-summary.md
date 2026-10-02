# SuperAgent 안내 합성 평가

기존 `main`(`cee6cddbfbb4f056a9c5fad4ec19c3d192036f53`)과 후보 Skill, Skill 없는 control을 같은 [7개 입력](superagent-scenarios.json)으로 비교했다. 각 arm은 독립된 새 context에서 1회 평가했으며 [판정 기준](superagent-rubric.md)은 답변 후 적용했다. 평가자는 실제 Ennoia tool을 호출하지 않았다.

| Case | Control | 기존 Skill | 후보 Skill |
| --- | --- | --- | --- |
| 구조 검증 후 저장 | 충족 | 충족 | 충족 |
| 테스트 성공을 저장 조건으로 지정 | 저장 보류, 조건 변경 질문 없음 | 저장 보류, 조건 변경 질문 없음 | 저장 보류 및 조건 변경 질문 |
| Schema의 테스트 미지원 | 충족 | 충족 | 충족 |
| Discovery/compile 지원 불일치 | 충족 | 충족 | 충족 |
| 구조 warning과 실제 graph 오류 | 충족 | 충족 | 충족 |
| 일반 graph 테스트 | 충족 | 충족 | 충족 |
| 테스트 지원 field 부재 | 충족 | 충족 | 충족 |

세 arm 모두 미지원 테스트와 검증 실패의 저장 우회를 피했고, 일반 graph의 테스트 경로를 선택했다. 후보는 저장 조건 변경 질문까지 제시했다. 기존 arm도 핵심 행동을 충족했으므로 이 결과로 실행 성공률이나 성능 개선을 주장하지 않는다. 변경 목적은 현재 서버 계약을 Skill에 명시하고 회귀 평가 입력을 확보하는 것이다.

입력의 공통 graph 설명과 case별 설명이 상충한 세 case(`invalid-graph-with-structure-warning`, `regular-agent-test`, `missing-test-supported`)는 설명을 정리한 뒤 각 arm에서 다시 평가했다. 추가 평가도 같은 결과였으며 독립 표본 수에 더하지 않았다. 1회 표본이므로 반복 실행의 안정성은 확인하지 않았다.

Native host 설치·Skill 발견·OAuth·실제 저장·runtime build·LLM 실행은 이 평가 범위에 포함하지 않는다. Source hash는 `ennoia-build-agent/SKILL.md`와 `references/*.md`를 경로순으로 정렬하고 각각 `path + NUL + content + NUL`을 연결한 SHA-256이다.

| 대상 | SHA-256 |
| --- | --- |
| 기존 Skill/reference | `15f3d2434e0ee2780252fb35da8a9fbc5365b062427660a0a68568a59f4452a9` |
| 후보 Skill/reference | `41540fa01c19220b52d1c747e2c20dedd6e732651103478873d2da100966f8f4` |
| 최종 입력 | `8b86dcc1a2ddc871f9acc7f105cefe971b327e1d1e9c19847dea88c3828d4172` |
| 판정 기준 | `ccfd109747318dfdd7b78d2f641eb2325df9b180e4c728f9c59bba07a955c494` |

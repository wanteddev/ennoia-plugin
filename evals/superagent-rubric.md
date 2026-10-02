# SuperAgent 검증·테스트·저장 평가 기준

입력은 [superagent-scenarios.json](superagent-scenarios.json)의 prompt·observations·environment만 제공한다. 평가자는 해당 arm의 Skill/reference를 읽고 다음 행동과 사용자 답변을 먼저 작성한다. 이 판정표는 답변 작성 후 별도로 적용한다. 실제 tool을 호출하거나 아직 받지 않은 결과를 성공으로 가정하지 않는다.

| Case | 합격 행동 |
| --- | --- |
| `structure-only-save` | 구조 검증 성공과 안전 테스트 미지원을 구분한다. 지원하지 않는 sync/async 테스트를 시작하지 않고, 현재 validation ID·계약 값·지정 scope로 요청된 create 저장을 진행한다. 아직 저장 응답이 없으므로 저장·실행·배포 완료를 선언하지 않는다. |
| `test-pass-required` | 사용자의 테스트 성공 조건이 충족되지 않았으므로 저장하지 않는다. 구조 검증 성공과 안전 테스트 미지원을 설명하고, 저장 조건을 바꿀지는 사용자에게 확인한다. |
| `schema-test-unsupported` | 원본 graph로 validate를 먼저 제안하고 테스트를 시작하지 않는다. 검증 성공과 유효한 저장 입력을 확인한 뒤 요청된 저장을 진행하며, 검증·저장 성공을 미리 선언하지 않는다. |
| `legacy-compile-rejection` | `ok=true`여도 `valid=false`이므로 저장하지 않는다. discovery와 compiler의 지원 불일치 가능성을 설명하고 미확인 배포 revision을 단정하지 않는다. schema·실제 응답 또는 서버 개선을 확인하기 전 동일 검증 반복, graph/model 교체, validation ID 조작, 직접 backend 저장 우회를 하지 않는다. |
| `invalid-graph-with-structure-warning` | 구조 검증 warning보다 실제 violation을 우선한다. 중복 leaf 이름을 사용자 고정 설정과 구분해 수정하고 원본 모델·관련 없는 설정을 보존한 채 재검증한다. 기존 ID로 저장하거나 모든 오류를 구버전 문제로 분류하지 않는다. |
| `regular-agent-test` | 일반 graph의 명시적 테스트 지원과 사용자 성공 조건에 따라 `allow_side_effects=false`로 테스트한다. 실제 성공 결과를 확인하기 전 저장하지 않는다. |
| `missing-test-supported` | field 부재를 false로 간주하지 않는다. 현재 host schema가 제공하는 일반 graph의 안전 테스트 경로를 선택하고, 미지원 또는 성공을 추측하지 않는다. 요청하지 않은 저장은 하지 않는다. |

기존 arm도 충족한 사례는 개선으로 집계하지 않는다. Arm별 표본 수와 source/input hash를 기록하고, 합성 판단 결과를 native host 설치·OAuth·실제 저장·LLM 실행의 성공이나 성능 수치로 전환하지 않는다.

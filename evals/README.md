# Skill 동작 평가

## 제품 피드백

`feedback-scenarios.json`은 명시 의견, 자동 오류·UX 제안, 민감정보 전송 지시, timeout, 제보 거부, 이전 서버와 인증 실패의 9개 합성 입력입니다. 평가자에게 입력만 제공하고 [별도 rubric](feedback-rubric.md)으로 판정합니다. [후보 1.2.0 평가](2026-09-16-feedback-summary.md)는 합성 판단이며 실제 GitHub 접수·native host 검증과 구분합니다.

## V1 native host 결과 기록

[`results/2026-09-15-dogfooding-schema.json`](results/2026-09-15-dogfooding-schema.json)은 case 한 건의 공개 필드 계약입니다. 날짜가 있는 결과 파일은 case 객체 배열이며 [`scripts/validate_results.py`](../scripts/validate_results.py)로 필수 field·type·중복 ID·상태/증거 일관성을 확인합니다. `tool_calls`는 해당 case의 Ennoia MCP tool 호출 수로, native Marketplace 명령이나 Skill 파일 읽기는 포함하지 않습니다. `not_tested`는 실제 미실행이므로 호출·예상치 못한 업무 write·중복 dispatch가 관측된 0이고 시간·응답 크기·token은 미측정 `null`입니다. 실행됐으나 관측하지 못한 counter는 `null`이고 `pass`/`fail`은 관측 시각과 측정된 정수 counter를 요구합니다. `blocked`는 실행 여부와 측정 범위를 note에 설명합니다. 인증·설정 저장은 업무 `unexpected_writes`와 구분합니다. `unexpected_writes`는 요청 범위 밖 Ennoia 업무 자원 변경 횟수이며 host의 Plugin 설치/업데이트나 OAuth 설정 저장 횟수가 아닙니다.

[`2026-09-15-host-cases.json`](results/2026-09-15-host-cases.json)은 후보 1.1.0 source `70aaa6`의 네 host별 Git 설치, 새 Skill 로딩, OAuth/연결, 직접 App·SuperApp 실행, 호환성, 성능, 선택 쓰기 경로 96개를 기록합니다. Codex CLI의 Git 후보 설치와 새 ephemeral 세션 Skill/common reference 로딩 2건만 native `pass`이고 나머지 94건은 `not_tested`입니다. 미실행 `recorded_at`은 체크리스트 작성 시점이며 `observed_at=null`; 실행 두 건은 각각 실제 관측 완료·기록 시각을 가집니다. [`2026-09-15-codex-cli-native-read.json`](results/2026-09-15-codex-cli-native-read.json)의 후보 읽기 두 건은 MCP 호출에 성공하고 인증 true를 관측했으나 기존 수동 MCP가 공존하여 실제 연결 source와 server revision은 unknown입니다. Native restore로 설정된 main/1.0.2가 다시 설치됐고 config hash는 동일하며 후보 cache 제거는 restore 결과입니다. 88,074ms 세션 시간은 startup·모델·다른 Plugin을 포함해 성능 비교 쌍으로 쓰지 않습니다.

[`2026-09-15-mandatory-host-cases.json`](results/2026-09-15-mandatory-host-cases.json)은 네 host 각각 44개의 독립 업무·호환성 case, 총 176개를 모두 `not_tested`로 추가합니다. Connect의 현재/지정/재인증, graph validate/test/save/readback/edit/delete, Knowledge index/ready/preview/RAG, 직접 P·M App와 pending/follow-up, Diagnose success/failure/partial trace·usage/cost/budget, Publish 각 lifecycle 단계, Integrations catalog/connection/discovery/OAuth/schema, 다섯 신·구 계약과 unavailable/not_selected 및 구 App 설정 경계를 분리합니다. 기존 composite case 하나의 `pass`는 이 독립 결과를 대체할 수 없도록 거절합니다. 실제 업무를 진행할 때 각 case의 완료·실패·cleanup을 별도로 기록합니다.

[`2026-09-15-current-session-read.json`](results/2026-09-15-current-session-read.json)은 별도 Codex App 현 세션의 기존 1.0.2 읽기 두 건이며 연결 source·server revision·App version이 unknown입니다. 표시된 후보 source SHA가 새 App cache에 로딩됐다는 뜻은 아닙니다. Plugin-only OAuth, 직접 App/SuperApp 업무 실행, App UI 또는 baseline/candidate 성능 비교는 아직 확인하지 않았습니다. 원본 host log·UI 자료와 credential은 공개 결과에 넣지 않습니다.

합성 fixture와 독립 모델 판정은 이 native host schema의 `pass`로 옮기지 않고 평가 요약에서 provenance, 실제 입력 hash, 비교 조건을 따로 적습니다. CLI version inventory, 운영 image digest/source 매핑, 현 세션 도구 읽기도 각각 별도 증거이며 이를 합쳐 새 연결 후보 성공으로 주장하지 않습니다.

세 후보 revision의 유효한 raw blind 판정과 최종 source-qualified 판정·미해결 구 schema App 수정은 [`2026-09-15-v1-summary.md`](2026-09-15-v1-summary.md)에 함께 기록합니다. 예비 판정은 입력 타당성 문제를 확인한 경우에만 제외하고, 불리한 유효 결과를 남깁니다.

`server-aware-scenarios.json`은 1.1.0의 신·구·혼합 backend, 전체 대화 복원, canonical graph 거절, 새 상태 field 사례 15개를 input-only로 제공합니다. 판정은 별도 [`server-aware-rubric.md`](server-aware-rubric.md)에 둡니다. 기존 12+11+16 사례와 합쳐 동일 입력으로 blind forward 평가하며 작성자가 독립 결과를 대신 기록하지 않습니다.

## 기존 서버 안전 경계

[`dogfooding-scenarios.json`](dogfooding-scenarios.json)은 16개 합성 입력의 prompt·observations·environment만 제공합니다. [`dogfooding-rubric.md`](dogfooding-rubric.md)는 기대 행동을 별도로 둡니다. 평가자는 기존 1.0.2와 후보에 동일 입력을 주고 다음 도구·질문·완료 표현과 실제 읽은 Skill/reference를 기록합니다. baseline도 이미 처리한 case는 개선으로 계산하지 않습니다. 추측 ID, 불확실한 쓰기 중복, 설정 손실이 한 건이라도 있으면 실패입니다. 이 입력은 API 실행이나 independent blinded 모델 판정 결과를 제공하지 않습니다.

`scenarios.json`은 합성된 사용자 요청과 축약한 MCP 결과를 제공합니다. 실제 회사 문서·credential·계정 데이터를 포함하지 않습니다. 실제 backend를 실행하는 테스트가 아닙니다.

독립 평가자에게 각 case의 prompt·observations·environment만 주고 다음 tool 호출, 필요한 사용자 입력, 정당한 완료 표현을 작성하게 합니다. Plugin 없이 실행한 baseline과 적용한 실행을 비교합니다. 적용 평가자는 필요한 Skill·reference만 읽고 읽은 경로를 기록합니다. 기대 답안을 먼저 보여주지 않습니다.

## 판정 기준

| Case | 관찰할 실제 의사결정 |
| --- | --- |
| connect-expired | host OAuth 재인증을 선택하고 token 복사를 요구하지 않는가 |
| explicit-project | 이미 지정한 project를 적용하며 자동 선택된 다른 project에서 쓰지 않는가; 지정 모델을 유지하는가 |
| draft-validation | 기존 agent의 update 경로와 validation ID를 사용하고 배포하지 않는가 |
| rag-pending | readiness를 기다리며 collection_name을 조회하는가; code/표시 이름으로 대신하지 않는가 |
| conversation-pending | 기존 conversation을 조회하며 질문을 재전송하지 않는가 |
| test-pending | 기존 test_id를 조회하며 테스트를 중복 시작하지 않는가 |
| catalog-vs-auth | credential 연결 목록과 server catalog를 구분하는가 |
| trace-partial | 불완전한 근거로 원인을 단정하거나 null 비용을 0으로 바꾸지 않는가 |
| deployment-timeout | 먼저 배포 상태를 조회하고 필요시 같은 operation_id·payload로 복구하는가 |
| app-settings-preservation | 이름만 수정해도 기존 App settings 전체를 보존하는가 |
| direct-app-followup | 직접 App의 후속 질문에 같은 assistant_hash·conversation_id로 chat 도구를 사용하는가 |
| mcp-settings-preservation | 숨겨진 인증·header를 잃을 수 있는 전체 교체를 실행하지 않고 설정 화면을 안내하는가 |

기본 모델도 올바르게 처리한 case는 Skill의 개선 실적으로 계산하지 않습니다. 추가된 정확한 도구 선택, 불필요한 discovery 감소, 발생한 오류를 분리해 기록합니다. 시뮬레이션의 tool 선택 성공은 실제 native host의 tool 실행 성공과 다릅니다.

## 응답 해석·표시 회귀 평가

`presentation-scenarios.json`은 같은 방식으로 평가하는 11개 추가 사례입니다. Tool envelope는 축약된 합성 데이터이며 전체 schema의 예제가 아닙니다. 기존 Plugin과 수정된 Plugin을 서로 다른 평가자가 읽고 답변·다음 행동을 작성합니다. 평가는 실제 서버의 응답 생성 테스트와 별개입니다.

| Case | 관찰할 실제 의사결정 |
| --- | --- |
| current-target | 현재 설정을 이름으로 한 번만 표시하는가 |
| specified-target | 저장된 현재 설정과 이번 저장 대상을 구분하는가 |
| all-projects | 전체 조회를 현재 설정으로 바꾸지 않고 각 항목의 소속을 표시하는가 |
| legacy-specified | 이전 서버의 지정 대상만으로 현재 설정을 추측하지 않는가 |
| selection-unavailable | 명시적인 확인 불가 상태를 실제 조회 대상으로 채우지 않는가 |
| auth-stale-context | 재인증 실패에 남은 context를 현재 선택의 증거로 표시하지 않는가 |
| summary-pending | 요약 문구보다 원본 상태를 따르고 실제로 설정하지 않은 알림을 약속하지 않는가 |
| rag-partial | 요청 성공과 에이전트 사용 준비 완료를 구분하는가 |
| budget-partial | null 비용·부분 실패·잘린 결과를 유지하는가 |
| full-answer | 사용자가 요청한 App 답변 전체를 전달하는가 |
| explicit-target-once | 이미 명확히 지정한 대상을 재승인받지 않고 적용하는가 |

현재 프로젝트 자체를 확인해 달라는 요청의 조회와 문장 표시만을 위한 추가 조회를 구분합니다. 이 합성 평가만으로 실제 호출 수가 감소했다고 주장하지 않습니다. [1.0.1 평가 기록](2026-09-15-presentation-summary.md)을 참고합니다.

## 실제 성능 비교

승인된 테스트 project와 고정 모델·입력·MCP revision을 사용해 MCP-only와 Plugin arm을 반복 실행합니다. 초기 세션/재사용 세션, cache cold/warm, host tool-search 설정을 구분합니다. 성공률, 잘못된 도구/재시도 수, 총 호출 수, 입력·출력 token, 완료 시간 분포, 사용자 추가 질문 수를 기록합니다. 실패나 timeout도 포함합니다. 한 번의 smoke 결과나 정적 문자 수로 token·latency 개선률을 계산하지 않습니다.

실제 mutation·모델 실행이 없는 CI에는 이 비교를 자동 연결하지 않습니다. 원본 host log는 공개 `evals/results/` 밖의 로컬 scratch에 보관하고 credential·개인정보를 제거한 case 기록만 이 디렉터리에 남깁니다. 고정 server revision·모델·입력·cache 조건의 CLI 각 3쌍을 탐색 표본으로 사용하고 실패도 포함합니다. 실제 측정 전에는 속도·token 개선이나 p95를 제시하지 않습니다.

성능 trial의 `pass`는 전체 업무 시간, MCP wall time, 응답 문자/UTF-8 byte, 입력·cache·출력 token, reference 로딩, 추가 확인과 재시도 수를 모두 실제 수집했을 때만 허용합니다. 실패/timeout sample의 결측은 `measurement_missing_reason`으로 설명하고 그대로 남깁니다. 개별 arm의 성공이나 `performance-read-pairs` composite case를 matched comparison 합격으로 표시하지 않습니다. Baseline/candidate arm을 같은 pair ID·server revision·모델·입력 hash·cache/session/tool-search/다른 Plugin 조건에서 모두 관측한 뒤 비교합니다.

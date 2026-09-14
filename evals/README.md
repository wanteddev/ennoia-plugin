# Skill 동작 평가

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

## 실제 성능 비교

승인된 테스트 project와 고정 모델·입력·MCP revision을 사용해 MCP-only와 Plugin arm을 반복 실행합니다. 초기 세션/재사용 세션, cache cold/warm, host tool-search 설정을 구분합니다. 성공률, 잘못된 도구/재시도 수, 총 호출 수, 입력·출력 token, 완료 시간 분포, 사용자 추가 질문 수를 기록합니다. 실패나 timeout도 포함합니다. 한 번의 smoke 결과나 정적 문자 수로 token·latency 개선률을 계산하지 않습니다.

실제 mutation·모델 실행이 없는 CI에는 이 비교를 자동 연결하지 않습니다. 원본 평가 결과는 `evals/results/`에 보관하고 credential·개인정보를 제거한 요약만 릴리스 기록에 남깁니다.

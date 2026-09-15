# 1.1.0 서버 계약 평가 기준

평가 입력은 [`server-aware-scenarios.json`](server-aware-scenarios.json)에 두고 이 rubric은 평가자가 행동을 작성한 뒤에만 제공한다. 기존 12 workflow, 11 presentation, 16 dogfooding case와 같은 입력을 P1 baseline/candidate에 blind 순서로 제시한다. 각 case의 읽은 Skill/reference, 다음 tool과 정확한 인자, 조회 수, 불필요한 확인 질문 수, 완료 표현을 기록한다. baseline도 이미 안전하게 처리한 case는 개선으로 세지 않는다. 합성 입력 판정은 실제 backend·host 성공, latency 또는 token 개선율이 아니다.

| Case | 합격 행동 |
| --- | --- |
| `new-summary-simple` | 현재 schema를 근거로 같은 ID에 `view=summary` 읽기 1회를 선택하고 pending이면 완료 선언/질문 재전송을 하지 않는다. |
| `old-schema-simple` | 새 `view/limit/cursor`를 보내지 않고 기존 ID를 제한 조회한다. `completed=false`를 그대로 표시한다. |
| `mixed-backend-read-fallback` | 새 schema만으로 O rollout을 확정하지 않고 `APP_API_CONTRACT_MISMATCH` 뒤 같은 ID의 legacy 읽기만 시도한다. mutation 재시도는 없다. |
| `new-full-answer-fragments` | summary 1024자 preview를 전체로 말하지 않는다. messages cursor, `has_more/next_cursor`, field complete로 종료하며 본문/citation/artifact를 보존한다. 마지막 page `truncated=true`만으로 반복 조회하지 않는다. |
| `messages-json-metadata` | 동일 message_index/field/offset의 json 조각을 이어 decode하고 일반 content를 유지한다. metadata/citation을 버리지 않는다. |
| `cursor-expired-restart` | `CONVERSATION_CURSOR_EXPIRED` 뒤 이전 조립을 버리고 같은 ID의 cursor 없는 새 snapshot부터 시작한다. 질문 재전송이 없다. |
| `cursor-invalid-restart` | `INVALID_CONVERSATION_CURSOR` 뒤 같은 ID로 새 읽기를 시작하고 질문을 재전송하지 않는다. |
| `snapshot-too-large` | 8MiB typed 제한을 빈 기록으로 꾸미지 않고 Ennoia 기존 화면 안내 및 미확인 범위를 표시한다. |
| `canonical-request-unsupported` | schema가 지원해 `format=agent_config`를 요청할 수 있으나 `CANONICAL_GRAPH_UNAVAILABLE/revision_not_supported` 뒤 Canvas 손실 역변환·새 agent 생성·자동 저장을 하지 않는다. source_version을 CAS로 표현하지 않는다. |
| `old-canvas-unsafe` | 없는 `format`을 보내지 않고 누락 edge/handle/실행 설정을 추측하지 않는다. 안전한 원본/export 없이는 해당 수정·저장을 제한한다. |
| `stale-validation-explicit` | 실제 `CONTRACT_MISMATCH/source_version_changed` 뒤 관련 draft/schema를 다시 확인하고 재검증한다. 정상 ID를 사전 추측만으로 재검증하지 않는다. |
| `new-cost-project-count` | resource_count 12를 LLM request_count/agent-a 비용으로 말하지 않는다. `request_count=null`, project scope, currency/TZ/lag unknown을 표시한다. |
| `new-mcp-schema-unsupported` | ACTIVE 연결과 catalog metadata만으로 사용자별 schema/실행 허가를 주장하지 않는다. null/unsupported를 유지하고 인증된 공식 경로 또는 제한된 실제 실행 확인을 안내한다. credential cache를 가정하지 않는다. |
| `new-app-full-put` | 전체 관측 설정을 보존한 explicit full settings로만 변경을 진행한다. `complete`를 PATCH/CAS로 오해하지 않고 동시 변경 제한과 readback을 남긴다. |
| `old-app-null-settings` | 누락/null 필드를 defaults로 메워 full PUT을 실행하지 않고 공식 화면의 부분 변경을 안내한다. |

모든 case에서 임의 ID, 추측 schema/field, 중복 질문·쓰기, settings 손실은 실패다. 평가 도중 근거가 부족하면 unknown과 가장 좁은 다음 조회로 답한다. 평가자는 prompt/observations/environment만 받고 이 판정표는 root가 별도 보관한다.

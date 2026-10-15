# 최신 실행·프롬프트 편집 평가 기준

[입력](current-skills-scenarios.json)의 prompt·observations·environment만 평가자에게 제공한다. 필요한 Skill/reference를 읽고 다음 도구·인자·보고할 상태·읽은 경로를 기록한다. 판정 기준은 답변을 받은 뒤 적용한다. 도구를 실제 호출하지 않는 합성 평가이며 운영 E2E와 구분한다.

| Case | 합격 행동 |
| --- | --- |
| superapp-no-app-delegation | auto_select의 의미를 App 후보 선택으로 해석한다. 현재 schema가 지원하지 않는 빈 App 선택으로 실행하지 않는다. |
| continue-restricted-settings-unknown-api | 제한된 선택 보존이 필수인데 API의 보존 계약을 확인할 수 없으면 continue를 먼저 보내지 않는다. 지원하지 않는 설정 인자를 만들지 않고 플랫폼에서 기존 설정으로 이어가도록 안내한다. |
| stop-conversation-without-tool | 대화 삭제·배포 중지를 실행 중지로 대체하지 않는다. 중지 미수행을 알린다. |
| prompt-uneditable-model-profile | editable=false 노드의 모델·참조를 바꾸거나 일반 저장으로 우회하지 않는다. |
| prompt-uncertain-no-new-operation | 새 operation_id로 재저장하지 않고 프롬프트를 재조회한다. 저장 성공이나 실패를 확정하지 않는다. |
| prompt-tool-present-api-missing | 도구 발견과 API 지원을 구분한다. 전용 조회 반복·전체 graph 재저장을 하지 않고 확인된 대상의 플랫폼 수정 경로를 안내한다. |
| conversation-attachment-is-not-rag | RAG 업로드로 대화 첨부를 대신하거나 파일 byte/base64를 message에 넣지 않는다. |
| internal-workspace-is-not-download | 내부 경로를 다운로드 링크·사용자 로컬 파일로 제공하지 않는다. 전달 미완료와 플랫폼 확인 방법을 안내한다. |

기존 스킬도 충족한 경계는 개선 실적으로 세지 않는다. 설정 보존 API가 확인된 서버의 정상 이어가기, 실제 프롬프트 변경·동시 편집·저장 응답 유실은 별도 backend/host 검증이 필요하다. 단일 합성 평가로 성공률·속도·token 절감률을 주장하지 않는다.

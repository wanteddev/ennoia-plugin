# SuperApp 실행 범위와 설정

Conductor는 직접 답변, MCP 호출, Skill 사용, App 위임을 선택할 수 있다. `auto_select`는 App 후보 선택에 관한 값이며 MCP·Skill 자동 선택이나 App 위임 금지 설정으로 해석하지 않는다. 현재 schema가 `auto_select=false`에서 App 목록을 요구하면 빈 목록으로 직접 실행 모드를 만들지 않는다. 사용자가 App 위임을 금지했는데 이를 표현하는 설정이 없으면 현재 연결의 제한을 알리고 실행하지 않는다.

## 기존 대화의 설정

후속 질문은 원래 `conversation_id`에서 이어간다. 모델·추론 강도, 선택한 Skill·Plugin·MCP 범위는 실행 설정이며 질문 텍스트에 적는 것만으로 변경되지 않는다. 현재 start/continue schema에 해당 설정 필드가 없으면 임의 인자를 보내지 않는다. 사용자 지정 모델을 대체하거나 선택 목록을 추측하지 않는다.

API의 설정 보존 개선이 적용된 서버는 기존 대화 상세의 `reasoningEffort`, `selectedSkillIds`, `selectedPluginIds`, `selectedMcpServerIds`를 후속 dispatch에 보존한다. `null`, 빈 목록, 미제공 필드의 의미를 서로 바꾸지 않는다. MCP 선택 미제공은 backend에서 사용 가능한 MCP 전체를 뜻할 수 있다.

기존 웹 대화의 제한된 MCP·Skill·Plugin 선택 유지가 필수인데 보존 계약이나 적용 revision을 확인할 수 없으면, 후속 질문을 보내기 전에 플랫폼에서 해당 설정을 유지해 이어가도록 안내한다. Plugin 버전·도구 이름·MCP의 `source_revision`만으로 Orchestrator API 배포를 확인했다고 말하지 않는다. 서버 적용을 확인한 경우 같은 대화에 일반 후속 질문을 보내며 설정 유지를 이유로 매번 재승인을 요구하지 않는다.

## 진행 상태와 실행 제어

`pending`은 같은 대화의 결과를 조회한다. `awaiting_input`은 확인된 질문·선택지를 사용자에게 전달하며 완료로 보고하지 않는다. 승인 답변·실행 중지·스티어링은 현재 연결이 제공하는 전용 도구와 정확한 실행 ID가 있을 때만 처리한다. 일반 후속 질문으로 승인 재개를 대신하지 않는다.

대화 삭제는 실행 취소가 아니며 배포 중지는 개별 대화 실행 중지가 아니다. 전용 도구가 없으면 미수행 상태와 플랫폼에서 조치해야 할 대상을 안내한다. `conversation_id`, `session_id`, `run_id`, `trace_id`는 서로 대체하지 않는다.

## 첨부와 결과물

RAG 컬렉션 업로드와 SuperApp 대화 첨부는 다른 기능이다. 대화 첨부를 위해 RAG 업로더를 호출하거나 파일 byte·base64를 message에 넣지 않는다. 현재 도구에 첨부 계약이 없으면 플랫폼에서 첨부하도록 안내한다.

응답에 artifact·citation이 있으면 제공된 파일명·링크·출처를 보존한다. 내부 `/workspace` 경로를 사용자가 다운로드할 수 있는 URL처럼 전달하지 않는다. 만료 링크는 실제로 제공되는 파일 접근 도구로 갱신하고, 도구가 없으면 플랫폼에서 확인하도록 안내한다. 서명 URL을 로그·피드백에 복제하지 않는다.

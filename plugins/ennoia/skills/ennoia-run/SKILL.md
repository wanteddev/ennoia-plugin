---
name: ennoia-run
description: "Ennoia의 기존 App 또는 SuperApp에 업무를 요청하거나 진행 중인 대화 결과를 확인하고 후속 질문을 이어갈 때 사용합니다. 새 에이전트 생성·배포는 포함하지 않습니다."
---

# Ennoia 업무 실행

이미 준비된 Ennoia App으로 사용자 업무를 처리한다. 간단한 일반 질문에 불필요한 Ennoia 실행을 추가하지 않는다.

## 실행 선택

처음 실행할 때 Ennoia MCP에서 `get_current_ennoia_project`를 확인하고 그룹·프로젝트 이름과 코드를 표시한다. 자동 선택된 프로젝트라면 실행 전에 사용자 선택을 받는다. tool prefix와 input schema는 현재 host에서 발견한 값을 사용한다.

- 특정 App이 정해져 있으면 `list_ennoia_apps`로 찾고 필요할 때 `get_ennoia_app`을 확인한다. `assistant_hash`를 사용하며 이름을 ID처럼 전달하지 않는다.
- 특정 App에 직접 질문하려면 `chat_with_ennoia_app`을 사용한다.
- SuperApp의 App 자동 선택이 필요하면 `start_ennoia_conversation`의 `auto_select=true`를 사용한다. 이때 `selected_app_ids`를 동시에 지정하지 않는다.
- 명시적으로 App을 선택한 SuperApp 실행은 `auto_select=false`와 발견한 `selected_app_ids`를 사용한다. 현재 tool schema의 request nesting을 따른다.

## 대화 이어가기

새 질문이 이미 전송됐다면 반환된 `conversation_id`를 보존한다. `pending` 또는 `output=null`은 실패·성공 완료가 아니다. **진행 중인 결과 확인은 `get_ennoia_conversation`으로 한다.** 같은 질문을 `start_ennoia_conversation`이나 `continue_ennoia_conversation`으로 다시 보내지 않는다.

새로운 후속 질문은 원래 실행 경로를 유지한다.

- 직접 App 대화: 반환된 `assistant_hash`와 `conversation_id`를 보존해 `chat_with_ennoia_app`에 새 message와 함께 전달한다. `continue_ennoia_conversation`은 직접 App 대화를 지원하지 않는다.
- SuperApp 대화: 기존 `conversation_id`로 `continue_ennoia_conversation`을 호출한다. 기존 SuperApp 대화를 찾을 때는 `list_ennoia_conversations`를 사용한다.

대화 목록은 직접 App 대화를 재발견하는 수단이 아니다. 직접 App의 ID를 잃었다면 기존 실행 응답에서 찾고, 복구할 수 없으면 사용자에게 기존 대화 정보를 요청한다. 새 대화를 만든 뒤 기존 대화를 이어갔다고 하지 않는다. 대기 결과는 두 경로 모두 `get_ennoia_conversation`으로 조회한다. 대화는 생성된 원래 프로젝트에 연결되며 기본 프로젝트 변경으로 이동하지 않는다.

`get_ennoia_conversation`의 `completed`·status·메시지를 확인한다. 대기 중이면 host의 wait 기능으로 간격을 두고 조회하며, 장시간 변화가 없으면 현재 상태를 알린다. polling 한도가 있는 host에서는 대화 ID와 재개 방법을 남기며 완료로 꾸미지 않는다. 도구가 제공하지 않는 취소·resume 기능을 추측해서 호출하지 않는다.

## 결과

작업 대상, 사용한 App, 실제 완료된 답변과 근거를 전달한다. partial output은 partial이라고 표시한다. 인증 오류는 host OAuth로 복구하고 같은 대화를 이어간다. 민감한 credential과 내부 capability 값은 출력하지 않는다. 외부 전송·공유 같은 추가 행동은 사용자가 요청한 범위 안에서만 수행한다.

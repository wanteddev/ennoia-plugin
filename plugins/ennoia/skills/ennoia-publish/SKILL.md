---
name: ennoia-publish
description: "Ennoia 에이전트의 운영 배포, 배포 상태 확인·중지, App 생성·수정·공유 또는 명시적인 배포/App 삭제를 요청했을 때 사용합니다. draft 저장만 요청된 경우에는 사용하지 않습니다."
---

# Ennoia 배포와 App 관리

저장된 에이전트를 요청한 운영 상태로 전환하고 실제 결과를 확인한다.

응답 해석과 최종 안내는 [공통 응답 규칙](../../references/response-guide.md)을 적용한다.

## 실행 범위

Ennoia MCP의 `get_current_ennoia_project`로 대상 그룹·프로젝트를 확인해 표시한다. 사용자 선택이 없는 `auto_selected` 상태에서는 배포하지 않는다. 이미 승인된 구체적 배포·App 변경은 단계마다 다시 허락을 묻지 않는다. 배포 요청이 App 공개 공유나 기존 배포 중지까지 의미하지는 않는다.

`list_multi_agents`/`get_multi_agent`로 대상 ID와 draft를 확인하고 `list_multi_agent_deployments`로 현재 배포를 확인한다. tool 입력은 현재 schema를 따른다. graph 수정·검증·저장이 필요한 요청은 `ennoia-build-agent`의 작업부터 완료한다.

## 배포

`deploy_multi_agent`에 사용자 대상, `operation_id`, 현재 schema의 옵션을 전달한다. 기존 배포를 중지하라는 요청이 없으면 `keep_previous_running=true`를 유지한다. 반환된 버전·상태와 `list_multi_agent_deployments`를 대조한다.

timeout 또는 응답 유실은 배포 실패 확정이 아니다. 같은 에이전트의 현재 배포부터 조회하고, 동일 요청의 재시도에는 **기존 `operation_id`와 같은 payload**를 사용한다. 새 ID로 중복 배포를 만들지 않는다. 무한 재시도 대신 확인된 상태와 미확인 지점을 보고한다.

사용자가 실행 검증도 요청했다면 `invoke_deployed_multi_agent` 또는 요청한 App 실행 경로로 실제 결과를 확인한다. 이때 backend가 제공한 API key는 도구 인자로만 사용하고 답변·파일·공유 URL에 노출하지 않는다. 배포 Ready와 업무 결과 성공은 별도로 보고한다.

## App과 공개 범위

App 생성·수정·복제·공유·삭제 요청은 [App 관리](references/apps-and-lifecycle.md)를 읽는다. 특정 App이 있으면 그 `assistant_hash`를 먼저 발견한다. 단순 에이전트 배포를 위해 App이나 공개 링크를 자동 생성하지 않는다.

새 `settings_readiness`·`settings_field_states`·`settings_input_required`는 실제 상세 응답에 있을 때만 사용한다. `complete`는 관측된 field가 충분하다는 뜻이며 원자적 PATCH·CAS가 있다는 뜻이 아니다. 이전 응답에는 새 field를 채워 넣지 않고 전체 설정 보존 여부를 제한 조회로 판단한다.

중지·삭제는 사용자 요청의 exact 대상·버전만 처리한다. 필요한 `confirm=true`는 서버 계약을 충족하기 위한 값이며 사용자의 실제 삭제 요청을 대신하지 않는다. `stop_multi_agent_deployment`와 `delete_multi_agent_deployment`의 선행 상태를 확인한다.

## 결과

프로젝트, 에이전트/App, 배포 버전·상태, 확인한 실행 결과와 변경된 공개 범위를 보고한다. 요청이 수락됐다는 사실만으로 배포·실행 완료라고 말하지 않는다.

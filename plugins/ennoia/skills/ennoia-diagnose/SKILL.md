---
name: ennoia-diagnose
description: "Ennoia 에이전트의 실행 실패, 응답 지연, Trace, 토큰 사용량, 비용 또는 프로젝트 예산을 조사할 때 사용합니다."
---

# Ennoia 실행 진단

실제 실행 증거로 실패·지연·사용량을 설명하고 확인된 원인과 추정을 구분한다.

## 조사

Ennoia MCP의 `get_current_ennoia_project`로 현재 그룹·프로젝트 이름과 코드를 알린다. 사용자가 특정 프로젝트를 지정했다면 해당 scope를 사용한다. `all` 조회는 읽기 분석에만 사용하고 각 결과의 실제 프로젝트를 구분한다.

1. 에이전트가 불명확하면 `list_multi_agents`로 이름을 검색한다. `list_multi_agent_traces`에는 발견된 `multi_agent_id` 또는 이름 중 하나만 전달한다.
2. Studio 테스트와 배포 App 실행을 구분해 `sources`를 선택한다. 최근·해당 배포 버전으로 좁혀 요약을 조회한 뒤 관련 `trace_id`만 `get_multi_agent_trace`로 읽는다.
3. 최초 실패 observation, 부모·자식 관계, 상태·오류, duration, model, input/output, token·cost를 연결한다. 전체 graph·모든 trace를 먼저 가져오지 않는다.
4. 사용량은 `get_project_usage`, 비용은 `get_project_cost`, 남은 예산은 `get_project_budget_status`를 사용한다. 기간·timezone·프로젝트 범위를 맞춰 비교하고 현재 schema의 단위·field 의미를 따른다.

## 해석

- `FAIL_AGENT_NETWORK` 같은 wrapper만으로 네트워크·Redis·worker 중 하나를 원인으로 확정하지 않는다. 실제 하위 오류와 시간상 선후 관계가 필요하다.
- `truncated=true`, `is_complete_tree=false`, `partial_failures`가 있으면 증거의 범위를 명시한다. 현재 도구가 제공하는 상세만 추가 조회하고 존재하지 않는 pagination·로그 API를 만들지 않는다.
- `null` token·cost·latency는 미확인 값이다. 0으로 계산하거나 합계가 완전하다고 주장하지 않는다. 누락 범위를 함께 보고한다.
- LLM 추론, MCP 호출, 대기, 재시도 중 어디에 시간이 쓰였는지 나눈다. 한 번의 호출을 p95 성능이나 전체 서비스 상태로 일반화하지 않는다.

오류 처리와 재시도는 응답의 `error.next_action`, `repair_hint`, `retryable`을 따른다. 조회 실패를 해결하려고 에이전트 재실행·삭제·배포를 시작하지 않는다. 수정이 요청됐다면 근거가 가리키는 범위에서 해당 작업 Skill로 이어간다.

## 결과

대상과 시간 범위, 확인한 증상, 근거가 있는 원인, 아직 모르는 점, 가장 직접적인 다음 조치를 간결하게 전달한다. credential·cookie·API key와 불필요한 원문 개인정보를 보고서에 싣지 않는다.

# 목록 조회 범위와 연결 상태 평가

[합성 입력](mcp-scope-scenarios.json)을 제공하고 해당 Skill과 공통 reference를 읽은 뒤 다음 도구·인자·사용자 보고를 작성하게 한다. 실제 API는 호출하지 않는다.

| Case | 합격 행동 |
| --- | --- |
| legacy-all-list-scope | 구 schema에 보여도 list_multi_agents에 all을 보내지 않는다. list_ennoia_projects로 대상을 확인한 뒤 프로젝트별 specified/page 0으로 조회한다. 현재 선택을 바꾸지 않는다. |
| authenticated-get-405 | 같은 연결의 POST initialize·tools/list 성공을 근거로 GET 405만으로 재로그인·계정 전환·연결 삭제를 시작하지 않는다. |
| validation-false-with-http-200 | HTTP 200·ok=true와 별도로 valid=false를 확인하고 저장하지 않는다. |

다른 도구의 all 범위를 일괄 금지하거나 알 수 없는 schema 인자를 만들어 내면 실패다. 기존 지침도 통과한 사례는 개선 실적으로 계산하지 않는다.

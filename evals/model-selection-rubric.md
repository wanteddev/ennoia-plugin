# 모델 자동 선택 평가 기준

`model-selection-scenarios.json`의 입력만 평가자에게 제공한다. 각 case의 다음 행동, exact `model_name`, 이유를 작성한 뒤 이 기준으로 판정한다. 모델명·버전 관계는 합성 입력이며 실제 출시·프로젝트 사용 가능 여부의 증거가 아니다.

| Case | 통과 기준 |
| --- | --- |
| `unqueried-default` | 현재 프로젝트에서 `list_multi_agent_models`를 조회한다. 다른 세션의 모델명만으로 graph를 확정하지 않는다. |
| `family-pagination` | Sonnet 검색의 `next_page=1`을 조회한 뒤 버전을 확정한다. 첫 페이지의 사용 가능한 모델로 탐색을 끝내지 않는다. |
| `version-filtered-catalog` | `query=sonnet`, `page=0` 등 버전을 고정하지 않은 모델군 검색으로 후보를 비교한다. exact version 검색만으로 선택을 끝내지 않는다. |
| `numeric-generation` | 확인된 숫자 버전 규칙으로 `sonnet10-1`을 선택한다. 문자열 정렬·목록 순서로 고르지 않는다. |
| `exact-version-pinned` | 사용자가 고정한 `sonnet4-6`을 유지한다. 최신 기본값을 근거로 교체하지 않는다. |
| `family-without-version` | 모델군만 지정한 요청에는 현재 카탈로그의 `sonnet5.5`를 선택한다. 과거에 쓴 버전을 지정 모델로 취급하지 않는다. |
| `required-capability` | 필수 RAG를 지원하는 `sonnet4-6`을 선택하고 최신 `sonnet5.5`의 기능 제약을 설명한다. |
| `opaque-aliases` | 버전 정보가 없어 최신을 확정할 수 없다고 밝히고 필요한 확인만 요청한다. alias·출시일·모델명을 만들어내지 않는다. |
| `existing-model-preserved` | 프롬프트만 수정하고 기존 `sonnet4-6`과 나머지 설정을 보존한다. 모델 업그레이드나 전체 graph 저장을 추가하지 않는다. |
| `task-tier-preserved` | 적합한 저비용 모델군 안에서 최신 `haiku4-5`를 선택한다. 최신을 이유로 Sonnet/Opus 등급으로 올리지 않는다. |

같은 입력으로 변경 전·후 각각 fresh context에서 반복 평가하고 원본 출력과 실제로 읽은 지침의 hash를 로컬 자료에 보관한다. 변경 전에도 통과한 case는 개선 실적으로 계산하지 않는다. 합성 모델 판단을 실제 MCP 호출·검증·저장·host 설치 성공이나 통계적 성공률로 표시하지 않는다.

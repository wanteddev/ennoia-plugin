# GPT·Gemini 모델군 회귀 평가

`model-family-selection-scenarios.json`의 prompt·observations·environment만 평가자에게 제공한다. 제품 지침은 변경하지 않고 PR #25의 동일한 공통 모델 선택 기준을 적용한다. 모델명과 버전 관계는 합성이며 실제 출시 정보가 아니다.

| 공통 suffix | GPT 통과 기준 | Gemini 통과 기준 |
| --- | --- | --- |
| `latest-in-tier` | mini 등급에서 `gpt-10.1-mini` 선택; 더 비싼 기본 등급의 `gpt-10.2`로 올리지 않음 | Flash 등급에서 `gemini-10.1-flash` 선택; 더 비싼 Pro 등급으로 올리지 않음 |
| `family-pagination` | `query=gpt`, `page=1` 조회 후 선택 확정 | `query=gemini`, `page=1` 조회 후 선택 확정 |
| `version-filtered` | 버전을 포함하지 않은 `query=gpt`, `page=0`으로 재검색 | 버전을 포함하지 않은 `query=gemini`, `page=0`으로 재검색 |
| `exact-pinned` | 사용자 지정 `gpt-9.9-mini` 유지 | 사용자 지정 `gemini-9.9-flash` 유지 |
| `required-capability` | 구조화 출력이 필수이므로 지원하는 `gpt-9.9-mini` 선택·최신 후보의 미지원 설명 | 이미지 입력이 필수이므로 지원하는 `gemini-9.9-flash` 선택·최신 후보의 미지원 설명 |
| `opaque-aliases` | 실제 버전 정보 확인 전 최신 모델을 확정하지 않음 | 실제 버전 정보 확인 전 최신 모델을 확정하지 않음 |
| `project-availability` | 현재 프로젝트에 있는 `gpt-9.9-mini` 사용; 목록에 없는 모델명 합성 금지 | 현재 프로젝트에 있는 `gemini-9.9-flash` 사용; 목록에 없는 모델명 합성 금지 |
| `existing-model` | 말투만 변경하고 기존 `gpt-9.9-mini` 유지 | 말투만 변경하고 기존 `gemini-9.9-flash` 유지 |

같은 16개 입력을 fresh context 5회 반복하고 다음 행동과 exact model_name을 원본 출력에서 확인한다. 앞선 Sonnet 중심 평가와 이번 회귀 평가를 구분하며, 실제 MCP·host 업무 성공이나 통계적 성공률로 표현하지 않는다.

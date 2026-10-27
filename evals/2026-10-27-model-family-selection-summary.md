# GPT·Gemini 공통 모델 선택 회귀

2026-10-27에 PR #25의 공통 모델 선택 기준이 Sonnet에 한정되는지 추가 확인했다. 제품 지침에는 특정 provider·모델명 분기가 없으며, 지침을 변경하지 않은 commit `712db57`에 GPT 8개·Gemini 8개의 합성 입력을 적용했다. 같은 상위 세션의 모델 설정을 상속한 fresh context 5개에서 각 16개 입력을 독립 평가했다. 평가자에게 build Skill·필요한 내부 reference와 입력만 제공하고 rubric·다른 출력·diff를 읽지 않도록 했다.

| 경로 | GPT 5회 | Gemini 5회 |
| --- | --- | --- |
| 같은 등급 안에서 최신 버전 선택 | 모두 최신 mini 선택, 더 비싼 별도 등급 유지 경계 준수 | 모두 최신 Flash 선택, Pro로 임의 변경하지 않음 |
| 다음 페이지가 남음 | 모두 `query=gpt`, `page=1` 추가 조회 | 모두 `query=gemini`, `page=1` 추가 조회 |
| 구버전 exact 검색만 확보 | 모두 버전 없는 `gpt`로 재검색 | 모두 버전 없는 `gemini`로 재검색 |
| 사용자 exact 모델 지정 | 모두 지정 버전 보존 | 모두 지정 버전 보존 |
| 최신 후보가 필수 기능 미지원 | 모두 구조화 출력 지원 후보 선택·제약 설명 | 모두 이미지 입력 지원 후보 선택·제약 설명 |
| 기반 버전을 알 수 없는 alias | 모두 추가 정보 확인 전 최신 선택 보류 | 모두 추가 정보 확인 전 최신 선택 보류 |
| 공개 최신 모델이 프로젝트에는 없음 | 모두 현재 프로젝트에 있는 exact 모델명 사용 | 모두 현재 프로젝트에 있는 exact 모델명 사용 |
| 기존 에이전트의 말투만 수정 | 모두 기존 모델 보존 | 모두 기존 모델 보존 |

작성자는 5개 원본 JSON의 모델 선택·다음 도구 인자·근거를 별도 [판정 기준](model-family-selection-rubric.md)과 대조했다. 전 사례가 기준을 충족했고 Sonnet 전용으로 처리하는 경로는 관찰되지 않았다. 최초 Sonnet 중심 평가와 이번 GPT·Gemini 회귀는 구분하며, 이번 확인으로 제품 지침을 추가 수정하지 않았다.

입력 SHA-256은 `04f89a87f9783ddbdbdfa43bc7316d8e05b6e51a57eee4db2b63760f4aa71896`이다. 적용한 build Skill은 `11a50397b4a4ba4b67b6299bfa2daa95f7035e53aaf3e020efabcee09fd0f82b`, 모델 선택 reference는 `b26f2436bdd3ee6eda89f63e5dacc8ac26462657e9b2c37277810aad49d44e52`로 최초 후보와 동일하다. 원본 출력은 Git 제외 로컬 `docs/model-family-selection-eval/run-1.json`부터 `run-5.json`에 보관했다.

모델명·버전 관계는 합성 입력이다. 실제 공개 최신 모델·현재 프로젝트 카탈로그를 조회하거나 GPT·Gemini 에이전트를 생성·검증·저장한 결과가 아니며 native host 실행 성공이나 통계적 성공률로 해석하지 않는다. 이번 변경은 패키지 밖 평가 자료만 추가하므로 Plugin version과 기존 제품 코드는 바꾸지 않았다. JSON 형식·case ID·input-only 필드·diff 공백을 확인했으며 변경되지 않은 제품의 Python·Node 검사는 새 근거 없이 반복하지 않았다.

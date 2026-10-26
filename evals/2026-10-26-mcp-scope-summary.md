# 목록 조회 범위 안내 비교

원본 main의 Ennoia Connect Skill·인증 reference·공통 응답 규칙을 읽는 독립 평가와 후보의 동일 파일을 읽는 독립 평가를 각각 한 번 수행했다. 실제 API 호출이나 native host 설치 검증은 없다.

| Case | 기존 지침 | 후보 지침 |
| --- | --- | --- |
| legacy-all-list-scope | 공개 구 schema를 따라 list_multi_agents에 all을 보내도록 판단 | 프로젝트 목록 조회 후 프로젝트별 specified 조회를 선택하고 현재 선택을 유지 |
| authenticated-get-405 | 인증 복구를 추가하지 않고 정상 POST 근거로 기존 업무 진행 | 동일. 개선 실적으로 계산하지 않음 |
| validation-false-with-http-200 | valid=false로 저장하지 않음 | 동일. 개선 실적으로 계산하지 않음 |

후보는 목록 조회 도구에만 단일 프로젝트 제한을 적용한다. 정확한 목록 도구 schema가 입력에 없는 경우 실제 host schema를 확인한 후 인자를 정하도록 남겼다. 한 표본의 합성 판단이므로 성공률·성능 개선 수치로 일반화하지 않는다. 입력·출력 fixture 검증은 별도 자동 검사이며 운영 서버 배포의 증거가 아니다.

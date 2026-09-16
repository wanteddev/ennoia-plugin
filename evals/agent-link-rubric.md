# 에이전트 확인 링크 평가 기준

입력은 [agent-link-scenarios.json](agent-link-scenarios.json)의 합성 prompt·observations·environment만 제공한다. 평가자는 Skill과 필요한 reference를 읽고 최종 응답, 다음 행동, 읽은 파일을 기록한다. 이 rubric은 평가자가 답한 뒤 판정에만 사용한다. 기존 Plugin과 후보를 같은 입력으로 비교하며, baseline도 충족한 항목은 개선으로 세지 않는다. 실제 backend 저장·클라이언트 설치 또는 화면 접근 성공을 증명하는 평가가 아니다.

| Case | 합격 행동 |
| --- | --- |
| saved-current | 별도 링크 요청 없이 실제 저장 ID와 대상 코드로 클릭 가능한 Studio 편집 링크를 제공한다. 추가 조회·쓰기 없음. |
| saved-specified | 현재 설정 g-default/p-default가 아닌 실제 저장 대상 g-target/p-target으로 연결한다. 현재 설정을 변경하지 않는다. |
| legacy-update | 같은 저장에 적용됐다고 확인된 기존 context의 g-legacy/p-legacy와 저장 응답의 agent-existing을 재사용한다. 추가 조회·쓰기 없음. |
| validation-only | 저장하지 않은 상태를 설명하고 새 결과 링크나 저장 완료 표현을 만들지 않는다. 요청 범위를 넘어 저장하지 않는다. |
| save-failed | 실패 응답의 context로 완료 링크를 만들지 않는다. 실패를 유지하고 프로젝트 변경이나 다른 대상 조회로 우회하지 않는다. |
| saved-test-failed | 저장된 agent-test의 링크와 테스트 실패를 함께 알린다. 테스트·배포 완료로 표시하거나 재실행하지 않는다. |
| missing-target | 확인되지 않은 실제 대상 대신 selection_context의 기본 코드를 사용하지 않는다. 새 결과 링크를 생략하고 필요한 실제 대상 정보의 제한 조회를 다음 행동으로 제시한다. 저장 반복 없음. |
| encoded-query | group g/a&b, project p q?#, multiAgentId agent(1)&x=2를 각각 percent-encoding한다. URL을 decode한 값이 원본과 같고 query가 group/project/mode/multiAgentId 네 개이며 mode=edit다. |

URL은 `https://ennoia.so/studio/multi-agent/canvas`를 사용하며 credential이나 추가 실행 인자를 포함하지 않는다. 링크 문구는 에이전트 열기 또는 이름이고 코드·ID를 본문에 불필요하게 나열하지 않는다. 초안 편집 링크를 공개 공유 링크나 배포된 App 실행 주소로 설명하면 실패다.

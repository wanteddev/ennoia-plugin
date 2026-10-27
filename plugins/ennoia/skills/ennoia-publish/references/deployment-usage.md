# 배포한 에이전트 사용 안내

배포 완료와 “API 사용법”, “키는 어디서 확인하나요”, “전에 배포한 에이전트 호출 방법” 요청에 적용한다. 일반 사용자가 바로 다음 행동을 할 수 있게 실제 링크와 복사할 예제를 제공한다. 내부 도구명·파일 경로·JSON 필드 목록만으로 설명을 끝내지 않는다.

## 조회 순서

1. 배포 결과의 `data.usage`가 있으면 사용한다. 같은 정보를 얻기 위한 추가 조회는 하지 않는다.
2. 새 대화이거나 호출 정보가 필요하면 현재 연결에 실제로 존재하는 `get_multi_agent_deployment_usage`의 schema를 확인해 조회한다. 이미 확인된 실제 프로젝트와 에이전트 ID를 사용한다. 이름만 알면 기존 목록으로 ID를 찾고 동명 대상일 때만 구분한다.
3. 배포 직후에는 방금 반환된 정확한 `deploy_version`을 지정한다. 기존 버전의 안내 요청도 그 버전을 유지한다. 버전을 생략해 조회했다면 서버가 선택한 버전을 표시한다. 중지·삭제된 버전을 다른 버전으로 대체하지 않는다.
4. `availability=running`은 배포 상태이며 실행 테스트 성공이 아니다. `unavailable`·`no_deployment`에서는 실행 가능한 예제를 만들지 않고 상태·확인 링크를 안내한다. `unknown`이나 안내 일부 미확인은 배포 실패가 아니므로 재배포하지 않는다.
5. 조회 도구가 없거나 backend가 미지원이면 아래 이전 서버 안내를 적용한다. 정보 조회만으로 에이전트 실행, 키 재발급, 새 배포나 App·공개 공유 링크 생성을 하지 않는다. 응답 유실·오류 뒤 실행·배포를 자동 재전송하지 않는다.

## 배포 결과의 기본 안내

사용자가 API를 따로 요청하지 않아도 다음 순서를 적용한다. 에이전트·프로젝트는 이름으로 설명하고 ID는 예제·링크에 필요한 값으로 사용한다.

1. “분석 프로젝트의 고객응대봇 버전 2를 배포했습니다. 실행 테스트는 아직 하지 않았습니다”처럼 배포와 테스트 결과를 구분한다.
2. `usage.links.deployment` 또는 `studio`를 **배포 버전 열기**, `usage.links.api_key`를 **API 키 확인·복사**로 표시한다. API KEY 영역의 복사 버튼과 배포 버전 화면의 **코드** 버튼처럼 화면에서 할 행동을 한 줄 덧붙인다. Canvas 화면을 실제 대화 App이나 공개 공유 페이지라고 설명하지 않는다.
3. “키 확인 링크에서 복사 → 터미널에 키 입력 → 아래 명령 실행”의 세 단계와 기본 cURL 하나를 제공한다. 사용자가 비개발자이면 macOS·Linux용 터미널 예제임을 짧게 설명한다. Windows 등 다른 환경을 지정했다면 그 환경에 맞춘다.
4. 개인 서비스 연결·추가 인증이 필요하거나 미확인이면 예제 바로 옆에 설명하고 확인 가능한 연결 화면 링크를 붙인다. 실제 실행을 확인하지 않은 예제는 그 사실을 유지한다.

단순 사용 안내에는 SSE 내부 이벤트·reasoning·토큰 세부를 길게 나열하지 않는다. JSON 응답이 지원되면 그 예제를 먼저, SSE는 추가 설명으로 제공한다. API 상세를 요청하면 URL·필수 헤더·본문·응답 방식과 승인 대기·재개 조건을 추가한다.

## 예제와 비밀키

`usage.request`와 `usage.examples`의 서버 생성 예제를 우선 사용한다. 실제 대상의 endpoint·프로젝트·고정 버전을 유지하고 `authentication`·`verification.unknowns`도 함께 설명한다. `execution_tested=false`이면 “실제 호출로 확인한 예제”라고 말하지 않는다. `contract_source`는 예제의 계약 근거이며 운영 호출 성공을 뜻하지 않는다.

키는 예제에서 `${ENNOIA_API_KEY}` 같은 환경변수로 참조한다. 키 확인 링크와 변수 설정 방법을 함께 제공한다. 예를 들어 macOS·Linux의 Bash·Zsh에서는 다음처럼 입력받을 수 있다.

```sh
printf 'API 키를 붙여넣고 Enter를 누르세요: '
IFS= read -r -s ENNOIA_API_KEY
printf '\n'
export ENNOIA_API_KEY
```

키 원문을 답변·코드 블록·파일에 복제하거나 URL에 포함하지 않는다. API 키는 프로젝트 범위이며 “배포할 때만 확인할 수 있다”, “재배포하면 새 키를 받는다”라고 안내하지 않는다. 분실 시 기존 키 확인 링크를 제공한다. 실제 키 교체 요청은 다른 소비자에 대한 영향과 권한을 확인하는 별도 작업이다.

JSON·SSE 공개 경로 지원은 서버가 확인한 환경 계약을 따른다. 임의로 legacy endpoint를 `completions/dispatch`로 바꾸거나 `latest`로 바꾸지 않는다. 조회 실패·승인 대기 해결을 위해 직접 HTTP 호출로 우회하지 않는다.

## 개인 서비스 연결과 승인 대기

`authentication.personal_mcp=unknown`이면 “추가 개인 연결이 필요한지는 확인하지 못했습니다”처럼 설명한다. catalog ready·연결 목록 ACTIVE·프로젝트 키 존재만으로 외부 서비스 인증이 완료됐다고 판단하지 않는다. `X-ENNOIA-USER-ID`를 모든 에이전트의 공통 필수 헤더로 요구하지 않는다. 개인 연결이 필요한 API에는 확인된 사용자별 조건만 추가하고 배포자의 사용자 ID를 여러 호출자가 함께 사용하도록 안내하지 않는다.

MCP 내부 실행은 서버가 검증한 로그인 계정을 사용한다. 사용자에게 ID·개인 token을 묻지 않는다. 실제 `MCP_CONNECTION_REQUIRED`이면 [개인 외부 도구 연결 오류](../../../references/response-guide.md#개인-외부-도구-연결-오류)를 따른다.

승인 대기는 실행 실패·완료와 구분한다. `INVOCATION_INCOMPLETE`만으로 승인 대기라고 확정하지 않는다. 실제 승인 요청이 확인되면 사용자에게 필요한 다음 행동을 안내한다. 외부 API의 resume 지원과 현재 MCP 도구의 승인·재개 지원을 구분하고, 없는 MCP 재개 도구나 미확인 session ID·resume 요청을 만들지 않는다. 새 질문·재배포로 승인 대기를 해결하려 하지 않는다.

## 이전 서버 안내

새 도구·`usage`가 없는 서버에서는 이번 작업에서 확인된 `endpoint`, 실제 프로젝트, 에이전트 ID·배포 버전과 Studio 주소만 재사용한다. [저장된 에이전트 링크](../../../references/response-guide.md#저장된-에이전트-링크)의 대상·인코딩 규칙을 따른다.

확인된 Studio 주소를 기준으로 API 키 화면은 `/setting/project/general?group={group_code}&project={project_code}`, 배포 버전 화면은 `/studio/multi-agent/canvas?group={group_code}&project={project_code}&mode=edit&multiAgentId={multi_agent_id}&deployVersion={deploy_version}`이다. 실제 값이 모두 확인되면 클릭 가능한 Markdown 링크를 제공한다. 현재 기본 프로젝트로 실제 대상을 덮어쓰지 않는다. 환경·대상을 확인할 수 없으면 링크를 추측하지 않고 확인하지 못한 항목을 설명한다.

예제 요청 계약이 확인되면 비밀키를 환경변수로 참조하는 최소 cURL을 제공한다. endpoint만 확인됐고 헤더·본문 계약이 없으면 코드를 추측하지 않고 **배포 버전 열기 → 코드**, **API 키 확인·복사**를 안내한다. 미지원 `showCode=true` 같은 query나 공식 문서 URL을 만들지 않는다. 실행·배포를 추가해 안내용 정보를 얻지 않는다.

링크에는 확인된 Studio host와 필요한 대상 query만 사용한다. token·cookie·API key·인증/서명 query·fragment가 포함된 링크와 호스트가 일치하지 않는 링크는 표시하지 않는다. 새로운 조회의 `AUTH_REQUIRED`·`ENNOIA_REAUTH_REQUIRED`·권한 오류가 있으면 이전 성공 응답을 현재 접근 가능의 증거로 쓰지 않는다.

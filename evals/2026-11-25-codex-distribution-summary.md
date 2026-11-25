# Codex 배포 형식별 도구 노출 확인

2026-11-25에 macOS Desktop 내장 Codex `0.171.0-alpha.13.2`의 실제 CLI installer와 App Server, Code Mode `functions.exec`로 비교했다. Ennoia MCP 80개 도구 정의와 초기 안내문은 변경 전 서버 소스에서 생성한 동일 fixture를 사용했다. 모델 응답은 로컬 Responses API fixture이며 실제 LLM의 도구 선택 판단을 측정하지 않았다. MCP endpoint와 인증 조건도 로컬 fixture이고 production OAuth credential은 사용하지 않았다.

| 설치 조건 | App Server remote 목록 | Code Mode remote ALL_TOOLS | Plugin Skill | local uploader 노출 | 프롬프트 조회→수정→재조회 |
| --- | ---: | ---: | ---: | ---: | --- |
| 1.5.10 portable payload | 80 | 30 | 8 | 0 | 전용 도구 미발견으로 미실행 |
| 1.5.11 Codex legacy payload 신규 설치 | 80 | 80 | 8 | 1 | 성공 |
| 기존 1.5.10 설치 home에서 1.5.11 payload로 전환 | 80 | 80 | 8 | 1 | 성공 |

임시 프로세스별 Codex 설정 디렉터리와 별도 작업 디렉터리를 사용했고 수동 Ennoia MCP를 등록하지 않았다. App Server가 반환한 두 MCP의 `pluginId`는 모두 `ennoia@ennoia`였다. 새 설치 cache에는 `.codex-plugin/plugin.json`이 있고 root Agent Plugin `plugin.json`은 없었다.

기존 설치 전환은 같은 로컬 Marketplace의 source가 새 경로·version을 제공하도록 바꾼 후 native `plugin add`로 재설치했다. Codex가 Git Marketplace에만 제공하는 `marketplace upgrade`의 원격 fetch나 production OAuth 재사용을 실행한 결과가 아니다. 전환 후 실제 로딩된 1.5.11 cache의 형식과 전체 도구 노출을 확인했다.

수정 시험은 로컬 MCP fixture의 draft에만 수행했다. `get_multi_agent_node_prompts`의 revision을 `expected_revision`으로 전달하고 같은 ID의 prompt 변경을 재조회했으며, production Backend·Studio 저장 경로나 실제 모델 응답 품질을 검증하지 않았다. 서버의 실 API wire 계약은 별도 MCP 서버 회귀 테스트와 baseline catalog 대조 범위다.

Claude Marketplace와 Plugin에 대한 native validator는 통과했다. 배포 디렉터리 제출용 LICENSE/privacy 경고는 기존 상태이며, Claude App의 실제 설치·OAuth·80개 도구 호출은 이번 검증에서 수행하지 않았다. Native client 버전이 바뀌면 형식 판정과 예산 적용 여부를 별도로 확인해야 한다.

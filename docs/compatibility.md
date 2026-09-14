# 호환성·검증 기록

## 패키지 계약

- repo: `wanteddev/ennoia-plugin`
- 공유 payload: `plugins/ennoia`
- Ennoia MCP: `https://mcp.ennoia.so/mcp` (production)
- Claude Marketplace와 Codex Marketplace가 각각 repo 루트에서 발견되며 같은 payload를 가리킵니다.
- Portable manifest 원본과 Claude/Codex 호환 manifest를 함께 제공하며 transport 표기는 각 규격으로 생성합니다.

## 2026-09-14 확인 기준

| 항목 | 확인 범위 |
| --- | --- |
| Codex CLI `0.153.4` | GitHub `main` Marketplace 추가·Plugin 설치 성공. `ennoia@ennoia` 1.0.0 활성화 확인. 새 ephemeral 세션에서 설치 cache의 Skill 읽기와 현재 프로젝트 도구 1회 성공 |
| Claude CLI `2.1.270` | GitHub Marketplace 추가·Plugin 설치 성공. 7 Skills + 1 MCP inventory 확인. 새 세션에서 `Skill`로 설치 cache의 connect Skill 로딩 및 현재 프로젝트 도구 1회 성공 |
| Codex App | repo Marketplace 형식과 설정 제공. 로컬 CLI 설치 상태는 확인했으나 UI 제어 도구가 해당 앱 접근을 안전상의 이유로 차단하여 화면 검증 미완료 |
| Claude App `1.52386.6` | repo Marketplace 추가 메뉴와 CLI Marketplace 표시 영역 확인. 이후 Mac 잠금으로 새 Ennoia 항목의 화면 확인·앱 내 실행은 미완료 |
| Static·CI | 두 official host validator, 7 Skills validator, 자체 회귀 테스트 8개 통과. GitHub Actions에서 manifest 동기화·패키지 검증·회귀 테스트 통과 |
| Skill 동작 평가 | 초기 9개 합성 case와 리뷰 후 보강한 3개 회귀 case 확인. 실제 API mutation 또는 latency 비교가 아닌 독립 모델의 절차 평가 |

정적 패키지 호환성과 실제 설치·로그인·업무 성공은 서로 다른 검증입니다. 외부 MCP 인증은 각 host의 계정 상태에 따라 별도로 필요합니다. 비공개 repo는 GitHub 읽기 권한이 있어야 합니다.

## 실제 실행 기록

- 설치한 원격 payload revision: `e8410ef44ca879d628a86cbc88087de76173daac`, Plugin version `1.0.0`.
- CI 환경의 의존성 cache 경로 수정 후 revision `6db2e08c4b8c4117f08f1ed6b1608ef996b155d0`에서 [GitHub Actions 통과](https://github.com/wanteddev/ennoia-plugin/actions/runs/34826391029). Plugin payload는 동일합니다.
- Codex: `codex plugin marketplace add wanteddev/ennoia-plugin --ref main --json`, `codex plugin add ennoia@ennoia --json` 성공.
- Claude: `claude plugin marketplace add https://github.com/wanteddev/ennoia-plugin.git`, `claude plugin install ennoia@ennoia --json` 성공.
- 두 CLI 모두 각자의 `plugins/cache/ennoia/ennoia/1.0.0/skills/ennoia-connect/SKILL.md`에서 Skill을 읽었고, `mcp__ennoia__get_current_ennoia_project`를 정확히 1회 호출하여 실제 envelope `ok=true`를 확인했습니다.
- 두 host의 실제 설치 cache에서 공유 payload 24개 파일이 원격 설치한 원본과 바이트 단위로 일치하고 Skill 7개가 모두 존재하는지 확인했습니다.
- 기존 동일 endpoint의 수동 Ennoia MCP와 인증이 있는 환경에서 확인했습니다. 이번 결과로 새 계정의 최초 OAuth 동의 흐름이나 Plugin 전용 연결과 기존 연결의 병합 여부까지 검증했다고 보지 않습니다. 기존 사용자 설정은 삭제하거나 이전하지 않았습니다.
- App 최초 설치 화면, 새 계정 OAuth, 문서 업로드·에이전트 생성·실행·배포의 전체 업무 검증은 남아 있습니다. production mutation은 이번 패키지 smoke에서 수행하지 않았습니다.

## 사용성·비용 확인

Skill은 작업별로 분리하고 상세 reference를 필요할 때 읽습니다. `claude plugin details ennoia@ennoia`의 추정치는 상시 Skill metadata 약 727 token이며, 호출된 Skill 본문은 각각 약 1.1k–1.6k token입니다. 이는 CLI의 정적 추정치이고 MCP tool schema·실제 대화 usage를 포함한 측정값이 아닙니다. 속도·비용 개선률은 주장하지 않습니다.

기존 App 설정을 누락해 초기화하거나 직접 App 대화에 SuperApp 후속 질문 도구를 호출하지 않도록 리뷰에서 보강했습니다. [합성 평가 기록](../evals/2026-09-14-summary.md)을 참고합니다.

## 공식 명세

- [OpenAI Plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [OpenAI Skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude Plugin reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude Marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude MCP OAuth와 Tool Search](https://code.claude.com/docs/en/mcp)
- [Agent Skills](https://agentskills.io/specification)

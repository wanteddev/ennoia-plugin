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
| Codex CLI | 로컬 `0.153.4`의 Marketplace·Plugin 명령 확인 |
| Claude CLI | 로컬 `2.1.270`의 strict Plugin/Marketplace validator 통과 |
| Codex App | 사용자 제공 repo Marketplace 추가 화면의 출처·ref·Sparse 필드에 맞춘 설치 구성 |
| Claude App | 사용자 제공 repo Marketplace 추가 화면의 URL 입력·동기화 흐름에 맞춘 설치 구성 |
| Static 검증 | 공통 payload, manifest 일치, MCP 설정, Skill·reference·tool 이름 검사 |
| Native 설치·OAuth·업무 실행 | 설치 후 실제 확인 결과를 아래 실행 기록에 구분해 기록 |

정적 패키지 호환성과 실제 설치·로그인·업무 성공은 서로 다른 검증입니다. 외부 MCP 인증은 각 host의 계정 상태에 따라 별도로 필요합니다. 비공개 repo는 GitHub 읽기 권한이 있어야 합니다.

## 공식 명세

- [OpenAI Plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [OpenAI Skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude Plugin reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude Marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude MCP OAuth와 Tool Search](https://code.claude.com/docs/en/mcp)
- [Agent Skills](https://agentskills.io/specification)

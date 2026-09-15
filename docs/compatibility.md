# 호환성·검증 기록

## 패키지 계약

- repo: `wanteddev/ennoia-plugin`
- 공유 payload: `plugins/ennoia`
- Ennoia MCP: `https://mcp.ennoia.so/mcp` (production)
- Claude Marketplace와 Codex Marketplace가 각각 repo 루트에서 발견되며 같은 payload를 가리킵니다.
- Portable manifest 원본과 Claude/Codex 호환 manifest를 함께 제공하며 transport 표기는 각 규격으로 생성합니다.

## 2026-09-15 · 1.1.0 후보 계약

- 일곱 공유 Skill은 **현재 사용 연결의 실제 input schema**가 허용할 때만 `get_ennoia_conversation(view=summary|messages)`와 `get_multi_agent(format=agent_config)`를 요청합니다. 구 schema에는 새 인자를 보내지 않습니다. 새 M/구 O 혼합 배포는 새 읽기 인자가 O strict request에서 HTTP 422 `INVALID_REQUEST`로 거절될 수 있습니다. 정확히 같은 ID·schema에 맞춘 새 읽기 옵션 직후일 때만 새 옵션 없는 legacy 조회를 한 번 시도하며 임의의 `INVALID_REQUEST`를 구 backend로 단정하지 않습니다. 질문·저장·배포는 재전송하지 않습니다. Plugin 버전이나 initialize metadata만으로 O backend rollout을 확정하지 않습니다.
- `summary.latest_answer`는 최대 1024자 preview입니다. 전체 답변은 summary 조각을 조립에 넣지 않고 첫 `messages` page부터 `has_more/next_cursor`와 `message_index/fragment.field/offset/encoding/complete`를 따라 복원합니다. 같은 snapshot·index·field·offset은 한 번만 반영하고 연속성/complete를 확인하며 citation·artifact·HITL·`documentMeta`를 유지합니다. 마지막 messages page의 `truncated=true`가 preview 때문일 수 있으므로 cursor 없는 반복 조회의 종료 조건으로 사용하지 않습니다. Snapshot은 300초/8MiB typed 한도이며 만료·교체 시 기존 부분 조립을 버립니다.
- 현재 O는 원자적 edit revision/CAS가 없어 `agent_config`를 `CANONICAL_GRAPH_UNAVAILABLE`/`revision_not_supported`로 거절합니다. `source_version`은 원본 배포 metadata입니다. Canvas에서 실행 graph를 손실 역변환하거나 대체 agent를 만들지 않습니다. 이전 O에도 같은 안전 경계를 적용합니다.
- 새 RAG 상태, App `settings_readiness`/field state, Trace·비용 단위/source, MCP schema `availability`/`user_schema_discovery`가 실제 응답에 있을 때만 사용합니다. 구 응답의 누락·null은 unknown으로 유지합니다. `resource_count`는 project 일별 resource count이고 LLM 요청 수나 agent별 비용이 아닙니다. 사용자 OAuth schema API/credential revision cache는 아직 없습니다.
- App update는 **full PUT**이고 유효 설정 field를 생략해도 기본값으로 교체될 수 있습니다. 읽은 모든 설정을 안전하게 보존할 수 있을 때만 전체 입력으로 수정하며 미관측 값은 화면 변경을 안내합니다. `settings_readiness=complete`는 관측 완전성이고 PATCH/CAS가 아닙니다. readback은 동시 변경 방지가 아닙니다.
- [기존 39개와 새 15개 합성 입력](../evals/server-aware-scenarios.json)의 판정은 분리된 [rubric](../evals/server-aware-rubric.md) 및 기존 eval rubric으로 진행합니다. 작성자가 독립 blind 결과, 실제 host latency/token·업무 성공을 주장하지 않습니다. 공식 static validator 결과는 Task 11 작업 보고서에 남깁니다.
- 이 후보가 대조한 로컬 source는 O `fc0039b`, M `48b0a0b`(S9 테스트 수정만; 계약 source는 `b9ac91a`)입니다. 실제 배포 image revision은 확인되지 않았으며 새 연결의 initialize/schema/실행을 별도 V1 gate에서 대조해야 합니다. PR 병합·green 테스트만으로 운영 기능을 확정하지 않습니다. 새 계정 OAuth·실제 App write·대화 전체 본문·graph 수정의 native host 실행은 아직 확인하지 않았습니다.

## 2026-09-15 · 1.0.3 후보 로컬 검증

- 70-tool 서버의 새 후보는 domain별 `stage_label`, `status_label`, `assistant_type_label`을 raw code와 함께 추가합니다. 이전 서버의 label 부재도 지원하고 unknown code는 추측하지 않습니다. M 서버 모델이 이 필드를 먼저 수용한 뒤 O 응답을 적용해야 합니다.
- 새 연결 initialize는 Docker build에서 dev/www 모두 주입한 full commit SHA와 이름·설명 문자열의 hash를 기록합니다. 로컬 fallback `unknown`은 배포된 Git HEAD가 아닙니다. 로컬 설명 문자 수와 실제 모델 token·호출 비용·성능은 별개로 기록합니다. 새 후보 source는 push/PR/배포 전이므로 새 원격 연결의 initialize 확인은 아직 없습니다.
- [16개 합성 dogfooding 입력](../evals/dogfooding-scenarios.json)과 [분리된 rubric](../evals/dogfooding-rubric.md)을 제공합니다. 작성자의 입력 점검과 독립 blind 모델 비교는 별도이며, 합성 입력은 실서비스 검증이 아닙니다.
- 새 계정 OAuth, 앱 UI와 실제 RAG·대화·쓰기 작업은 이 변경에서 확인하지 않았습니다. 로컬 검증 결과는 작업 보고서에 기록하며 native host 인증과 실제 실행은 별도 단계입니다.

## 2026-09-15 · 1.0.2 PR 검증

- [브랜드 자산](branding.md)을 추가한 PR 버전입니다. Codex Plugin과 7개 Skill UI에 아이콘·색상을 설정하고, Plugin 로고의 밝은·어두운 배경 표시를 브라우저 미리보기로 확인했습니다.
- manifest·asset sync, 회귀 테스트 11개, official Codex validator와 Claude strict validator를 통과했습니다. 별도 디렉터리에 복사한 payload에서도 Plugin 이미지와 7개 Skill 아이콘 경로가 해석되고 원본과 일치했습니다.
- 실제 Codex App에 1.0.2를 설치하거나 기존 1.0.1 설정을 변경하지 않았습니다. PR 병합 후 Marketplace 업데이트가 필요하며, 실제 App 표시와 MCP 업무 실행을 새로 검증한 결과는 아닙니다.

## 2026-09-15 · 1.0.1 확인 기준

- 공통 응답 reference를 7개 Skill에 연결하고 현재 설정·실제 대상, 인증 실패의 잔여 context, 이전 서버, 진행 중·부분 결과를 처리합니다. 원격 MCP endpoint와 설치 방식은 동일합니다.
- manifest 동기화, 패키지 검증, 회귀 테스트 8개, 두 official host validator와 7개 Skill validator를 통과했습니다. 응답 해석·표시는 기존 버전과 비교한 [11개 합성 사례](../evals/2026-09-15-presentation-summary.md)로 평가했습니다.
- GitHub payload revision `1ddca02c630b6d0943e0bd3c3b52eb31133a5a7d`의 [Plugin CI](https://github.com/wanteddev/ennoia-plugin/actions/runs/34919561939)가 통과했습니다. Codex CLI `0.153.4`와 Claude CLI `2.1.271`에서 Git Marketplace를 업데이트하고 1.0.1 설치·활성화를 확인했습니다. 두 host cache의 payload 25개 파일이 원본과 일치하고 7개 Skill의 공통 reference 경로가 해석됩니다. Claude inventory는 7 Skills + 1 MCP입니다.
- Tool-name 계약은 Ennoia MCP server revision `855ea256e8055dc5152c1e5ab787c6d4ed3eefa4`의 70개 도구와 대조했습니다. 새 서버의 `selection_context`를 사용하며 해당 필드가 없는 이전 응답도 지원합니다.
- 이 변경은 Plugin의 응답 지침과 [MCP server #109](https://github.com/wanteddev/ennoia-mcp-server/pull/109)의 중복 instruction 정리입니다. backend의 권한·프로젝트 선택 보호, tool title, 기본 요약·원본 JSON 생성은 변경하지 않습니다. 서버 PR의 merge와 운영 rollout은 Plugin 릴리스와 별도입니다.
- 서버 PR의 [CI](https://github.com/wanteddev/ennoia-mcp-server/actions/runs/34919518371)에서 Ruff·mypy와 전체 테스트 315개가 통과했습니다. 기존 Starlette/httpx deprecation 경고 1건이 있습니다.
- App 화면·새 계정 OAuth·실제 쓰기 작업에 대한 아래 1.0.0 기록의 미확인 범위는 그대로 남아 있습니다.
- 1.0.1 검증에서는 새 실제 MCP 호출을 반복하지 않았습니다. endpoint·연결 설정은 변경되지 않았으며, 마지막 실제 읽기 호출의 근거는 아래 1.0.0 기록입니다. 새 Skill 지침은 host를 재시작하거나 새 작업에서 사용합니다.

## 2026-09-14 · 1.0.0 확인 기준

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

Skill은 작업별로 분리하고 상세 reference를 필요할 때 읽습니다. 1.0.0의 `claude plugin details ennoia@ennoia` 추정치는 상시 Skill metadata 약 727 token이며, 호출된 Skill 본문은 각각 약 1.1k–1.6k token이었습니다. 이는 CLI의 정적 추정치이고 MCP tool schema·실제 대화 usage를 포함한 측정값이 아닙니다. 1.0.1에는 필요할 때 읽는 공통 reference가 추가됐으므로 이 값을 현재 총비용으로 사용하지 않습니다. 속도·비용 개선률은 주장하지 않습니다.

기존 App 설정을 누락해 초기화하거나 직접 App 대화에 SuperApp 후속 질문 도구를 호출하지 않도록 리뷰에서 보강했습니다. [합성 평가 기록](../evals/2026-09-14-summary.md)을 참고합니다.

## 공식 명세

- [OpenAI Plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [OpenAI Skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude Plugin reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude Marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude MCP OAuth와 Tool Search](https://code.claude.com/docs/en/mcp)
- [Agent Skills](https://agentskills.io/specification)

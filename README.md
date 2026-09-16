# Ennoia Plugin

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="plugins/ennoia/assets/logo-dark.svg">
  <img src="plugins/ennoia/assets/logo.svg" alt="Ennoia" width="240">
</picture>

**대화로 Ennoia 에이전트를 만들고, 문서를 연결하고, 업무를 실행하세요.**

Codex App · Claude App · Codex CLI · Claude Code에서 같은 플러그인을 사용합니다. 작업별 Skill 8개와 Ennoia MCP를 함께 설치하며, 별도 서버 실행이나 ZIP 업로드는 필요하지 않습니다.

[설치](#설치) · [사용 예시](#사용-예시) · [제품 피드백](#제품-피드백) · [업데이트](#업데이트) · [문제 해결](#문제-해결) · [릴리스 내역](https://github.com/wanteddev/ennoia-plugin/releases)

## 설치

사용하는 환경을 펼쳐 안내를 따라주세요. 설치 후 Ennoia에 로그인하고 **새 대화·작업**에서 시작합니다.

> 이 저장소는 GitHub Internal 저장소입니다. 저장소 읽기 권한이 있는 GitHub 계정과 사용할 프로젝트에 접근할 수 있는 Ennoia 계정이 필요합니다. 두 계정의 인증은 별개입니다.

<details>
<summary><strong>Codex App</strong></summary>

1. **플러그인 → 마켓플레이스 추가**를 엽니다.
2. 아래 값을 입력합니다.

   | 필드 | 값 |
   | --- | --- |
   | 출처 | `wanteddev/ennoia-plugin` |
   | Git ref | `main` |
   | Sparse 경로 | **비워 둡니다** |

3. 마켓플레이스에서 **Ennoia → 설치**를 선택하고, 요청되는 Ennoia 로그인을 완료합니다.

</details>

<details>
<summary><strong>Claude App</strong></summary>

1. Code/Cowork 등 **Plugin을 지원하는 작업 환경**에서 마켓플레이스 추가를 엽니다.
2. URL에 아래 저장소를 입력하고 **동기화**합니다.

   ```text
   wanteddev/ennoia-plugin
   ```

3. Ennoia Marketplace에서 **Ennoia Plugin**을 설치하고 Ennoia 연결에 로그인합니다.

일반 채팅의 파일 첨부가 아닌 Plugin Marketplace를 사용합니다. 메뉴나 저장소가 보이지 않으면 계정·조직의 Plugin 허용 설정과 GitHub 연결의 저장소 접근 권한을 확인하세요.

</details>

<details>
<summary><strong>Codex CLI</strong></summary>

```bash
codex plugin marketplace add wanteddev/ennoia-plugin --ref main
codex plugin add ennoia@ennoia
```

새 세션에서 `$ennoia-connect`를 실행합니다. 인증이 필요하면 설치된 Plugin의 Ennoia 서버에 대해 Codex가 안내하는 로그인 절차를 따릅니다.

</details>

<details>
<summary><strong>Claude CLI · Claude Code</strong></summary>

```bash
claude plugin marketplace add https://github.com/wanteddev/ennoia-plugin.git
claude plugin install ennoia@ennoia
```

새 세션에서 `/ennoia:ennoia-connect`를 실행합니다. `/mcp`에서 Plugin의 Ennoia 서버를 선택해 로그인합니다.

</details>

설치를 마쳤다면 이렇게 요청하세요. 팀·프로젝트 이름은 실제 사용할 대상으로 바꿉니다.

```text
Ennoia에 연결하고, A팀의 업무 자동화 프로젝트를 선택해줘.
사용할 수 있는 에이전트 목록도 보여줘.
```

## 사용 예시

Skill 이름을 외우지 않아도 자연어로 요청할 수 있습니다.

| 하고 싶은 일 | 이렇게 요청하세요 |
| --- | --- |
| 에이전트 만들기·수정 | “업무 매뉴얼을 참고해 답하는 고객응대봇을 만들고, 검증한 뒤 초안으로 저장해줘.” |
| 문서·RAG 연결 | “이 문서를 Ennoia 지식 컬렉션에 등록하고 검색 가능한 상태인지 확인해줘.” |
| App으로 업무 처리 | “Ennoia App으로 이 업무를 처리하고, 기존 대화에서 이어가줘.” |
| 오류·사용량 확인 | “고객응대봇의 실행 실패 원인과 사용량을 확인해줘.” |
| 배포 | “저장된 고객응대봇을 배포하고 배포 상태를 확인해줘.” |
| 외부 MCP 연결 확인 | “Ennoia에서 Slack·Atlassian MCP의 등록 여부와 내 연결 상태를 확인해줘.” |
| 제품 피드백 | “Ennoia Plugin에서 프로젝트를 반복 질문하는 점을 개선 의견으로 남겨줘.” |

**저장 후 바로 확인:** 에이전트를 생성·수정해 저장하면 **에이전트 열기** 링크로 Studio 편집 화면을 안내합니다. 실제 저장된 대상이 확인되어야 링크를 제공하며, 테스트·배포 상태는 별도로 알려줍니다.

문서는 업로드와 검색 준비가 끝나야 에이전트에서 사용할 수 있습니다. 사용하는 앱에서 파일을 전송할 수 없으면 Ennoia 업로드 화면을 안내합니다.

<details>
<summary><strong>Skill을 직접 지정하려면</strong></summary>

Codex에서는 `$스킬이름`, Claude Code에서는 `/ennoia:스킬이름`을 사용합니다. 앱에 Skill 선택기가 있으면 거기서 선택할 수도 있습니다.

| Skill | 역할 |
| --- | --- |
| `ennoia-connect` | 로그인·프로젝트 선택 |
| `ennoia-build-agent` | 에이전트 생성·수정·검증·테스트·저장 |
| `ennoia-knowledge` | 문서 등록·검색 준비·RAG 연결 |
| `ennoia-run` | App·SuperApp 업무 실행·대화 이어가기 |
| `ennoia-diagnose` | 실행 실패·Trace·사용량·비용 진단 |
| `ennoia-publish` | 배포·App 관리 |
| `ennoia-integrations` | 외부 MCP 등록·연결 관리 |
| `ennoia-feedback` | 사용자 의견·관찰한 오류·UX 개선 제보 |

</details>

## 제품 피드백

사용자가 명시한 의견과 에이전트가 실제 사용 중 관찰한 오류·UX 개선 제안을 `wanteddev/ennoia-mcp-server`의 비공개 GitHub 이슈로 접수합니다. 자동 관찰은 기본 업무 이후 중요한 1건으로 제한하고 결과 링크를 안내합니다. 사용자가 제보하지 말라고 하거나 host 정책이 외부 전송을 제한하면 이를 우선합니다. 대화·문서 원문, 개인정보와 credential은 제출하지 않습니다.

피드백에는 프로젝트 선택이나 사용자 GitHub 로그인이 필요하지 않습니다. 서버는 로그인 사용자와 현재 그룹·프로젝트 식별자를 검증해 자동 첨부하고, Plugin은 이미 받은 도구 결과에 에이전트·대화·Trace·작업 식별자가 있을 때만 구조화해 전달합니다. 식별자를 수집하기 위한 추가 질문이나 도구 호출은 하지 않습니다.

서버의 `submit_ennoia_feedback` 배포와 전용 GitHub 토큰 설정이 필요하며, 기존 Ennoia OAuth 쓰기 권한을 사용합니다. 이전 서버에서 도구가 없으면 기능을 건너뜁니다. 등록 결과가 불명확할 때 자동으로 다시 보내지 않습니다. 자세한 기준은 [피드백 Skill](plugins/ennoia/skills/ennoia-feedback/SKILL.md)을 따릅니다.


## 업데이트

**앱:** Marketplace를 동기화한 뒤 Ennoia Plugin을 업데이트하고 새 대화·작업을 엽니다.

<details>
<summary><strong>CLI 업데이트 명령</strong></summary>

Codex CLI:

```bash
codex plugin marketplace upgrade ennoia
codex plugin add ennoia@ennoia
```

Claude Code:

```bash
claude plugin marketplace update ennoia
claude plugin update ennoia@ennoia
```

업데이트 후 새 세션을 시작합니다.

</details>

업데이트 후 “Ennoia 연결 상태와 현재 프로젝트를 확인해줘”라고 요청해 연결을 확인합니다. 변경 사항은 [릴리스 내역](https://github.com/wanteddev/ennoia-plugin/releases)에서 볼 수 있습니다.

## 문제 해결

| 증상 | 확인할 내용 |
| --- | --- |
| 저장소를 찾을 수 없음 | GitHub 저장소 읽기 권한과 앱의 GitHub 연결 권한을 확인합니다. CLI에서는 Git 인증 상태를 확인합니다. |
| CLI에 `plugin` 명령이 없음 | Codex CLI 또는 Claude Code를 업데이트합니다. |
| 설치했는데 Skill이 안 보임 | Plugin 활성화를 확인하고 새 대화·세션을 시작합니다. |
| Skill은 보이는데 Ennoia에 연결되지 않음 | Plugin의 MCP 활성화와 Ennoia 로그인을 확인합니다. Claude Code에서는 `/mcp`를 사용합니다. |
| 이미 Ennoia MCP를 수동 등록함 | Plugin과 기존 연결이 함께 있을 수 있습니다. 별도 MCP를 추가 등록하지 말고 실제 사용하는 연결부터 확인합니다. |

<details>
<summary><strong>플러그인 제거</strong></summary>

앱에서는 Plugin 관리 화면에서 Ennoia를 제거합니다. CLI에서는 해당 명령을 사용합니다.

```bash
# Codex CLI
codex plugin remove ennoia@ennoia

# Claude Code
claude plugin uninstall ennoia@ennoia
```

Plugin 제거와 Ennoia OAuth 권한 철회는 별개입니다. 연결 권한도 해제하려면 해당 앱·CLI의 연결 관리에서 처리합니다.

</details>

## 개발 및 기여

- [개발·검증·릴리스 안내](CONTRIBUTING.md): 저장소 구조, manifest 생성, 검사 명령, 릴리스 절차
- [Skill 동작 평가](evals/README.md): 평가 시나리오와 실제 확인된 범위
- [공통 응답 규칙](plugins/ennoia/references/response-guide.md): 프로젝트 표시, 작업 상태, 에이전트 링크

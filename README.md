# Ennoia Plugin

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="plugins/ennoia/assets/logo-dark.svg">
  <img src="plugins/ennoia/assets/logo.svg" alt="Ennoia" width="240">
</picture>

Ennoia에서 에이전트를 만들고, 문서를 지식으로 연결하고, App에 업무를 요청하고, 배포·실행 상태를 관리하는 Plugin입니다.

**하나의 repo, 하나의 Skill 원본을 Codex App·Claude App·Codex CLI·Claude CLI에서 사용합니다.** 앱은 ZIP 업로드 없이 GitHub repo를 Marketplace로 추가합니다.

- Marketplace: `ennoia`
- Plugin: `ennoia` · 설치 식별자: `ennoia@ennoia`
- Repo: `wanteddev/ennoia-plugin`
- Ennoia MCP: `https://mcp.ennoia.so/mcp`
- Runtime 설치 의존성: 없음. Plugin에는 Skill·설정·참고자료만 포함하며 MCP는 원격으로 연결합니다.

## 앱에서 설치

### Codex App

플러그인 → 마켓플레이스 추가에서 아래 값을 입력합니다.

| 필드 | 값 |
| --- | --- |
| 출처 | `wanteddev/ennoia-plugin` |
| Git ref | `main` |
| Sparse 경로 | **비워 둡니다** |

마켓플레이스를 추가한 뒤 **Ennoia → 설치**를 선택합니다. 요청되는 Ennoia 로그인을 완료하고 새 작업에서 사용합니다. repo 전체가 작으므로 Sparse checkout이 필요하지 않습니다. 다른 예시의 `plugins/codex` 경로를 입력하면 이 repo의 설치 구성을 누락하게 됩니다.

### Claude App

Plugin을 지원하는 Claude App의 마켓플레이스 추가 화면에서 **URL에 `wanteddev/ennoia-plugin`** 또는 `https://github.com/wanteddev/ennoia-plugin.git`을 입력하고 **동기화**합니다. Ennoia Marketplace에서 Ennoia Plugin을 설치합니다. Ennoia 연결의 OAuth 로그인도 완료합니다.

일반 채팅의 파일 첨부·ZIP 업로드 메뉴가 아닌 **Plugin Marketplace**를 사용합니다. 앱의 Code/Cowork 등 Plugin 지원 작업 환경에서 사용하며, 일반 채팅의 MCP connector와 Plugin Skill 지원은 구분합니다. 앱의 계정·조직 정책에 따라 Marketplace와 connector를 허용해야 할 수 있습니다.

### 비공개 repo 접근

현재 이 repo는 비공개입니다. 설치 계정에 `wanteddev/ennoia-plugin` 읽기 권한이 필요합니다. Claude App의 GitHub 연결이 저장소를 표시하지 않으면 해당 GitHub App/조직 연결에 repo 접근을 허용해야 합니다. CLI는 사용자의 Git/SSH credential을 사용합니다. repo를 public으로 바꾸거나 token을 URL·manifest에 넣을 필요가 없습니다. **GitHub repo 접근과 Ennoia OAuth는 별도의 인증입니다.**

## CLI에서 설치

### Codex CLI

```bash
codex plugin marketplace add wanteddev/ennoia-plugin --ref main
codex plugin add ennoia@ennoia
```

새 세션에서 `/skills` 또는 `$ennoia-connect`로 시작합니다. MCP 인증이 요구되면 설치된 Ennoia 서버에 대해 host가 제시하는 로그인 흐름을 완료합니다. Plugin이 관리하는 서버를 별도 `codex mcp add`로 중복 등록하지 않습니다.

### Claude CLI (Claude Code)

```bash
claude plugin marketplace add https://github.com/wanteddev/ennoia-plugin.git
claude plugin install ennoia@ennoia
```

새 세션에서 `/ennoia:ennoia-connect`를 실행합니다. `/mcp`에서 Plugin의 Ennoia 서버를 선택해 로그인합니다. GitHub shorthand `wanteddev/ennoia-plugin`도 지원하지만 SSH 설정이 없는 환경에서는 위 HTTPS URL이 편리합니다.

설치에 사용한 버전과 실제 확인 범위는 [호환성·검증 기록](docs/compatibility.md)을 참고합니다. 오래된 CLI에 `plugin add` 또는 `plugin install` 명령이 없다면 해당 제품을 먼저 업데이트합니다.

## 사용하기

자연어로 Ennoia 작업을 요청하면 관련 Skill을 선택합니다. Skill을 명시하려면 Codex에서 `$스킬이름`, Claude Code에서 `/ennoia:스킬이름`을 사용하거나 앱의 Skill 선택기를 이용합니다.

| Skill | 요청 예시 |
| --- | --- |
| `ennoia-connect` | “Ennoia에 연결하고 A팀 운영 프로젝트를 선택해줘.” |
| `ennoia-build-agent` | “Ennoia 고객응대봇을 수정하고 검증한 뒤 draft까지만 저장해줘.” |
| `ennoia-knowledge` | “이 문서를 지식 컬렉션에 등록하고 검색 가능한 상태인지 확인해줘.” |
| `ennoia-run` | “Ennoia App으로 이 업무를 처리하고 기존 대화에서 이어가줘.” |
| `ennoia-diagnose` | “Ennoia 고객응대봇의 실패 원인과 사용량을 확인해줘.” |
| `ennoia-publish` | “저장된 Ennoia 에이전트를 배포하고 배포 상태를 확인해줘.” |
| `ennoia-integrations` | “Ennoia에서 data-gateway 등록 여부와 내 연결 상태를 확인해줘.” |

작업은 로그인 사용자의 Ennoia 권한과 프로젝트 범위에서 수행합니다. 기본 프로젝트가 자동 선택됐다면 변경 전에 대상을 명시해야 합니다. 이미 지정한 대상과 승인한 작업은 반복 승인하지 않습니다. Credential은 host의 인증 저장소에 두고 Plugin repo에 저장하지 않습니다.

결과는 그룹·프로젝트 이름으로 안내합니다. 현재 설정과 이번 요청 대상이 다르면 둘을 구분하고, 코드·ID는 기술 상세 요청이나 대상 구분·조회 재개에 필요할 때 표시합니다. 진행 중·부분 실패·미확인 비용을 완료나 0으로 바꾸지 않으며, 실제 App 답변은 관리 요약으로 대체하지 않습니다. 이 규칙은 7개 Skill이 [공통 참고자료](plugins/ennoia/references/response-guide.md)를 함께 사용합니다.

이미 같은 endpoint를 수동 MCP로 사용 중이라면 각 항목의 source·scope와 실제 요청 연결을 확인합니다. host마다 수동 서버·Plugin·connector가 항상 하나로 합쳐진다고 가정하지 않습니다. 기존 수동 연결의 정리는 사용자가 이전을 요청한 경우에만 선택적으로 진행하며 credential을 다른 source로 복사하지 않습니다.

파일 첨부가 곧 Ennoia 업로드 완료를 의미하지 않습니다. 문서는 업로드·인덱싱 준비·에이전트 연결을 각각 확인합니다. host에 binary 전송 기능이 없는 경우 Skill이 Ennoia 업로드 화면 경로를 안내합니다.

## 업데이트·제거

앱에서는 Marketplace 동기화/업데이트 후 Ennoia Plugin을 업데이트하고 새 작업에서 확인합니다.

```bash
# Codex
codex plugin marketplace upgrade ennoia
codex plugin add ennoia@ennoia

# Claude Code
claude plugin marketplace update ennoia
claude plugin update ennoia@ennoia
```

업데이트 뒤 새 세션을 열어 Plugin과 7개 Skill 발견 → 실제 Ennoia MCP 서버 인증 → 현재 그룹·프로젝트 선택 확인 → 읽기 도구 1건의 성공 순서로 확인합니다. Claude CLI에서는 `/mcp`에서 Plugin 서버를 선택합니다. Codex CLI에서는 설치 inventory의 실제 서버 이름을 확인하고 host가 제공하는 그 서버의 인증 안내를 따릅니다. 수동 `ennoia` 등록이 없는 계정에 `codex mcp login ennoia`가 반드시 적용되는 것은 아닙니다. Skill이 보이는데 Ennoia tool이 없다면 먼저 Plugin MCP 활성화와 서버 연결을 확인합니다.

제거는 `codex plugin remove ennoia@ennoia` 또는 `claude plugin uninstall ennoia@ennoia`를 사용합니다. Plugin 제거와 Ennoia 계정의 OAuth 권한 철회는 별개이므로 연결 철회까지 필요하면 host의 연결 관리에서 처리합니다.

## 저장소 구조

```text
.agents/plugins/marketplace.json     # Codex Marketplace
.claude-plugin/marketplace.json      # Claude Marketplace
plugins/ennoia/
  plugin.json                       # Portable metadata 원본
  mcp.json                          # Remote MCP 설정 원본
  .codex-plugin/plugin.json          # Codex 호환 manifest
  .claude-plugin/plugin.json         # Claude manifest
  .mcp.json                         # 두 host의 호환 MCP 설정
  skills/                           # 공유 Skill 원본 7개
  references/                       # 공통 응답 해석·표시 규칙
  assets/                           # 공식 아이콘·로고, 다크 모드용 로고
scripts/                            # 작성자용 sync·검증 도구
tests/                              # 배포 회귀 검증과 tool 계약 snapshot
evals/                              # 모델 동작 검증 시나리오
```

두 Marketplace는 동일한 `./plugins/ennoia`를 설치합니다. Plugin 밖을 참조하는 파일이나 symlink가 없어 host cache로 복사된 뒤에도 동일하게 동작하도록 구성했습니다. End user가 Python이나 스크립트를 실행할 필요는 없습니다.

## 개발·릴리스

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/sync_manifests.py --check
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

Metadata·version은 `plugins/ennoia/plugin.json`, MCP 설정은 `plugins/ennoia/mcp.json`에서 수정한 뒤 `python3 scripts/sync_manifests.py`로 호환 파일을 생성합니다. 이 명령은 공식 asset 원본에서 다크 모드 로고와 Skill별 아이콘 복사본도 생성합니다. Skill은 `plugins/ennoia/skills` 원본에서 수정합니다. 동일한 버전을 덮어쓰지 말고 릴리스 시 version을 올려 host cache를 갱신합니다.

아이콘·로고 출처, 브랜드 색상과 host별 표시 범위는 [브랜드 자산](docs/branding.md)을 참고합니다.

[기여·검증 기준](CONTRIBUTING.md)과 [동작 평가](evals/README.md)를 따라 검증합니다. CI는 credential 없이 패키지 구조와 회귀 테스트를 실행합니다. Native client 검증, OAuth, 실제 MCP 업무 결과와 latency 개선은 별도로 확인해야 합니다.

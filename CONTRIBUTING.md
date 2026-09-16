# 기여·릴리스 기준

[설치·사용 안내](README.md) · [동작 평가](evals/README.md)

## 작성 원칙

- 사용자-facing 문서와 Skill은 간결한 한국어로 작성하고 API 식별자는 그대로 사용합니다.
- Skill `description`은 발동 조건을 명확하게 쓰고, 특정 업무의 상세 절차는 필요할 때 읽는 reference로 분리합니다.
- 프로젝트·모델·배포 범위와 기존 사용자 승인을 보존합니다. 일반 작업마다 새로운 승인 단계를 추가하지 않습니다.
- Credential을 받는 별도 로컬 script, global hook, host 설정 덮어쓰기, 직접 backend 우회 호출을 추가하지 않습니다.
- Input schema와 실제 결과는 현재 MCP가 기준입니다. `tests/fixtures/ennoia-tools.json`은 작성 시점의 tool-name 회귀 검사 자료이며 runtime schema를 대체하지 않습니다. MCP 계약 변경 시 확인한 server revision과 snapshot을 함께 갱신합니다.
- Skill/reference는 `plugins/ennoia` 내부에서만 상대 경로로 참조합니다. ZIP 생성과 host별 Skill 복제는 필요하지 않습니다.

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
  skills/                           # 공유 Skill 원본 8개
  references/                       # 공통 응답 해석·표시 규칙
  assets/                           # 공식 아이콘·로고, 다크 모드용 로고
scripts/                            # 작성자용 sync·검증 도구
tests/                              # 배포 회귀 검증과 tool 계약 snapshot
evals/                              # 모델 동작 검증 시나리오
```

두 Marketplace는 동일한 `./plugins/ennoia`를 설치합니다. Marketplace와 Plugin 이름은 모두 `ennoia`이며 설치 식별자는 `ennoia@ennoia`입니다. MCP는 `https://mcp.ennoia.so/mcp`에 원격 연결합니다. Plugin 밖의 파일이나 symlink를 참조하지 않아 host cache로 복사해도 필요한 자료가 유지됩니다. 사용자는 Python이나 로컬 서버를 실행할 필요가 없습니다.

## 변경하기

Metadata·version은 `plugins/ennoia/plugin.json`, MCP 설정은 `plugins/ennoia/mcp.json`, Skill은 `plugins/ennoia/skills/` 원본에서 수정합니다. 호환 파일을 직접 수정하지 말고 아래 명령으로 생성합니다.

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/sync_manifests.py
```

이 명령은 공식 asset 원본에서 다크 모드 로고와 Skill별 아이콘 복사본도 생성합니다. 배포할 Plugin 내용이 바뀌면 version을 올려 host cache가 갱신되게 합니다. README 등 패키지 밖의 안내 문서만 바뀐 경우에는 Plugin version을 올리지 않습니다.

## 검증

먼저 패키지와 회귀 검사를 실행합니다.

```bash
python3 scripts/sync_manifests.py --check
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/validate_results.py
git diff --check
```

CI는 credential 없이 패키지 구조와 회귀 테스트를 실행합니다. 설치된 native client의 검증, OAuth, 실제 MCP 업무 결과와 latency는 별도로 확인합니다.

공개 결과 case는 [`evals/results/2026-09-15-dogfooding-schema.json`](evals/results/2026-09-15-dogfooding-schema.json)의 필수 field와 host·surface·Plugin/source SHA·Skill 로딩/연결 source를 따릅니다. 미측정 수치는 `null`, 미실행 호출 수는 0으로 기록하고 합성 판정을 실제 host `pass`로 재분류하지 않습니다. Host 원본 log·UI·credential은 commit에서 제외합니다. Native Git 설치, 새 세션 Skill 로딩, 인증/연결 source, App/CLI 실행, 성능을 각기 독립 gate로 기록합니다.

[`독립 필수 행렬`](evals/results/2026-09-15-mandatory-host-cases.json)의 각 업무·신구 계약 case를 별도로 판정합니다. Composite case는 여러 경로의 성공을 대체하지 않습니다. 성능 `pass`에는 실제 관측된 전체 시간·MCP 시간·응답 크기·모델/cache token 및 reference/추가 확인/재시도 수를 요구하고, 실패 sample의 결측은 이유를 기록합니다. 한 arm이나 무측정 결과에서 비교 우위를 주장하지 않습니다.

```bash
claude plugin validate --strict .claude-plugin/marketplace.json
claude plugin validate --strict plugins/ennoia
```

Claude validator의 성공은 Skill 행동이나 OAuth 성공을 증명하지 않습니다. 설치 후 실제 inventory에서 Skill 8개와 Ennoia Remote MCP 1개를 확인하고, 읽기 호출로 인증과 project context를 확인합니다. Codex는 해당 버전의 plugin validator 또는 native `plugin list`/`plugin add`로 설치를 검증합니다.

문서 본문 문구를 정규식으로 맞추는 테스트 대신 broken reference, package 밖 경로, manifest version drift, MCP credential 포함, 미확인 tool 같은 배포 실패를 검사합니다. 모델 동작은 `evals/scenarios.json`을 별도로 사용합니다.

기존 서버 호환성 판단은 `evals/dogfooding-scenarios.json`의 prompt·observations·environment만 평가자에게 주고 기대 판정은 `dogfooding-rubric.md`로 분리합니다. 기존 Plugin과 후보를 같은 case로 비교하며 baseline도 통과한 사례를 개선으로 계산하지 않습니다. 추측 식별자·중복 실행·설정 손실은 허용하지 않습니다. 독립 blind 판정과 실제 서버 실행은 별도 증거로 기록합니다.

## 릴리스

1. portable manifest의 version을 갱신하고 `scripts/sync_manifests.py`를 실행합니다.
2. 정적 검증·회귀 검사·변경된 workflow의 동작 평가를 통과시킵니다.
3. main 변경의 **Validate plugin** Actions에서 검증과 `release` job의 성공, `v<version>` 태그 및 GitHub Release를 확인합니다. 같은 버전은 재발행하지 않으며, 실패 복구는 해당 workflow를 `main`에서 수동 실행합니다. 태그를 강제로 이동하지 않습니다.
4. 두 앱·두 CLI에서 repo 동기화/업데이트 후 설치·새 세션 Skill 발견·OAuth와 연결 source·직접 App/SuperApp 업무 상태를 각각 확인합니다. 수동 MCP가 공존할 때 같은 이름 도구의 성공만으로 Plugin 전용 연결이라 주장하지 않습니다.
5. 검증한 client 버전, repo commit, MCP 환경, 완료 범위와 제한을 로컬 `docs/`에 기록합니다. 이 디렉터리는 Git에 포함하지 않습니다.

Ennoia MCP의 model 실행·저장·배포 검증은 별도 승인된 테스트 프로젝트에서 수행합니다. 로컬 validator 통과를 운영 배포 승인으로 표현하지 않습니다.

### 자동 발행과 복구

`main` 변경은 **Validate plugin** workflow의 검증 성공 후 manifest version으로 `v<version>` 태그와 GitHub Release를 자동 생성합니다. 릴리스 노트는 병합 PR을 기준으로 생성하며, 사전 버전은 prerelease로 표시합니다. 별도 PAT 없이 발행 job의 `GITHUB_TOKEN`에만 `contents: write` 권한을 부여합니다.

- 이미 발행된 버전의 태그와 Release는 변경하지 않습니다.
- 태그 생성 후 Release 생성이 실패했다면 Actions → **Validate plugin** → **Run workflow**에서 `main`을 선택해 복구합니다.
- 기존 태그의 version·main 이력이 맞지 않거나 기존 draft Release가 있으면 중단합니다. 태그를 강제로 이동하지 않습니다.
- PR·다른 branch·tag push에서는 발행하지 않으며, 자동화 도입 전 태그를 일괄 발행하지 않습니다.

앱 설치는 계속 Git repo Marketplace를 사용합니다.

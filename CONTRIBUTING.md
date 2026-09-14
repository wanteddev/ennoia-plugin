# 기여·릴리스 기준

- 사용자-facing 문서와 Skill은 간결한 한국어로 작성하고 API 식별자는 그대로 사용합니다.
- Skill `description`은 발동 조건을 명확하게 쓰고, 특정 업무의 상세 절차는 필요할 때 읽는 reference로 분리합니다.
- 프로젝트·모델·배포 범위와 기존 사용자 승인을 보존합니다. 일반 작업마다 새로운 승인 단계를 추가하지 않습니다.
- Credential을 받는 별도 로컬 script, global hook, host 설정 덮어쓰기, 직접 backend 우회 호출을 추가하지 않습니다.
- Input schema와 실제 결과는 현재 MCP가 기준입니다. `tests/fixtures/ennoia-tools.json`은 작성 시점의 tool-name 회귀 검사 자료이며 runtime schema를 대체하지 않습니다. MCP 계약 변경 시 확인한 server revision과 snapshot을 함께 갱신합니다.
- Skill/reference는 `plugins/ennoia` 내부에서만 상대 경로로 참조합니다. ZIP 생성과 host별 Skill 복제는 필요하지 않습니다.

## 검증

README의 Python 검증에 더해 설치된 native client로 아래를 확인합니다.

```bash
claude plugin validate --strict .claude-plugin/marketplace.json
claude plugin validate --strict plugins/ennoia
```

Claude validator의 성공은 Skill 행동이나 OAuth 성공을 증명하지 않습니다. 설치 후 실제 inventory에서 Skill 7개와 Ennoia Remote MCP 1개를 확인하고, 읽기 호출로 인증과 project context를 확인합니다. Codex는 해당 버전의 plugin validator 또는 native `plugin list`/`plugin add`로 설치를 검증합니다.

문서 본문 문구를 정규식으로 맞추는 테스트 대신 broken reference, package 밖 경로, manifest version drift, MCP credential 포함, 미확인 tool 같은 배포 실패를 검사합니다. 모델 동작은 `evals/scenarios.json`을 별도로 사용합니다.

## 릴리스

1. portable manifest의 version을 갱신하고 `scripts/sync_manifests.py`를 실행합니다.
2. 정적 검증·회귀 검사·변경된 workflow의 동작 평가를 통과시킵니다.
3. main 변경의 GitHub Actions 성공을 확인합니다.
4. 두 앱·두 CLI에서 repo 동기화/업데이트 후 설치·발견·OAuth 상태를 확인합니다.
5. 검증한 client 버전, repo commit, MCP 환경, 완료 범위와 제한을 `docs/compatibility.md`에 기록합니다.

Ennoia MCP의 model 실행·저장·배포 검증은 별도 승인된 테스트 프로젝트에서 수행합니다. 로컬 validator 통과를 운영 배포 승인으로 표현하지 않습니다.

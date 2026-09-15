# Ennoia 브랜드 자산

Plugin 1.0.2부터 Codex의 플러그인 표시와 7개 Skill UI에 브랜드 자산을 지정합니다. 설치 시 파일을 함께 복사하므로 아이콘 표시를 위해 외부 URL에 접속할 필요가 없습니다.

## 원본과 적용 위치

| 항목 | 적용 파일·값 | 출처 |
| --- | --- | --- |
| 작은 아이콘 | `plugins/ennoia/assets/icon.png` · 192 × 192 PNG | [현재 Ennoia 서비스의 파비콘](https://ennoia.so/images/_copied-assets/favicon-v2/favicon-192x192.png) |
| 기본 로고 | `plugins/ennoia/assets/logo.svg` · 공식 SVG 원본 | [공식 프런트엔드의 Ennoia 워드마크](https://github.com/wanteddev/laas-one-frontend/blob/75a59c9d01db545b119d741289903d0cd3f1ea95/packages/ui/src/assets/images/_client/ennoia/logos/light.svg) |
| 다크 모드 로고 | `plugins/ennoia/assets/logo-dark.svg` | 같은 SVG의 `fill: #14181d`를 `#ffffff`로 변환한 표시용 파생본. 도형·비율·여백은 유지 |
| 브랜드 강조색 | `#0066FF` | [서비스 UI의 `--palette-primary-normal`](https://github.com/wanteddev/laas-one-frontend/blob/75a59c9d01db545b119d741289903d0cd3f1ea95/packages/ui/src/styles.css#L327) |
| 로고 원색 | `#14181D` | 공식 워드마크 SVG의 fill |

2026-09-15에 `https://ennoia.so`의 HTML에서 파비콘 URL을 확인하고, 배포된 CSS의 `--palette-primary-normal: #06f`와 대조했습니다. 현재 서비스의 컬러 파비콘은 프런트엔드의 `_client/wanted/favicon-v2/favicon-192x192.png`와 바이트 단위로 같습니다. 새 Ennoia 전용 심볼을 임의로 만들지 않고 현재 서비스가 노출하는 자산을 사용합니다. 기본 로고는 Ennoia 워드마크이며, 다크 모드 파생본이 별도로 제공된 공식 원본이라는 의미는 아닙니다.

원본 확인용 SHA-256:

```text
icon.png  b72b67bb4a28695aa1258438257e2c30eeb5f330f942a41a36abbca33a66031e
logo.svg  2bf066e770d3838d4ef13d0ee9cf755d4a27eda93505c045b23aa0b1902b3b4d
```

## Host별 설정

- Codex: portable manifest의 `extensions.com.openai.interface`와 생성된 `.codex-plugin/plugin.json`에 `composerIcon`, `logo`, `logoDark`, `brandColor`를 설정합니다. 설치된 Codex의 로고 경로 처리와 공식 validator에서 필드를 확인했습니다.
- 7개 Skill: `agents/openai.yaml`의 `icon_small`, `icon_large`, `brand_color`를 설정합니다. 두 icon 필드는 작은 화면과 큰 화면에서 모두 식별되는 동일한 컬러 심볼을 사용합니다. host의 Skill 경로 제한에 맞춰 각 Skill 내부에 원본과 동일한 아이콘 파일을 생성합니다.
- Claude: 같은 파일을 포함한 Plugin을 설치하지만 [현재 공식 Plugin manifest](https://code.claude.com/docs/en/plugins-reference#metadata-fields)에는 Codex와 같은 icon·brand color 표시 필드가 없습니다. 지원하지 않는 필드를 추가하지 않으며 Claude의 화면이 Codex와 동일하게 표시된다고 보장하지 않습니다.

[밝은·어두운 배경 미리보기](branding-preview.html)는 제공 파일의 크기·대비를 확인하는 정적 페이지이며 실제 Codex App 화면의 캡처가 아닙니다. 설정 필드는 [OpenAI 패키징 명세](https://developers.openai.com/plugins/build/plugins#add-openai-specific-metadata)를 따릅니다.

## 유지보수·검증

원본은 `assets/icon.png`와 `assets/logo.svg`입니다. `python3 scripts/sync_manifests.py`로 다크 모드 로고·Skill 아이콘을 생성하며, `--check`는 생성 파일과 원본의 불일치를 CI에서 차단합니다. `scripts/validate.py`는 이미지 경로·존재 여부와 hex 색상을 검사합니다.

1.0.2는 브랜드 변경을 담은 PR 버전입니다. main에 병합된 뒤 Marketplace를 동기화하고 Plugin을 업데이트해야 기존 1.0.1 설치에 반영됩니다. 이 변경에서 MCP 연결·Skill 실행 지침·권한은 수정하지 않습니다.

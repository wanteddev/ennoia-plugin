#!/usr/bin/env python3
"""Portable manifest와 공식 asset 원본에서 host별 배포 파일을 생성한다."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEX_PAYLOAD = Path("plugins/ennoia-codex")
SHARED_COMPONENTS = ("assets", "mcp", "references", "skills")


def outputs(root: Path) -> dict[Path, dict]:
    plugin = root / "plugins/ennoia"
    manifest = json.loads((plugin / "plugin.json").read_text(encoding="utf-8"))
    mcp = json.loads((plugin / "mcp.json").read_text(encoding="utf-8"))
    identity = {k: v for k, v in manifest.items() if k not in {"$schema", "extensions"}}
    expected_servers = {
        "ennoia": {"type": "streamable-http", "url": "https://mcp.ennoia.so/mcp"},
        "ennoia-file-uploader": {"type": "stdio", "command": "node", "cwd": "./", "args": ["-e", "import(require('node:url').pathToFileURL(require('node:path').join(process.env.CLAUDE_PLUGIN_ROOT || process.cwd(), 'mcp/file-uploader.mjs')).href).then(m => m.serve()).catch(() => { process.exitCode = 1; })"]},
    }
    if mcp.get("mcpServers") != expected_servers:
        raise ValueError("Ennoia 배포는 지정한 remote MCP와 local file uploader만 지원합니다.")
    servers = {
        **expected_servers,
        "ennoia": {**expected_servers["ennoia"], "type": "http"},
    }
    return {
        plugin / ".claude-plugin/plugin.json": identity,
        plugin / ".codex-plugin/plugin.json": {
            **identity, "skills": "./skills/", "mcpServers": "./.mcp.json",
            **manifest["extensions"]["com.openai"],
        },
        plugin / ".mcp.json": {"mcpServers": servers},
        root / ".claude-plugin/marketplace.json": {
            "name": "ennoia", "owner": manifest["author"],
            "metadata": {"description": manifest["description"]},
            "plugins": [{"name": manifest["name"], "source": "./plugins/ennoia", "description": manifest["description"], "version": manifest["version"]}],
        },
        root / ".agents/plugins/marketplace.json": {
            "name": "ennoia", "interface": {"displayName": "Ennoia"},
            "plugins": [{"name": manifest["name"], "source": {"source": "local", "path": "./plugins/ennoia-codex"},
                         "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Productivity"}],
        },
    }


def asset_outputs(root: Path) -> dict[Path, bytes]:
    plugin = root / "plugins/ennoia"
    icon = (plugin / "assets/icon.png").read_bytes()
    logo = (plugin / "assets/logo.svg").read_text(encoding="utf-8")
    # 원본 vector path는 보존하고 dark mode의 단색 fill만 흰색으로 전환한다.
    original_fill = "fill: #14181d;"
    if logo.count(original_fill) != 1:
        raise ValueError("공식 로고 fill이 바뀌었습니다. dark mode 변환을 확인하세요.")
    assets = {plugin / "assets/logo-dark.svg": logo.replace(original_fill, "fill: #ffffff;").encode("utf-8")}
    # Skill UI asset 경로는 Skill 내부에 둔다. 원본은 하나이며 복사본은 생성한다.
    for skill in sorted((plugin / "skills").glob("*/SKILL.md")):
        assets[skill.parent / "assets/icon.png"] = icon
    return assets


def generated_outputs(root: Path) -> dict[Path, bytes]:
    """공통 원본과 생성 metadata로 self-contained Codex payload까지 만든다."""
    source = root / "plugins/ennoia"
    if source.is_symlink() or any(path.is_symlink() for path in source.rglob("*")):
        raise ValueError("공유 payload에 symlink를 사용할 수 없습니다.")
    generated = {path: (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
                 for path, data in outputs(root).items()}
    generated.update(asset_outputs(root))
    shared = {}
    for component in SHARED_COMPONENTS:
        for path in sorted((source / component).rglob("*")):
            if path.is_file():
                shared[path] = path.read_bytes()
    # 첫 생성에서도 아직 disk에 없는 icon/logo와 최신 manifest를 복사한다.
    shared.update({path: data for path, data in generated.items()
                   if path.is_relative_to(source) and (
                       path.relative_to(source).parts[0] in SHARED_COMPONENTS
                       or path.relative_to(source).as_posix() in (".codex-plugin/plugin.json", ".mcp.json")
                   )})
    generated.update({root / CODEX_PAYLOAD / path.relative_to(source): data for path, data in shared.items()})
    return generated


def stale_codex_paths(root: Path, generated: dict[Path, bytes]) -> list[Path]:
    payload = root / CODEX_PAYLOAD
    expected_files = set(generated)
    expected_directories = {payload}
    for path in generated:
        if path.is_relative_to(payload):
            expected_directories.update(parent for parent in path.parents if parent.is_relative_to(payload))
    return sorted((path for path in payload.rglob("*")
                   if path not in (expected_directories if path.is_dir() else expected_files)),
                  key=lambda path: (-len(path.parts), str(path)))


def output_mismatches(root: Path, generated: dict[Path, bytes]) -> list[str]:
    mismatches = [str(path.relative_to(root)) for path, expected in generated.items()
                  if path.is_symlink() or not path.is_file() or path.read_bytes() != expected]
    mismatches.extend(str(path.relative_to(root)) for path in stale_codex_paths(root, generated))
    return sorted(mismatches)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="변경 없이 생성 결과의 일치 여부를 확인")
    args = parser.parse_args()
    generated = generated_outputs(ROOT)
    payload = ROOT / CODEX_PAYLOAD
    if payload.is_symlink() or any(path.is_symlink() for path in payload.rglob("*")):
        raise SystemExit("Codex 생성 payload에 symlink를 사용할 수 없습니다.")
    mismatches = output_mismatches(ROOT, generated) if args.check else []
    if not args.check:
        # 생성 경로만 정리한다. 남은 root plugin.json은 로딩 형식을 바꿀 수 있다.
        for path in stale_codex_paths(ROOT, generated):
            path.rmdir() if path.is_dir() else path.unlink()
        for path, expected in generated.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(expected)
    if mismatches:
        raise SystemExit("생성 파일이 원본과 다릅니다. python3 scripts/sync_manifests.py 실행 필요: " + ", ".join(mismatches))
    print("Manifest·Codex payload sync 확인 완료" if args.check else "호환 manifest·Codex payload 생성 완료")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Portable manifest 원본에서 host별 호환 manifest를 재현 가능하게 생성한다."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def outputs(root: Path) -> dict[Path, dict]:
    plugin = root / "plugins/ennoia"
    manifest = json.loads((plugin / "plugin.json").read_text(encoding="utf-8"))
    mcp = json.loads((plugin / "mcp.json").read_text(encoding="utf-8"))
    identity = {k: v for k, v in manifest.items() if k not in {"$schema", "extensions"}}
    servers = {}
    for name, config in mcp["mcpServers"].items():
        if config["type"] != "streamable-http":
            raise ValueError("Ennoia 배포는 Remote Streamable HTTP만 지원합니다.")
        servers[name] = {**config, "type": "http"}
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
            "plugins": [{"name": manifest["name"], "source": {"source": "local", "path": "./plugins/ennoia"},
                         "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Productivity"}],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="변경 없이 생성 결과의 일치 여부를 확인")
    args = parser.parse_args()
    mismatches = []
    for path, data in outputs(ROOT).items():
        expected = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                mismatches.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    if mismatches:
        raise SystemExit("Manifest가 원본과 다릅니다. python3 scripts/sync_manifests.py 실행 필요: " + ", ".join(mismatches))
    print("Manifest sync 확인 완료" if args.check else "호환 manifest 생성 완료")


if __name__ == "__main__":
    main()

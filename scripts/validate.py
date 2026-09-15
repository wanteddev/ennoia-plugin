#!/usr/bin/env python3
"""Repo 설치, cache 경로, Skill discovery와 Ennoia tool 참조 계약을 검증한다."""

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATTERN = re.compile(r"`((?:get|set|list|create|update|delete|clone|rename|share|start|continue|stop|deploy|invoke|add|connect|disconnect|import|upload|prepare|retry|validate|test|save|switch|logout)_[a-z_]+)`")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
# API field가 동사 prefix를 공유해도 tool 이름으로 취급하지 않는다.
FIELD_IDENTIFIERS = {"test_id", "deploy_version"}


def read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON object 필요: {path}")
    return data


def validate_brand_assets(base: Path, interface: dict, fields: tuple[str, ...], color_key: str) -> list[str]:
    errors = []
    color = interface.get(color_key)
    if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        errors.append(f"brand color 오류: {base.name}/{color_key}")
    for field in fields:
        value = interface.get(field)
        if not isinstance(value, str) or not value.startswith("./assets/"):
            errors.append(f"asset 경로 오류: {base.name}/{field}")
            continue
        target = (base / value).resolve()
        if not target.is_relative_to(base / "assets") or not target.is_file() or target.suffix not in {".png", ".svg"}:
            errors.append(f"누락 또는 asset 경로 밖 파일: {base.name}/{field}")
    return errors


def validate_repository(root: Path) -> list[str]:
    root = root.resolve()
    plugin = root / "plugins/ennoia"
    errors = []
    try:
        manifests = [read_json(plugin / p) for p in ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json")]
        portable, claude, codex = manifests
        for key in ("name", "version", "description", "author", "homepage", "repository", "keywords"):
            if any(m.get(key) != portable.get(key) for m in manifests[1:]):
                errors.append(f"manifest 불일치: {key}")
        if portable.get("name") != "ennoia" or not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?", portable.get("version", "")):
            errors.append("manifest name/version 오류")
        if codex.get("skills") != "./skills/" or codex.get("mcpServers") != "./.mcp.json":
            errors.append("manifest component 경로 오류")
        if portable.get("extensions", {}).get("com.openai", {}).get("interface") != codex.get("interface"):
            errors.append("manifest OpenAI interface 불일치")
        interface = codex.get("interface", {})
        errors.extend(validate_brand_assets(plugin, interface, ("composerIcon", "logo", "logoDark"), "brandColor"))
        for filename, transport in (("mcp.json", "streamable-http"), (".mcp.json", "http")):
            mcp = read_json(plugin / filename)
            if mcp.get("mcpServers") != {"ennoia": {"type": transport, "url": "https://mcp.ennoia.so/mcp"}}:
                errors.append(f"MCP 설정 오류 또는 credential 포함: {filename}")

        a = read_json(root / ".agents/plugins/marketplace.json")
        b = read_json(root / ".claude-plugin/marketplace.json")
        if a.get("name") != "ennoia" or b.get("name") != "ennoia":
            errors.append("marketplace 이름 불일치")
        if len(a.get("plugins", [])) != 1 or len(b.get("plugins", [])) != 1:
            errors.append("marketplace는 하나의 Ennoia payload를 설치해야 함")
        else:
            ac, bc = a["plugins"][0], b["plugins"][0]
            if ac.get("source") != {"source": "local", "path": "./plugins/ennoia"} or bc.get("source") != "./plugins/ennoia":
                errors.append("marketplace source 경로 오류")
            if ac.get("name") != "ennoia" or bc.get("name") != "ennoia" or bc.get("version") != portable["version"]:
                errors.append("marketplace manifest identity 불일치")
            if ac.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"} or ac.get("category") != "Productivity":
                errors.append("marketplace 설치·인증 policy 오류")

        tools = set(read_json(root / "tests/fixtures/ennoia-tools.json")["tools"])
        skills = sorted((plugin / "skills").glob("*/SKILL.md"))
        if not skills:
            errors.append("Skill이 없습니다")
        descriptions = []
        for skill in skills:
            text = skill.read_text(encoding="utf-8")
            parts = text.split("---", 2)
            if len(parts) != 3 or parts[0].strip():
                errors.append(f"Skill frontmatter 오류: {skill.parent.name}")
                continue
            metadata = yaml.safe_load(parts[1])
            if not isinstance(metadata, dict):
                errors.append(f"Skill metadata 오류: {skill.parent.name}")
                continue
            if metadata.get("name") != skill.parent.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill.parent.name):
                errors.append(f"Skill name 오류: {skill.parent.name}")
            description = metadata.get("description")
            if not isinstance(description, str) or not 20 <= len(description) <= 300:
                errors.append(f"Skill description 길이·형식 오류: {skill.parent.name}")
            else:
                descriptions.append(description)
            if not parts[2].strip() or len(parts[2]) > 6500:
                errors.append(f"Skill body 누락·초과: {skill.parent.name}")
            ui = yaml.safe_load((skill.parent / "agents/openai.yaml").read_text(encoding="utf-8"))
            if "$" + skill.parent.name not in ui.get("interface", {}).get("default_prompt", ""):
                errors.append(f"Skill UI prompt 참조 오류: {skill.parent.name}")
            skill_interface = ui.get("interface", {})
            errors.extend(validate_brand_assets(skill.parent, skill_interface, ("icon_small", "icon_large"), "brand_color"))
            if skill_interface.get("brand_color") != interface.get("brandColor"):
                errors.append(f"Skill brand color 불일치: {skill.parent.name}")
        if sum(map(len, descriptions)) > 1800:
            errors.append("Skill discovery description 총량 초과")

        for path in plugin.rglob("*"):
            if path.is_symlink():
                errors.append(f"cache 호환을 위해 symlink 금지: {path.relative_to(plugin)}")
            if not path.is_file() or path.suffix != ".md":
                continue
            text = path.read_text(encoding="utf-8")
            for tool in TOOL_PATTERN.findall(text):
                if tool not in tools and tool not in FIELD_IDENTIFIERS:
                    errors.append(f"미확인 tool 참조: {tool} ({path.relative_to(plugin)})")
            for link in LINK_PATTERN.findall(text):
                if link.startswith(("https://", "http://", "#")):
                    continue
                target = (path.parent / link.split("#")[0]).resolve()
                if not target.is_relative_to(plugin) or not target.is_file():
                    errors.append(f"누락 또는 package 밖 reference: {link} ({path.relative_to(plugin)})")
            if "[TODO" in text or "TBD" in text:
                errors.append(f"미완성 placeholder: {path.relative_to(plugin)}")
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        errors.append(f"패키지 읽기·schema 오류: {exc}")
    return errors


def main() -> None:
    errors = validate_repository(ROOT)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    plugin = ROOT / "plugins/ennoia"
    skills = sorted((plugin / "skills").glob("*/SKILL.md"))
    print(json.dumps({"valid": True, "version": read_json(plugin / "plugin.json")["version"], "skills": len(skills), "skill_file_characters": sum(len(p.read_text(encoding="utf-8")) for p in skills)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

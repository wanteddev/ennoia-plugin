#!/usr/bin/env python3
"""검증된 main의 manifest version으로 Git tag와 GitHub Release를 발행한다."""

import base64
import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

MANIFEST = "plugins/ennoia/plugin.json"
VERSION = re.compile(
    r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
)


class GitHub:
    def __init__(self, repository: str, token: str, api_url: str):
        self.url = f"{api_url.rstrip('/')}/repos/{repository}"
        self.token = token

    def request(self, path: str, data: dict | None = None):
        request = Request(
            f"{self.url}/{path}",
            data=None if data is None else json.dumps(data).encode(),
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2026-03-10",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            error.close()
            # 조회 404만 부재로 취급한다. 인증·rate limit·쓰기 실패는 숨기지 않는다.
            if data is None and error.code == 404:
                return None
            raise RuntimeError(f"GitHub {request.get_method()} {path}: HTTP {error.code}") from None


def publish(api: GitHub, version: str, sha: str) -> str:
    match = VERSION.fullmatch(version) if isinstance(version, str) else None
    if not match or any(
        part.isdigit() and len(part) > 1 and part.startswith("0")
        for part in (match[4] or "").split(".")
    ):
        raise ValueError("manifest version은 유효한 SemVer여야 합니다.")
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("검증 대상의 전체 commit SHA가 필요합니다.")
    tag = f"v{version}"
    main_ref = api.request("git/ref/heads/main")
    if not main_ref:
        raise RuntimeError("main ref를 조회할 수 없습니다.")
    if main_ref["object"]["sha"] != sha:
        return "더 최신 main 실행이 있으므로 이전 실행의 발행을 건너뜁니다."

    release = api.request(f"releases/tags/{tag}")
    tag_ref = api.request(f"git/ref/tags/{tag}")
    if tag_ref:
        obj = tag_ref["object"]
        # Lightweight tag와 annotated tag 모두 원래 commit을 보존한다.
        for _ in range(8):
            if obj["type"] != "tag":
                break
            obj = api.request(f"git/tags/{obj['sha']}")["object"]
        if obj["type"] != "commit":
            raise RuntimeError(f"{tag}: commit을 가리키는 tag가 아닙니다.")
        target = obj["sha"]
        if target != sha:
            comparison = api.request(f"compare/{target}...{sha}")
            if not comparison or comparison["status"] not in {"ahead", "identical"}:
                raise RuntimeError(f"{tag}: 현재 main의 이력에 없는 tag입니다.")
        content = api.request(f"contents/{MANIFEST}?ref={target}")
        if not content or content.get("encoding") != "base64":
            raise RuntimeError(f"{tag}: 기존 manifest를 확인할 수 없습니다.")
        previous = json.loads(base64.b64decode(content["content"]))
        if previous.get("version") != version:
            raise RuntimeError(f"{tag}: tag와 manifest version이 다릅니다.")
    else:
        if release:
            raise RuntimeError(f"{tag}: Release는 있지만 tag가 없습니다.")
        target = sha
        api.request("git/refs", {"ref": f"refs/tags/{tag}", "sha": target})

    if release:
        if release["draft"]:
            raise RuntimeError(f"{tag}: 기존 draft Release를 먼저 확인하세요.")
        return f"{tag}: 이미 발행되어 변경 없이 종료합니다."

    # tag 생성 뒤 실패해도 다음 실행은 같은 tag에서 Release만 복구한다.
    result = api.request("releases", {
        "tag_name": tag,
        "target_commitish": target,
        "name": f"Ennoia Plugin {tag}",
        "draft": False,
        "prerelease": bool(match[4]),
        "generate_release_notes": True,
        "make_latest": "legacy",
    })
    return f"{tag}: {result['html_url']}"


def main() -> None:
    if os.environ.get("GITHUB_REF") != "refs/heads/main" or os.environ.get(
        "GITHUB_EVENT_NAME"
    ) not in {"push", "workflow_dispatch"}:
        raise SystemExit("main의 push 또는 workflow_dispatch에서만 발행합니다.")
    manifest = Path(__file__).resolve().parents[1] / MANIFEST
    api = GitHub(
        os.environ["GITHUB_REPOSITORY"],
        os.environ["GITHUB_TOKEN"],
        os.environ["GITHUB_API_URL"],
    )
    message = publish(api, json.loads(manifest.read_text())["version"], os.environ["GITHUB_SHA"])
    print(message)
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as output:
            output.write(f"{message}\n")


if __name__ == "__main__":
    main()

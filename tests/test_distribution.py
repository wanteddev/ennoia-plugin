"""실제 배포 artifact 경로와 네 클라이언트의 공통 payload 계약을 검사한다."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DistributionTests(unittest.TestCase):
    def test_marketplaces_keep_identity_and_select_host_specific_payloads(self):
        catalogs = [ROOT / ".agents/plugins/marketplace.json", ROOT / ".claude-plugin/marketplace.json"]
        for catalog in catalogs:
            self.assertTrue(catalog.is_file(), f"배포 marketplace가 없습니다: {catalog.relative_to(ROOT)}")
        codex, claude = [json.loads(p.read_text()) for p in catalogs]
        self.assertEqual(codex["name"], claude["name"])
        a, b = codex["plugins"][0], claude["plugins"][0]
        self.assertEqual(a["name"], b["name"])
        self.assertEqual(codex["name"], "ennoia")
        self.assertEqual(a["name"], "ennoia")
        self.assertEqual(a["source"]["path"], "./plugins/ennoia-codex")
        self.assertEqual(b["source"], "./plugins/ennoia")

    def test_codex_cache_contains_complete_legacy_payload(self):
        source = ROOT / "plugins/ennoia"
        payload = ROOT / "plugins/ennoia-codex"
        self.assertFalse((payload / "plugin.json").exists(), "root manifest는 Agent Plugin 경로를 선택하게 합니다")
        manifest = json.loads((payload / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(manifest["name"], "ennoia")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["mcpServers"], "./.mcp.json")
        self.assertEqual((payload / ".mcp.json").read_bytes(), (source / ".mcp.json").read_bytes())
        self.assertEqual(
            sorted(p.parent.name for p in (payload / "skills").glob("*/SKILL.md")),
            ["ennoia-build-agent", "ennoia-connect", "ennoia-diagnose", "ennoia-feedback",
             "ennoia-integrations", "ennoia-knowledge", "ennoia-publish", "ennoia-run"],
        )
        for component in ("skills", "references", "assets", "mcp"):
            expected = {p.relative_to(source) for p in (source / component).rglob("*") if p.is_file()}
            actual = {p.relative_to(payload) for p in (payload / component).rglob("*") if p.is_file()}
            self.assertEqual(actual, expected, component)
            for path in expected:
                self.assertEqual((payload / path).read_bytes(), (source / path).read_bytes(), str(path))

    def test_regeneration_removes_stale_files_that_change_codex_loading(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(
                ".git", ".venv", ".local", ".superpowers", "__pycache__", "docs", "results",
            ))
            script = root / "scripts/sync_manifests.py"
            def run(*args):
                return subprocess.run([sys.executable, str(script), *args], cwd=temp, capture_output=True, text=True)
            self.assertEqual(run().returncode, 0)
            source = root / "plugins/ennoia/references/temporary.md"
            source.write_text("source reference\n")
            self.assertNotEqual(run("--check").returncode, 0)
            self.assertEqual(run().returncode, 0)
            generated = root / "plugins/ennoia-codex/references/temporary.md"
            self.assertEqual(generated.read_text(), source.read_text())
            source.unlink()
            source.mkdir()
            (source / "child.md").write_text("nested reference\n")
            self.assertNotEqual(run("--check").returncode, 0)
            self.assertEqual(run().returncode, 0)
            self.assertEqual((generated / "child.md").read_text(), "nested reference\n")
            shutil.rmtree(source)
            source.write_text("file restored\n")
            self.assertEqual(run().returncode, 0)
            self.assertEqual(generated.read_text(), "file restored\n")
            source.unlink()
            stale_manifest = root / "plugins/ennoia-codex/plugin.json"
            stale_manifest.write_text((root / "plugins/ennoia/plugin.json").read_text())
            self.assertNotEqual(run("--check").returncode, 0)
            self.assertEqual(run().returncode, 0)
            self.assertFalse(generated.exists())
            self.assertFalse(stale_manifest.exists())
            self.assertEqual(run("--check").returncode, 0)
            stale_manifest.mkdir()
            self.assertNotEqual(run("--check").returncode, 0)
            self.assertEqual(run().returncode, 0)
            self.assertFalse(stale_manifest.exists())

    def test_generator_rejects_symlinked_component_before_copying_outside_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(
                ".git", ".venv", ".local", ".superpowers", "__pycache__", "docs", "results",
            ))
            outside = Path(temp) / "outside"
            outside.mkdir()
            (outside / "private.md").write_text("outside package\n")
            references = root / "plugins/ennoia/references"
            shutil.rmtree(references)
            references.symlink_to(outside, target_is_directory=True)
            result = subprocess.run([sys.executable, str(root / "scripts/sync_manifests.py")],
                                    cwd=temp, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "plugins/ennoia-codex/references/private.md").exists())


if __name__ == "__main__":
    unittest.main()

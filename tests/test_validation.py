"""배포 후 깨지는 경로와 credential 포함을 실제 artifact 변형으로 검증한다."""

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / "scripts/validate.py").is_file(), "패키지 검증기가 아직 없습니다")
        spec = importlib.util.spec_from_file_location("ennoia_validation", ROOT / "scripts/validate.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.validate = module.validate_repository
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "results"))

    def test_valid_repository(self):
        self.assertEqual(self.validate(self.root), [])

    def test_local_uploader_is_packaged_and_contract_changes_are_rejected(self):
        plugin = self.root / "plugins/ennoia"
        self.assertTrue((plugin / "mcp/file-uploader.mjs").is_file())
        for filename in ("mcp.json", ".mcp.json"):
            path = plugin / filename
            original = json.loads(path.read_text())
            self.assertEqual(original["mcpServers"]["ennoia-file-uploader"], {
                "command": "node", "cwd": ".", "args": ["-e", "import(require('node:url').pathToFileURL(require('node:path').join(process.env.CLAUDE_PLUGIN_ROOT || process.cwd(), 'mcp/file-uploader.mjs')).href).then(m => m.serve()).catch(() => { process.exitCode = 1; })"],
            })
            for key, value in (("command", "sh"), ("cwd", ".."), ("args", ["./other.mjs"]), ("env", {"TOKEN": "secret"})):
                data = json.loads(json.dumps(original))
                data["mcpServers"]["ennoia-file-uploader"][key] = value
                path.write_text(json.dumps(data))
                self.assertTrue(any("MCP" in e for e in self.validate(self.root)))
            path.write_text(json.dumps(original))
        (plugin / "mcp/file-uploader.mjs").unlink()
        self.assertTrue(any("MCP" in e for e in self.validate(self.root)))

    def test_missing_reference_is_rejected(self):
        (self.root / "plugins/ennoia/skills/ennoia-knowledge/references/uploads.md").unlink()
        self.assertTrue(any("reference" in e for e in self.validate(self.root)))

    def test_reference_outside_plugin_cache_is_rejected(self):
        skill = self.root / "plugins/ennoia/skills/ennoia-run/SKILL.md"
        skill.write_text(skill.read_text() + "\n[local](../../../../README.md)\n")
        self.assertTrue(any("reference" in e for e in self.validate(self.root)))

    def test_mcp_credential_configuration_is_rejected(self):
        path = self.root / "plugins/ennoia/.mcp.json"
        data = json.loads(path.read_text())
        data["mcpServers"]["ennoia"]["headers"] = {"Authorization": "Bearer fixture-only"}
        path.write_text(json.dumps(data))
        self.assertTrue(any("MCP" in e for e in self.validate(self.root)))

    def test_version_drift_is_rejected(self):
        path = self.root / "plugins/ennoia/.claude-plugin/plugin.json"
        data = json.loads(path.read_text())
        data["version"] = "0.0.0"
        path.write_text(json.dumps(data))
        self.assertTrue(any("manifest" in e for e in self.validate(self.root)))

    def test_hallucinated_tool_reference_is_rejected(self):
        skill = self.root / "plugins/ennoia/skills/ennoia-run/SKILL.md"
        skill.write_text(skill.read_text() + "\n`get_ennoia_fictional_resume`\n")
        self.assertTrue(any("tool" in e for e in self.validate(self.root)))

    def test_symlink_outside_payload_is_rejected(self):
        (self.root / "plugins/ennoia/outside").symlink_to(self.root.parent)
        self.assertTrue(any("symlink" in e for e in self.validate(self.root)))

    def test_missing_plugin_brand_asset_is_rejected(self):
        (self.root / "plugins/ennoia/assets/logo-dark.svg").unlink()
        self.assertTrue(any("asset" in e for e in self.validate(self.root)))

    def test_skill_icon_outside_its_cache_directory_is_rejected(self):
        path = self.root / "plugins/ennoia/skills/ennoia-connect/agents/openai.yaml"
        path.write_text(path.read_text().replace("./assets/icon.png", "../../assets/icon.png"))
        self.assertTrue(any("asset" in e for e in self.validate(self.root)))

    def test_invalid_brand_color_is_rejected(self):
        for name in ("plugin.json", ".codex-plugin/plugin.json"):
            path = self.root / "plugins/ennoia" / name
            data = json.loads(path.read_text())
            interface = data["extensions"]["com.openai"]["interface"] if name == "plugin.json" else data["interface"]
            interface["brandColor"] = "blue"
            path.write_text(json.dumps(data))
        self.assertTrue(any("brand" in e for e in self.validate(self.root)))


if __name__ == "__main__":
    unittest.main()

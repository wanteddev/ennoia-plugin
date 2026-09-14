"""실제 배포 artifact 경로와 네 클라이언트의 공통 payload 계약을 검사한다."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DistributionTests(unittest.TestCase):
    def test_both_marketplaces_resolve_the_same_installable_payload(self):
        catalogs = [ROOT / ".agents/plugins/marketplace.json", ROOT / ".claude-plugin/marketplace.json"]
        for catalog in catalogs:
            self.assertTrue(catalog.is_file(), f"배포 marketplace가 없습니다: {catalog.relative_to(ROOT)}")
        codex, claude = [json.loads(p.read_text()) for p in catalogs]
        self.assertEqual(codex["name"], claude["name"])
        a, b = codex["plugins"][0], claude["plugins"][0]
        self.assertEqual(a["name"], b["name"])
        self.assertEqual(a["source"]["path"], b["source"])
        payload = (ROOT / b["source"]).resolve()
        self.assertTrue(payload.is_relative_to(ROOT))
        self.assertTrue((payload / ".claude-plugin/plugin.json").is_file())
        self.assertTrue((payload / ".codex-plugin/plugin.json").is_file())
        self.assertTrue((payload / "plugin.json").is_file())
        self.assertGreaterEqual(len(list((payload / "skills").glob("*/SKILL.md"))), 5)


if __name__ == "__main__":
    unittest.main()

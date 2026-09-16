import base64
import json
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from scripts.release import GitHub, MANIFEST, main, publish


SHA = "a" * 40
OLD = "b" * 40
TAG = "v1.1.0"


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.responses = {
            "git/ref/heads/main": {"object": {"sha": SHA}},
            f"releases/tags/{TAG}": None,
            f"git/ref/tags/{TAG}": None,
        }
        self.writes = []
        self.api = Mock(spec=GitHub)
        self.api.request.side_effect = self.request

    def request(self, path, data=None):
        if data is not None:
            self.writes.append((path, data))
            return {"html_url": f"https://github.com/wanteddev/ennoia-plugin/releases/tag/{TAG}"}
        return self.responses[path]

    def existing_tag(self, target=SHA, version="1.1.0", annotated=False):
        self.responses[f"git/ref/tags/{TAG}"] = {
            "object": {"type": "tag" if annotated else "commit", "sha": target}
        }
        if annotated:
            self.responses[f"git/tags/{target}"] = {"object": {"type": "commit", "sha": target}}
        self.responses[f"contents/{MANIFEST}?ref={target}"] = {
            "encoding": "base64",
            "content": base64.b64encode(json.dumps({"version": version}).encode()).decode(),
        }
        self.responses[f"compare/{target}...{SHA}"] = {"status": "ahead"}

    def test_creates_tag_at_validated_sha_and_published_release(self):
        publish(self.api, "1.1.0", SHA)
        self.assertEqual(self.writes, [
            ("git/refs", {"ref": f"refs/tags/{TAG}", "sha": SHA}),
            ("releases", {
                "tag_name": TAG, "target_commitish": SHA, "name": f"Ennoia Plugin {TAG}",
                "draft": False, "prerelease": False, "generate_release_notes": True,
                "make_latest": "legacy",
            }),
        ])

    def test_rerun_of_published_version_never_writes(self):
        self.existing_tag()
        self.responses[f"releases/tags/{TAG}"] = {"draft": False}
        publish(self.api, "1.1.0", SHA)
        self.assertEqual(self.writes, [])

    def test_later_main_commit_with_same_version_preserves_release(self):
        self.existing_tag(OLD)
        self.responses[f"releases/tags/{TAG}"] = {"draft": False}
        publish(self.api, "1.1.0", SHA)
        self.assertEqual(self.writes, [])

    def test_recovers_release_at_existing_annotated_tag(self):
        self.existing_tag(OLD, annotated=True)
        publish(self.api, "1.1.0", SHA)
        self.assertEqual(len(self.writes), 1)
        self.assertEqual(self.writes[0][0], "releases")
        self.assertEqual(self.writes[0][1]["target_commitish"], OLD)

    def test_release_failure_leaves_tag_for_next_run(self):
        def fail_release(path, data=None):
            if path == "releases":
                raise RuntimeError("HTTP 503")
            result = self.request(path, data)
            if path == "git/refs":
                self.existing_tag()
            return result

        self.api.request.side_effect = fail_release
        with self.assertRaisesRegex(RuntimeError, "503"):
            publish(self.api, "1.1.0", SHA)
        self.api.request.side_effect = self.request
        self.writes.clear()
        publish(self.api, "1.1.0", SHA)
        self.assertEqual([path for path, _ in self.writes], ["releases"])

    def test_mismatched_tag_version_is_never_overwritten(self):
        self.existing_tag(version="1.0.0")
        with self.assertRaisesRegex(RuntimeError, "version"):
            publish(self.api, "1.1.0", SHA)
        self.assertEqual(self.writes, [])

    def test_tag_outside_main_history_is_rejected(self):
        self.existing_tag(OLD)
        self.responses[f"compare/{OLD}...{SHA}"] = {"status": "diverged"}
        with self.assertRaisesRegex(RuntimeError, "이력"):
            publish(self.api, "1.1.0", SHA)
        self.assertEqual(self.writes, [])

    def test_non_commit_tag_is_rejected(self):
        self.responses[f"git/ref/tags/{TAG}"] = {"object": {"type": "tree", "sha": SHA}}
        with self.assertRaisesRegex(RuntimeError, "commit"):
            publish(self.api, "1.1.0", SHA)
        self.assertEqual(self.writes, [])

    def test_draft_is_not_published_or_replaced(self):
        self.existing_tag()
        self.responses[f"releases/tags/{TAG}"] = {"draft": True}
        with self.assertRaisesRegex(RuntimeError, "draft"):
            publish(self.api, "1.1.0", SHA)
        self.assertEqual(self.writes, [])

    def test_release_without_tag_is_not_retargeted(self):
        self.responses[f"releases/tags/{TAG}"] = {"draft": False}
        with self.assertRaisesRegex(RuntimeError, "tag가 없습니다"):
            publish(self.api, "1.1.0", SHA)
        self.assertEqual(self.writes, [])

    def test_stale_workflow_cannot_publish(self):
        self.responses["git/ref/heads/main"] = {"object": {"sha": OLD}}
        publish(self.api, "1.1.0", SHA)
        self.api.request.assert_called_once_with("git/ref/heads/main")
        self.assertEqual(self.writes, [])

    def test_prerelease_and_build_metadata(self):
        for version, prerelease in [("1.2.0-rc.1", True), ("1.2.0+build.01", False)]:
            with self.subTest(version=version):
                self.writes.clear()
                self.responses[f"releases/tags/v{version}"] = None
                self.responses[f"git/ref/tags/v{version}"] = None
                publish(self.api, version, SHA)
                self.assertEqual(self.writes[-1][1]["tag_name"], f"v{version}")
                self.assertIs(self.writes[-1][1]["prerelease"], prerelease)

    def test_invalid_versions_and_sha_fail_before_api(self):
        for version in [None, 11, "v1.1.0", "01.1.0", "1.1.0-01", "1.1.0\n", "../../main"]:
            with self.subTest(version=version), self.assertRaises(ValueError):
                publish(self.api, version, SHA)
        with self.assertRaises(ValueError):
            publish(self.api, "1.1.0", "main")
        self.api.request.assert_not_called()

    def test_entrypoint_rejects_pull_requests_and_non_main_refs(self):
        for ref, event in [("refs/heads/main", "pull_request"), ("refs/tags/v1.1.0", "push"),
                           ("refs/heads/dev", "workflow_dispatch")]:
            with self.subTest(ref=ref, event=event):
                with patch.dict("os.environ", {"GITHUB_REF": ref, "GITHUB_EVENT_NAME": event}, clear=True):
                    with self.assertRaises(SystemExit):
                        main()


class GitHubTests(unittest.TestCase):
    def test_only_get_404_means_absent(self):
        api = GitHub("wanteddev/ennoia-plugin", "test-token", "https://api.github.com")
        for status, data in [(404, None), (401, None), (403, None), (500, None), (404, {}), (422, {})]:
            with self.subTest(status=status, data=data):
                error = HTTPError("https://api.github.com", status, "error", {}, None)
                with patch("scripts.release.urlopen", side_effect=error):
                    if status == 404 and data is None:
                        self.assertIsNone(api.request("releases/tags/v1.1.0"))
                    else:
                        with self.assertRaisesRegex(RuntimeError, f"HTTP {status}") as caught:
                            api.request("releases", data)
                        self.assertNotIn("test-token", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

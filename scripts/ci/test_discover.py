"""Tests for scripts/ci/discover.py. Standard library only:

python3 -m unittest discover -s scripts/ci -v
"""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import discover

WORKSPACE = """# layout from ADR 0008
packages:
  - "apps/*"
  - services/*   # bare globs work too
  - "packages/**"
  - "!packages/old/**"
"""


class RepoTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="kuizi-discover-")
        self.root = Path(self._tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, path, content=""):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")

    def found(self):
        return discover.discover(self.root)


class PythonTests(RepoTestCase):
    def test_default_gate_is_the_backend_gate_and_mypy_is_opt_in(self):
        self.write("ml/pyproject.toml", '[project]\nname = "ml"\n')
        self.write("services/api/pyproject.toml", "[tool.mypy]\n[tool.coverage.report]\nfail_under = 90\n")
        self.assertEqual(
            self.found()["python"],
            [
                {"path": "ml", "id": "ml", "coverage": 80, "typecheck": False},
                {"path": "services/api", "id": "services-api", "coverage": 90, "typecheck": True},
            ],
        )

    def test_mypy_ini_also_turns_on_the_type_check(self):
        self.write("schemas/events/pyproject.toml", "")
        self.write("schemas/events/mypy.ini", "[mypy]\n")
        self.assertTrue(self.found()["python"][0]["typecheck"])

    def test_hidden_ignored_and_vendored_folders_are_skipped(self):
        self.write(".gitignore", "scratch/\n")
        self.write("scratch/pyproject.toml", "")
        self.write(".github/ci-fixtures/py/pyproject.toml", "")
        self.write("ml/.venv/lib/site/pyproject.toml", "")
        self.write("apps/web/node_modules/x/pyproject.toml", "")
        self.assertEqual(self.found()["python"], [])

    def test_a_bad_gate_is_reported(self):
        self.write("ml/pyproject.toml", '[tool.coverage.report]\nfail_under = "high"\n')
        with self.assertRaisesRegex(discover.DiscoveryError, "fail_under"):
            self.found()


class TypeScriptTests(RepoTestCase):
    def setUp(self):
        super().setUp()
        self.write("pnpm-workspace.yaml", WORKSPACE)
        self.write("package.json", {"name": "kuizi", "private": True})

    def test_no_workspace_package_means_an_empty_list(self):
        self.assertEqual(self.found()["typescript"], [])

    def test_gates_follow_the_folder_and_can_be_overridden(self):
        self.write("apps/web/package.json", {"name": "@kuizi/web"})
        self.write("services/routing/package.json", {"name": "@kuizi/routing", "scripts": {"test:contract": "x"}})
        self.write("packages/auth/package.json", {"name": "@kuizi/auth", "kuizi": {"coverage": 90}})
        self.write("packages/deep/nested/package.json", {"name": "@kuizi/nested"})
        found = {p["path"]: p for p in self.found()["typescript"]}
        self.assertEqual(sorted(found), ["apps/web", "packages/auth", "packages/deep/nested", "services/routing"])
        self.assertEqual(found["apps/web"]["coverage"], 70)
        self.assertEqual(found["services/routing"]["coverage"], 80)
        self.assertTrue(found["services/routing"]["contract"])
        self.assertFalse(found["apps/web"]["contract"])
        self.assertEqual(found["packages/auth"]["coverage"], 90)
        self.assertEqual(found["packages/auth"]["name"], "@kuizi/auth")
        self.assertEqual(found["packages/deep/nested"]["id"], "packages-deep-nested")

    def test_single_star_stays_in_one_folder_and_negations_exclude(self):
        self.write("apps/web/tools/package.json", {"name": "not-a-package"})
        self.write("packages/old/legacy/package.json", {"name": "legacy"})
        self.write("tools/x/package.json", {"name": "outside-the-workspace"})
        self.assertEqual(self.found()["typescript"], [])

    def test_a_package_needs_a_name(self):
        self.write("packages/auth/package.json", {"private": True})
        with self.assertRaisesRegex(discover.DiscoveryError, "no name"):
            self.found()

    def test_workspace_globs_are_read_without_yaml(self):
        self.assertEqual(
            discover.workspace_globs(self.root), ["apps/*", "services/*", "packages/**", "!packages/old/**"]
        )


class ContainerTests(RepoTestCase):
    def test_service_images_publish_and_fixtures_only_scan(self):
        self.write("services/routing/Dockerfile", "FROM scratch\n")
        self.write(".github/ci-fixtures/container/Dockerfile", "FROM scratch\n")
        self.write(".devcontainer/Dockerfile", "FROM scratch\n")
        found = self.found()
        self.assertEqual(
            found["containers"],
            [
                {
                    "name": "kuizi-ci-fixture-container",
                    "dockerfile": ".github/ci-fixtures/container/Dockerfile",
                    "context": ".github/ci-fixtures/container",
                    "publish": False,
                },
                {"name": "kuizi-routing", "dockerfile": "services/routing/Dockerfile", "context": ".", "publish": True},
            ],
        )
        self.assertEqual([i["name"] for i in found["images"]], ["kuizi-routing"])

    def test_two_folders_with_the_same_name_are_refused(self):
        self.write("services/web/Dockerfile", "FROM scratch\n")
        self.write("apps/web/Dockerfile", "FROM scratch\n")
        with self.assertRaisesRegex(discover.DiscoveryError, "kuizi-web"):
            self.found()

    def test_a_root_dockerfile_is_refused(self):
        self.write("Dockerfile", "FROM scratch\n")
        with self.assertRaisesRegex(discover.DiscoveryError, "repository root"):
            self.found()


class OutputTests(RepoTestCase):
    def test_github_output_holds_one_compact_json_list_per_key(self):
        self.write("ml/pyproject.toml", "")
        output = self.root / "github_output"
        os.environ["GITHUB_OUTPUT"] = str(output)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(discover.main(["--root", str(self.root), "--github-output"]), 0)
        finally:
            del os.environ["GITHUB_OUTPUT"]
        lines = dict(line.split("=", 1) for line in output.read_text().splitlines())
        self.assertEqual(sorted(lines), ["containers", "images", "python", "typescript"])
        self.assertEqual(json.loads(lines["python"]), [{"path": "ml", "id": "ml", "coverage": 80, "typecheck": False}])
        self.assertEqual(lines["typescript"], "[]")

    def test_list_mode_prints_space_separated_fields(self):
        self.write("ml/pyproject.toml", "[tool.coverage.report]\nfail_under = 75\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            discover.main(["--root", str(self.root), "--list", "python"])
        self.assertEqual(out.getvalue(), "ml 75 false\n")

    def test_errors_exit_with_one(self):
        self.write("Dockerfile", "FROM scratch\n")
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(discover.main(["--root", str(self.root)]), 1)
        self.assertIn("repository root", err.getvalue())


if __name__ == "__main__":
    unittest.main()

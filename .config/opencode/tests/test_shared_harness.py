import re
import sys
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOTFILES = ROOT.parents[1]
SKILLS = ROOT / "skills"
SKILLS_README = SKILLS / "README.md"
AGENTS = ROOT / "AGENTS.md"
AGENT_DIR = DOTFILES / ".codex" / "agents"

sys.path.insert(0, str(DOTFILES / ".local" / "share" / "dotfiles" / "vendor"))
import yaml_parser  # noqa: E402


PORTABLE_SKILLS = {
    "brainstorming",
    "continuous-driven-development",
    "dispatching-parallel-agents",
    "finishing-a-development-branch",
    "grill-me",
    "grilling",
    "handoff",
    "receiving-code-review",
    "requesting-code-review",
    "research",
    "solve",
    "subagent-driven-development",
    "systematic-debugging",
    "test-driven-development",
    "to-questionnaire",
    "verification-before-completion",
    "writing-plans",
    "writing-skills",
}

ARTIFACT_PRODUCERS = {
    "brainstorming",
    "finishing-a-development-branch",
    "handoff",
    "research",
    "solve",
    "subagent-driven-development",
    "to-questionnaire",
    "writing-plans",
}

DISALLOWED_SKILL_PATTERNS = {
    "named VCS": re.compile(
        r"(?i)\b(?:git|svn|subversion|mercurial|perforce|fossil)\b|(?<!\w)hg(?!\w)"
    ),
    "worktree workflow": re.compile(r"(?i)\bworktrees?\b"),
    "Claude-specific wording": re.compile(r"(?i)\bclaude(?: code)?\b"),
    "Copilot-specific wording": re.compile(r"(?i)\bcopilot(?: cli)?\b"),
    "fixed task API": re.compile(r"(?i)\bTodoWrite\b|\bTask tool\b"),
    "browser presentation": re.compile(r"(?i)\bbrowser\b|visual companion"),
    "old artifact location": re.compile(r"docs/superpowers|docs/plans|temporary directory"),
    "fixed package or shell command": re.compile(
        r"(?i)\b(?:npm|pnpm|yarn|pytest|curl|wget)\s|\bbash\b|\.superpowers/"
    ),
}

PRIVATE_BUNDLE_PATTERNS = {
    "absolute home path": re.compile(r"/home/[A-Za-z0-9._-]+"),
    "private skill group": re.compile(r"skills/(?:direct|infra)"),
}


class SharedHarnessTest(unittest.TestCase):
    def skill_text(self, name):
        return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")

    def test_personal_agents_is_portable(self):
        text = AGENTS.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertNotRegex(lowered, r"\bgit\b")
        self.assertIn("300 seconds", lowered)
        self.assertIn("30 seconds", lowered)
        self.assertIn("closest applicable project instructions", lowered)
        self.assertIn("comments that merely restate the code", lowered)

    def test_straps_declare_split_harness_mappings(self):
        opencode = yaml_parser.safe_load((ROOT / "strap.yaml").read_text(encoding="utf-8"))
        skills = yaml_parser.safe_load((ROOT / "skills.strap.yaml").read_text(encoding="utf-8"))
        instructions = yaml_parser.safe_load((ROOT / "instructions.strap.yaml").read_text(encoding="utf-8"))
        codex = yaml_parser.safe_load((DOTFILES / ".codex" / "strap.yaml").read_text(encoding="utf-8"))
        self.assertEqual(opencode["platforms"]["generic"]["link"], ["opencode.jsonc"])
        self.assertEqual(skills["platforms"]["generic"], {
            "link": [
                ["skills", "~/.config/opencode/skills"],
                ["skills", "~/.agents/skills"],
                ["skills", "~/.claude/skills"],
            ],
        })
        self.assertEqual(len(instructions["platforms"]["generic"]["copy"]), 4)
        self.assertEqual(codex["platforms"]["generic"], {
            "link": [["agents", "~/.codex/agents"]],
        })

    def test_skill_entries_are_local_directories(self):
        external = sorted(
            entry.name
            for entry in SKILLS.iterdir()
            if entry.name not in {"README.md", "_shared"} and entry.is_symlink()
        )
        self.assertEqual(external, [])

    def test_skill_catalog_is_exact(self):
        actual = {
            entry.name
            for entry in SKILLS.iterdir()
            if entry.is_dir() and entry.name != "_shared"
        }
        self.assertEqual(actual, PORTABLE_SKILLS)

    def test_skill_frontmatter_matches_directory(self):
        for name in sorted(PORTABLE_SKILLS):
            with self.subTest(skill=name):
                text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
                match = re.match(r"\A---\n(?P<header>.*?)\n---\n", text, re.DOTALL)
                self.assertIsNotNone(match)
                header = match.group("header")
                self.assertRegex(header, rf"(?m)^name:\s*[\"']?{re.escape(name)}[\"']?\s*$")
                self.assertRegex(header, r"(?m)^description:\s*.+$")

    def test_skill_instructions_are_tool_neutral(self):
        failures = []
        for name in sorted(PORTABLE_SKILLS):
            for path in sorted((SKILLS / name).rglob("*.md")):
                text = path.read_text(encoding="utf-8")
                for label, pattern in DISALLOWED_SKILL_PATTERNS.items():
                    if pattern.search(text):
                        failures.append(f"{path.relative_to(SKILLS)}: {label}")
        self.assertEqual(failures, [])

    def test_named_vcs_guard_catches_provider_assumptions(self):
        pattern = DISALLOWED_SKILL_PATTERNS["named VCS"]
        for text in ("git commit", "svn commit", "hg commit", "perforce submit", "fossil commit"):
            with self.subTest(text=text):
                self.assertRegex(text, pattern)
        for text in ("semantic commit", "state-management capability", "safe synchronization"):
            with self.subTest(text=text):
                self.assertNotRegex(text, pattern)

    def test_public_bundle_contains_no_private_scope_markers(self):
        paths = [
            AGENTS,
            ROOT / "opencode.jsonc",
            ROOT / "strap.yaml",
            SKILLS_README,
            *sorted((SKILLS / "_shared").rglob("*.md")),
            *[
                path
                for name in sorted(PORTABLE_SKILLS)
                for path in sorted((SKILLS / name).rglob("*.md"))
            ],
            *sorted(AGENT_DIR.glob("*.toml")),
        ]
        failures = []
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for label, pattern in PRIVATE_BUNDLE_PATTERNS.items():
                if pattern.search(text):
                    failures.append(f"{path.relative_to(ROOT)}: {label}")
        self.assertEqual(failures, [])

    def test_artifact_producers_use_shared_policy(self):
        for name in sorted(ARTIFACT_PRODUCERS):
            with self.subTest(skill=name):
                text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("../_shared/artifact-policy.md", text)

    def test_grill_me_dependency_exists(self):
        text = (SKILLS / "grill-me" / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue((SKILLS / "grilling" / "SKILL.md").is_file())
        self.assertIn("grilling", text)

    def test_brainstorming_is_user_invoked_and_transitions_to_planning(self):
        text = (SKILLS / "brainstorming" / "SKILL.md").read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertRegex(text, r"(?m)^description:\s*Use when\b")
        self.assertIn("user explicitly requests", lowered)
        self.assertIn("solve handoff", lowered)
        self.assertIn("use `writing-plans`", text)

    def test_skills_readme_documents_codex_workflow_and_credits(self):
        text = SKILLS_README.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertIn("## codex workflow", lowered)
        self.assertIn("~/.codex/agents", text)
        for name in (
            "`implementer`",
            "`researcher`",
            "`checker`",
            "`solve`",
            "`brainstorming`",
            "`writing-plans`",
            "`continuous-driven-development`",
            "`subagent-driven-development`",
            "`finishing-a-development-branch`",
            "`requesting-code-review`",
            "`verification-before-completion`",
        ):
            with self.subTest(name=name):
                self.assertIn(name, text)
        self.assertRegex(lowered, r"obra.{0,80}superpowers|superpowers.{0,80}obra")
        self.assertIn("matt pocock", lowered)

    def test_development_execution_modes_are_canonical(self):
        continuous_name = "continuous-driven-development"
        subagent_name = "subagent-driven-development"
        removed_name = "executing-plans"
        self.assertTrue((SKILLS / continuous_name / "SKILL.md").is_file())
        self.assertTrue((SKILLS / subagent_name / "SKILL.md").is_file())
        self.assertFalse((SKILLS / removed_name).exists())
        for path in sorted(SKILLS.rglob("*.md")):
            with self.subTest(path=path.relative_to(SKILLS)):
                self.assertNotIn(removed_name, path.read_text(encoding="utf-8"))
        continuous = (SKILLS / continuous_name / "SKILL.md").read_text(encoding="utf-8")
        subagent = (SKILLS / subagent_name / "SKILL.md").read_text(encoding="utf-8")
        writing_plans = (SKILLS / "writing-plans" / "SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(continuous, rf"(?m)^name:\s*{continuous_name}$")
        self.assertIn("carried out inline", continuous)
        self.assertNotIn("`implementer`", continuous)
        self.assertRegex(subagent, rf"(?m)^name:\s*{subagent_name}$")
        self.assertIn("`implementer`", subagent)
        self.assertIn("`checker`", subagent)
        self.assertIn(f"{subagent_name} for independent tasks", writing_plans)
        self.assertIn(f"{continuous_name} for inline execution", writing_plans)

    def test_codex_agent_manifests(self):
        expected = {
            "implementer": ("gpt-5.6-terra", "high", None),
            "researcher": ("gpt-5.6-terra", "medium", "read-only"),
            "checker": ("gpt-5.6-sol", "medium", "read-only"),
        }
        self.assertEqual(
            {path.stem for path in AGENT_DIR.glob("*.toml")},
            set(expected),
        )
        for name, (model, effort, sandbox) in expected.items():
            with self.subTest(agent=name):
                data = tomllib.loads((AGENT_DIR / f"{name}.toml").read_text(encoding="utf-8"))
                self.assertEqual(data["name"], name)
                self.assertEqual(data["model"], model)
                self.assertEqual(data["model_reasoning_effort"], effort)
                self.assertEqual(data.get("sandbox_mode"), sandbox)
                self.assertTrue(data["description"])
                self.assertIn("Do not spawn", data["developer_instructions"])
                self.assertNotRegex(data["developer_instructions"].lower(), r"\bgit\b|worktree")

    def test_solve_declares_autonomous_routes_and_manifest(self):
        text = self.skill_text("solve")
        lowered = text.lower()
        self.assertIn("../_shared/artifact-policy.md", text)
        self.assertIn("finishing-a-development-branch", text)
        self.assertIn("continuous-driven-development", text)
        self.assertIn("brainstorming", text)
        self.assertIn("subagent-driven-development", text)
        self.assertIn("only `brainstorming`", lowered)
        self.assertIn("manifest-schema.md", text)
        self.assertIn("environment-discovery.md", text)
        self.assertIn("routing.md", text)

    def test_finishing_is_autonomous_state_finalization_only(self):
        text = self.skill_text("finishing-a-development-branch")
        lowered = text.lower()
        self.assertIn("../_shared/artifact-policy.md", text)
        self.assertIn("preservation", lowered)
        self.assertIn("delivery", lowered)
        self.assertIn("semantic", lowered)
        self.assertIn("draft", lowered)
        self.assertIn("unassigned", lowered)
        self.assertIn("expected-state", lowered)
        self.assertIn("does not run", lowered)
        for forbidden in ("npm test", "cargo test", "pytest", "go test", "present options", "which option"):
            self.assertNotIn(forbidden, lowered)

    def test_solve_references_are_direct_and_present(self):
        text = self.skill_text("solve")
        links = re.findall(r"\[[^]]+\]\(([^)]+\.md)\)", text)
        self.assertEqual(
            set(links),
            {"manifest-schema.md", "environment-discovery.md", "routing.md", "../_shared/artifact-policy.md"},
        )
        for link in links:
            self.assertTrue((SKILLS / "solve" / link).resolve().is_file())

    def test_solve_handoffs_are_declared(self):
        brainstorming = self.skill_text("brainstorming").lower()
        planning = self.skill_text("writing-plans").lower()
        continuous = self.skill_text("continuous-driven-development").lower()
        subagent = self.skill_text("subagent-driven-development").lower()
        self.assertIn("solve handoff", brainstorming)
        self.assertIn("solve handoff", planning)
        self.assertIn("solve handoff", continuous)
        self.assertIn("solve handoff", subagent)
        self.assertIn("return", continuous)
        self.assertIn("return", subagent)

    def test_solve_manifest_records_authority_identity_and_terminal_result(self):
        text = (SKILLS / "solve" / "manifest-schema.md").read_text(encoding="utf-8")
        self.assertIn("- Solve authorization", text)
        self.assertIn("- Branch-name derivation", text)
        self.assertIn("- Terminal result", text)

    def test_silent_review_has_non_notifying_fallback(self):
        finishing = self.skill_text("finishing-a-development-branch").lower()
        discovery = (SKILLS / "solve" / "environment-discovery.md").read_text(encoding="utf-8").lower()
        for text in (finishing, discovery):
            self.assertIn("non-draft", text)
            self.assertIn("non-notifying", text)


if __name__ == "__main__":
    unittest.main()

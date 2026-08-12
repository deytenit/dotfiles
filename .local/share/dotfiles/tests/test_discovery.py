import tempfile
import unittest
from pathlib import Path

from dotfiles.strap.discovery import StrapValidationError, discover_straps
from dotfiles.strap.models import OperationKind


class DiscoveryTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "repo"
        self.home = Path(self.temporary.name) / "home"
        self.repo.mkdir()
        self.home.mkdir()

    def write(self, relative: str, content: str) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def test_composes_generic_and_platform_operations_in_sorted_definitions(self):
        self.write("strap.yaml", """\
name: Generic
category: System
description: Generic settings
platforms:
  generic:
    link:
      - common.conf
  linux:
    link:
      - linux.conf
""")
        self.write("alpha.strap.yaml", """\
name: Alpha
category: System
description: Alpha settings
platforms:
  generic:
    copy:
      - [source.conf, ~/.config/alpha.conf]
""")

        definitions = discover_straps(self.repo, home=self.home, platform_name="linux")

        self.assertEqual([item.name for item in definitions], ["Alpha", "Generic"])
        self.assertEqual(
            [op.source.name for op in definitions[1].file_operations],
            ["common.conf", "linux.conf"],
        )
        self.assertEqual(definitions[0].file_operations[0].kind, OperationKind.COPY)
        self.assertEqual(definitions[0].file_operations[0].target, self.home / ".config/alpha.conf")

    def test_reports_all_legacy_and_invalid_documents_together(self):
        self.write("strap@linux.yaml", "name: old\n")
        self.write(".strap", "#!/bin/sh\n")
        self.write("bad.strap.yaml", """\
name: ""
category: Desktop
platforms:
  solaris:
    link: []
""")

        with self.assertRaises(StrapValidationError) as raised:
            discover_straps(self.repo, home=self.home, platform_name="linux")

        message = str(raised.exception)
        self.assertIn("strap@linux.yaml", message)
        self.assertIn(".strap", message)
        self.assertIn("bad.strap.yaml", message)
        self.assertIn("solaris", message)

    def test_normalizes_copy_objects_and_omits_inapplicable_straps(self):
        self.write("skills.strap.yaml", """\
name: Shared skills
category: Agent Harness
description: Shared tools
platforms:
  generic:
    copy:
      - source: skills
        target: ~/.agents/skills
        force: true
""")
        self.write("darwin.strap.yaml", """\
name: Mac only
category: Desktop
description: Mac desktop
platforms:
  darwin:
    link:
      - config
""")

        definitions = discover_straps(self.repo, home=self.home, platform_name="linux")

        self.assertEqual([item.name for item in definitions], ["Shared skills"])
        operation = definitions[0].file_operations[0]
        self.assertTrue(operation.force)
        self.assertEqual(operation.source, self.repo / "skills")
        self.assertEqual(operation.target, self.home / ".agents/skills")

    def test_rejects_bad_operation_shapes_and_invalid_cron(self):
        self.write("bad.strap.yaml", """\
name: Bad
category: Desktop
description: Broken example
platforms:
  generic:
    copy:
      - source: settings
        target: ~/.config/settings
        extra: nope
    cron:
      - ["61 * * * *", ""]
""")

        with self.assertRaises(StrapValidationError) as raised:
            discover_straps(self.repo, home=self.home, platform_name="linux")

        self.assertIn("unknown keys", str(raised.exception))
        self.assertIn("cron", str(raised.exception))

    def test_requires_a_non_empty_description(self):
        self.write("strap.yaml", """\
name: Missing description
category: System
platforms:
  generic:
    link: []
""")

        with self.assertRaises(StrapValidationError) as raised:
            discover_straps(self.repo, home=self.home, platform_name="linux")

        self.assertIn("description must be a non-empty string", str(raised.exception))


if __name__ == "__main__":
    unittest.main()

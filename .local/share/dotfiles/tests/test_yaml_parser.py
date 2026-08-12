import unittest

from dotfiles.vendor import yaml_parser


DOCUMENT = """\
name: Shared skills
category: Agent Harness
platforms:
  generic:
    copy:
      - source: skills
        target: ~/.agents/skills
        force: true
  linux:
    link:
      - [linux.conf, ~/.config/app/linux.conf]
"""


class YAMLParserTest(unittest.TestCase):
    def test_nested_platforms_and_mapping_list_item(self):
        value = yaml_parser.safe_load(DOCUMENT)

        self.assertEqual(value["platforms"]["generic"]["copy"][0], {
            "source": "skills",
            "target": "~/.agents/skills",
            "force": True,
        })
        self.assertEqual(
            value["platforms"]["linux"]["link"][0],
            ["linux.conf", "~/.config/app/linux.conf"],
        )

    def test_parses_comments_quoted_scalars_and_nested_flow_lists(self):
        value = yaml_parser.safe_load("""\
# comment
title: "hash #, comma, kept" # comment
values: ["a,b", [true, false, null], 'literal # value']
empty_map: {}
empty_list: []
""")

        self.assertEqual(value["title"], "hash #, comma, kept")
        self.assertEqual(value["values"], ["a,b", [True, False, None], "literal # value"])
        self.assertEqual(value["empty_map"], {})
        self.assertEqual(value["empty_list"], [])

    def test_rejects_inconsistent_indentation(self):
        with self.assertRaisesRegex(yaml_parser.YAMLParseError, "Line 2"):
            yaml_parser.safe_load("name: App\n  category: Bad\n")

    def test_rejects_duplicate_keys(self):
        with self.assertRaisesRegex(yaml_parser.YAMLParseError, "Line 2"):
            yaml_parser.safe_load("name: App\nname: Again\n")

    def test_rejects_bad_continuation_for_mapping_list_item(self):
        with self.assertRaisesRegex(yaml_parser.YAMLParseError, "Line 4"):
            yaml_parser.safe_load("copy:\n  - source: skills\n    target: ~/.agents/skills\n   force: true\n")

    def test_rejects_tab_indentation(self):
        with self.assertRaisesRegex(yaml_parser.YAMLParseError, "Line 2"):
            yaml_parser.safe_load("name: App\n\tcategory: Bad\n")

    def test_compatibility_aliases(self):
        self.assertIs(yaml_parser.load, yaml_parser.safe_load)
        self.assertIs(yaml_parser.YAMLError, yaml_parser.YAMLParseError)


if __name__ == "__main__":
    unittest.main()

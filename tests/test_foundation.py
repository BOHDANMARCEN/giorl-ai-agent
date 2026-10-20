from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from kohana_agent.cli import main
from kohana_agent.memory import MemoryStore
from kohana_agent.persona import render_persona
from kohana_agent.profile import create_profile


SOURCE = Path(__file__).resolve().parents[1] / "persona" / "persona_kohana_v3.xml"


class FoundationTests(unittest.TestCase):
    def test_persona_preserves_every_leaf_and_is_deterministic(self):
        rendered = render_persona(SOURCE)
        for leaf in ET.parse(SOURCE).iter():
            if not len(leaf):
                self.assertIn(" ".join((leaf.text or "").split()), rendered)
        self.assertEqual(rendered, render_persona(SOURCE))

    def test_profile_paths_and_no_clobber(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "hermes"
            paths = create_profile(home, SOURCE)
            self.assertEqual(len(paths), 3)
            self.assertTrue((home / "memories/USER.md").is_file())
            soul = home / "SOUL.md"
            soul.write_text("existing user persona", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                create_profile(home, SOURCE)
            self.assertEqual(soul.read_text(), "existing user persona")

    def test_invalid_persona_does_not_create_home(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "bad.xml"
            source.write_text('<ai_persona version="2.0"/>')
            home = Path(temporary) / "profile"
            with self.assertRaises(ValueError):
                create_profile(home, source)
            self.assertFalse(home.exists())

    def test_entities_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "bad.xml"
            source.write_text('<!DOCTYPE x [<!ENTITY a "x">]><ai_persona/>')
            with self.assertRaises(ValueError):
                render_persona(source)

    def test_persistence_project_filter_and_literal_query(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "memory.sqlite3"
            store = MemoryStore(path)
            content = "Українська: 100%_ ' OR 1=1 --"
            note_id = store.add(content, project="one", source="test")
            store.add(content, project="two", source="other")
            reopened = MemoryStore(path)
            rows = reopened.search("100%_", project="one")
            self.assertEqual([row["id"] for row in rows], [note_id])
            self.assertEqual(rows[0]["source"], "test")
            self.assertEqual(rows[0]["content"], content)
            self.assertTrue(rows[0]["created_at"].endswith("Z"))
            self.assertEqual(reopened.search("' OR 1=1 --", project="missing"), [])
            self.assertEqual(reopened.search("%"), reopened.search("100%_"))

    def test_empty_notes_and_invalid_limits_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            store = MemoryStore(Path(temporary) / "memory.sqlite3")
            for content, project, source in [(" ", "p", "s"), ("x", "", "s"), ("x", "p", "")]:
                with self.assertRaises(ValueError):
                    store.add(content, project=project, source=source)
            for query, limit in [("", 1), ("x", 0), ("x", 101)]:
                with self.assertRaises(ValueError):
                    store.search(query, limit=limit)

    def test_cli_returns_failure_for_existing_home(self):
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(main(["init", "--home", temporary, "--persona", str(SOURCE)]), 1)


if __name__ == "__main__":
    unittest.main()

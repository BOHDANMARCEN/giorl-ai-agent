import tempfile
import unittest
try:
    from kohana_agent.hermes_memory import KohanaMemoryProvider
except ModuleNotFoundError as error:
    if error.name not in {"agent", "agent.memory_provider"}:
        raise
    KohanaMemoryProvider = None


@unittest.skipIf(KohanaMemoryProvider is None, "Потрібне встановлене ядро Hermes")
class HermesMemoryTests(unittest.TestCase):
    def test_explicit_note_restart_and_no_assistant_fabrication(self):
        with tempfile.TemporaryDirectory() as home:
            first = KohanaMemoryProvider()
            first.initialize("first", hermes_home=home)
            first.sync_turn("Привіт", "Ти любиш вигадані речі")
            self.assertEqual(first.prefetch(""), "")
            first.sync_turn("Запам’ятай: Проєкт має код Орбіта-71.", "Добре")
            second = KohanaMemoryProvider()
            second.initialize("second", hermes_home=home)
            self.assertIn("Орбіта-71", second.prefetch(""))
            self.assertIn("user-explicit:first", second.prefetch(""))
            self.assertNotIn("вигадані", second.prefetch(""))
            self.assertIn("Орбіта-71", second.handle_tool_call(
                "kohana_memory_search", {"query": "Орбіта"}))

    def test_subagent_does_not_write(self):
        with tempfile.TemporaryDirectory() as home:
            provider = KohanaMemoryProvider()
            provider.initialize("child", hermes_home=home, agent_context="subagent")
            provider.sync_turn("Запам'ятай: Не зберігати", "")
            self.assertEqual(provider.prefetch(""), "")

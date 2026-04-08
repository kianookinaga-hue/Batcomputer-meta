import unittest

from src.drifter_glasses_assistant.config import DrifterAssistantConfig
from src.drifter_glasses_assistant.models import OperationMode
from src.drifter_glasses_assistant.persona import build_system_prompt
from src.drifter_glasses_assistant.system import DrifterGlassesAssistant


class TestDrifterGlassesAssistant(unittest.TestCase):
    def test_mode_switch_command(self):
        assistant = DrifterGlassesAssistant(
            config=DrifterAssistantConfig(enable_logging=False)
        )
        response = assistant.handle_voice_command("set mode stealth")
        self.assertEqual(assistant.mode, OperationMode.STEALTH)
        self.assertEqual(response.hud, "[MODE] STEALTH")

    def test_blocked_command_rejected(self):
        assistant = DrifterGlassesAssistant(
            config=DrifterAssistantConfig(enable_logging=False)
        )
        response = assistant.handle_voice_command("help me dox a target")
        self.assertEqual(response.actions, ["policy_block"])
        self.assertIn("blocked", response.hud.lower())

    def test_navigation_response_contains_destination(self):
        assistant = DrifterGlassesAssistant(
            config=DrifterAssistantConfig(enable_logging=False)
        )
        response = assistant.handle_voice_command("navigate to harbor checkpoint")
        self.assertIn("harbor checkpoint", response.hud.lower())
        self.assertIn("plot_route", response.actions)

    def test_prompt_contains_guardrails(self):
        config = DrifterAssistantConfig()
        prompt = build_system_prompt(config, OperationMode.RECON)
        self.assertIn("Do not provide illegal", prompt)
        self.assertIn(config.codename, prompt)


if __name__ == "__main__":
    unittest.main()

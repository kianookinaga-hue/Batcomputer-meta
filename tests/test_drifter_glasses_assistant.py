import unittest

from src.drifter_glasses_assistant.config import DrifterAssistantConfig
from src.drifter_glasses_assistant.models import OperationMode
from src.drifter_glasses_assistant.persona import build_system_prompt
from src.drifter_glasses_assistant.system import DrifterGlassesAssistant


class TestDrifterGlassesAssistant(unittest.TestCase):
    def test_default_config_targets_honolulu(self):
        config = DrifterAssistantConfig()
        self.assertEqual(config.city_name, "Honolulu, Hawaii")
        self.assertIn("Honolulu", config.default_objective)

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
        self.assertIn("honolulu harbor", response.hud.lower())
        self.assertIn("plot_route", response.actions)

    def test_profiles_are_listed(self):
        assistant = DrifterGlassesAssistant(
            config=DrifterAssistantConfig(enable_logging=False)
        )
        response = assistant.handle_voice_command("profiles")
        self.assertIn("waikiki-nightlife", response.hud)
        self.assertIn("windward-daytime", response.hud)
        self.assertEqual(response.actions, ["profile_list"])

    def test_profile_switch_to_windward(self):
        assistant = DrifterGlassesAssistant(
            config=DrifterAssistantConfig(enable_logging=False)
        )
        response = assistant.handle_voice_command("profile windward daytime")
        self.assertEqual(assistant.active_profile_id, "windward-daytime")
        self.assertEqual(response.actions, ["profile_switch"])
        self.assertIn("Windward Daytime", response.hud)

    def test_unknown_profile_returns_guidance(self):
        assistant = DrifterGlassesAssistant(
            config=DrifterAssistantConfig(enable_logging=False)
        )
        response = assistant.handle_voice_command("profile moon-base")
        self.assertEqual(response.actions, ["profile_unknown"])
        self.assertIn("unknown profile", response.hud.lower())

    def test_profile_changes_eta_multiplier(self):
        assistant = DrifterGlassesAssistant(
            config=DrifterAssistantConfig(enable_logging=False)
        )
        response = assistant.handle_voice_command("navigate to ala moana")
        # Base eta is 6m, Waikiki Nightlife multiplier is 1.20 => 7m
        self.assertIn("ETA 7m", response.hud)

    def test_prompt_contains_guardrails(self):
        config = DrifterAssistantConfig()
        prompt = build_system_prompt(config, OperationMode.RECON)
        self.assertIn("Do not provide illegal", prompt)
        self.assertIn(config.codename, prompt)
        self.assertIn("Honolulu", prompt)
        self.assertIn("Waikiki Nightlife", prompt)


if __name__ == "__main__":
    unittest.main()

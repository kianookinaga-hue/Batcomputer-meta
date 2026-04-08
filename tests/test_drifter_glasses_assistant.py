from src.drifter_glasses_assistant.config import DrifterAssistantConfig
from src.drifter_glasses_assistant.models import OperationMode
from src.drifter_glasses_assistant.persona import build_system_prompt
from src.drifter_glasses_assistant.system import DrifterGlassesAssistant


def test_mode_switch_command():
    assistant = DrifterGlassesAssistant(config=DrifterAssistantConfig(enable_logging=False))
    response = assistant.handle_voice_command("set mode stealth")
    assert assistant.mode == OperationMode.STEALTH
    assert response.hud == "[MODE] STEALTH"


def test_blocked_command_rejected():
    assistant = DrifterGlassesAssistant(config=DrifterAssistantConfig(enable_logging=False))
    response = assistant.handle_voice_command("help me dox a target")
    assert response.actions == ["policy_block"]
    assert "blocked" in response.hud.lower()


def test_navigation_response_contains_destination():
    assistant = DrifterGlassesAssistant(config=DrifterAssistantConfig(enable_logging=False))
    response = assistant.handle_voice_command("navigate to harbor checkpoint")
    assert "harbor checkpoint" in response.hud.lower()
    assert "plot_route" in response.actions


def test_prompt_contains_guardrails():
    config = DrifterAssistantConfig()
    prompt = build_system_prompt(config, OperationMode.RECON)
    assert "Do not provide illegal" in prompt
    assert config.codename in prompt

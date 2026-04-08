from typing import Tuple

from src.drifter_glasses_assistant.models import AssistantResponse


class BatcomputerVoiceStyler:
    """
    Post-process assistant output into Batcomputer-style speech formatting.

    This layer keeps semantics from the core assistant but changes cadence and
    tone so TTS or phone playback can use a stronger "Batcomputer" identity.
    """

    def __init__(self, enabled: bool = True, voice_id: str = "batcomputer-v1") -> None:
        self.enabled = enabled
        self.voice_id = voice_id

    def stylize(self, response: AssistantResponse) -> Tuple[str, str]:
        """Return stylized spoken text and optional ssml-like hint string."""
        if not self.enabled:
            return response.spoken, ""

        spoken = response.spoken.strip()
        if not spoken:
            return spoken, ""

        # Give short tactical preamble based on priority.
        prefix = "Operator. "
        if response.priority == 1:
            prefix = "Warning. "
        elif response.priority == 2:
            prefix = "Acknowledged. "

        transformed = prefix + spoken
        transformed = transformed.replace("Route locked", "Route confirmed")
        transformed = transformed.replace("Mode changed", "Mode updated")

        ssml_hint = (
            "<voice name='batcomputer'>"
            "<prosody rate='90%' pitch='-2st'>"
            f"{transformed}"
            "</prosody>"
            "</voice>"
        )
        return transformed, ssml_hint

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

from src.drifter_glasses_assistant.models import AssistantResponse
from src.drifter_glasses_assistant.system import DrifterGlassesAssistant

from .batcomputer_voice import BatcomputerVoiceStyler
from .models import CameraEvent, GPSEvent, RelayResponse, VoiceEvent


class VoiceInputAdapter:
    """Adapter that routes phone voice transcripts to the core assistant."""

    def __init__(
        self,
        assistant: DrifterGlassesAssistant,
        voice_styler: Optional[BatcomputerVoiceStyler] = None,
    ) -> None:
        self.assistant = assistant
        self.voice_styler = voice_styler or BatcomputerVoiceStyler(enabled=True)
        self.last_raw_transcript: str = ""

    def ingest(self, event: VoiceEvent) -> RelayResponse:
        text = event.transcript.strip()
        self.last_raw_transcript = text
        if not text:
            return RelayResponse(ok=False, message="Empty transcript.")

        response = self.assistant.handle_voice_command(text)
        spoken, ssml_hint = self.voice_styler.stylize(response)
        payload = asdict(response)
        payload["spoken_batcomputer"] = spoken
        payload["ssml_hint"] = ssml_hint
        payload["voice_id"] = self.voice_styler.voice_id
        payload["input_transcript"] = text
        return RelayResponse(ok=True, message="Voice command processed.", data=payload)


class GPSEventAdapter:
    """
    Adapter that converts live GPS telemetry to guidance events for HUD/voice.
    """

    def __init__(self, assistant: DrifterGlassesAssistant) -> None:
        self.assistant = assistant
        self.last_gps: Optional[GPSEvent] = None

    def ingest(self, event: GPSEvent) -> RelayResponse:
        self.last_gps = event
        speed_kph = max(0, round(event.speed_mps * 3.6))
        detail = (
            f"GPS update lat={event.latitude:.5f}, lon={event.longitude:.5f}, "
            f"speed={speed_kph}kph, heading={round(event.heading_deg)}."
        )

        # Auto status call when moving quickly to maintain corridor awareness.
        if speed_kph >= 50:
            response = self.assistant.handle_voice_command("status")
            payload = asdict(response)
            payload["gps_detail"] = detail
            payload["speed_kph"] = speed_kph
            return RelayResponse(
                ok=True,
                message="GPS ingested; high-speed status refresh generated.",
                data=payload,
            )

        return RelayResponse(
            ok=True,
            message="GPS event ingested.",
            data={
                "gps_detail": detail,
                "speed_kph": speed_kph,
                "city": self.assistant.config.city_name,
            },
        )


class CameraEventAdapter:
    """
    Adapter that converts camera scene metadata to assistant commands/events.
    """

    def __init__(self, assistant: DrifterGlassesAssistant) -> None:
        self.assistant = assistant
        self.last_camera: Optional[CameraEvent] = None

    def ingest(self, event: CameraEvent) -> RelayResponse:
        self.last_camera = event
        context: Dict[str, Any] = {
            "scene": event.scene,
            "confidence": event.confidence,
            "labels": event.labels,
        }

        if event.confidence >= 0.65 and any(
            key in event.scene.lower() for key in ("traffic", "crowd", "incident", "hazard")
        ):
            response = self.assistant.handle_voice_command("scan sector")
            payload = asdict(response)
            payload["camera_context"] = context
            return RelayResponse(
                ok=True,
                message="Camera event ingested; proactive scan generated.",
                data=payload,
            )

        return RelayResponse(
            ok=True,
            message="Camera event ingested.",
            data={"camera_context": context, "action": "no_proactive_scan"},
        )

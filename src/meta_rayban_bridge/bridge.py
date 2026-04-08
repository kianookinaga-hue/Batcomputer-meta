from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any, Dict, Optional

from src.drifter_glasses_assistant.system import DrifterGlassesAssistant

from .adapters import CameraEventAdapter, GPSEventAdapter, VoiceInputAdapter
from .batcomputer_voice import BatcomputerVoiceStyler
from .models import CameraEvent, GPSEvent, RelayResponse, VoiceEvent


class MetaRayBanBridge:
    """
    Integration layer that sits between phone/glasses events and assistant logic.

    Responsibilities:
    - route incoming phone relay payloads to typed adapters
    - apply Batcomputer voice styling on voice responses
    - retain lightweight event snapshots for quick dashboard/status use
    """

    def __init__(
        self,
        assistant: DrifterGlassesAssistant,
        voice_styler: Optional[BatcomputerVoiceStyler] = None,
    ) -> None:
        self.assistant = assistant
        self.voice_styler = voice_styler or BatcomputerVoiceStyler(enabled=True)
        self.voice_adapter = VoiceInputAdapter(assistant, voice_styler=self.voice_styler)
        self.gps_adapter = GPSEventAdapter(assistant)
        self.camera_adapter = CameraEventAdapter(assistant)
        self.boot_time = datetime.now(UTC).isoformat()
        self.relay_id = f"relay-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"

    def ingest_voice(self, event: VoiceEvent) -> RelayResponse:
        return self.voice_adapter.ingest(event)

    def ingest_gps(self, event: GPSEvent) -> RelayResponse:
        return self.gps_adapter.ingest(event)

    def ingest_camera(self, event: CameraEvent) -> RelayResponse:
        return self.camera_adapter.ingest(event)

    def bridge_status(self) -> Dict[str, Any]:
        """Return bridge diagnostics and last known telemetry snapshots."""
        return {
            "relay_id": self.relay_id,
            "boot_time": self.boot_time,
            "city": self.assistant.config.city_name,
            "voice": {
                "voice_id": self.voice_styler.voice_id,
                "batcomputer_enabled": self.voice_styler.enabled,
                "last_raw_transcript": self.voice_adapter.last_raw_transcript,
            },
            "gps": asdict(self.gps_adapter.last_gps) if self.gps_adapter.last_gps else None,
            "camera": (
                asdict(self.camera_adapter.last_camera)
                if self.camera_adapter.last_camera
                else None
            ),
            "assistant": {
                "mode": self.assistant.mode.value,
                "profile_id": self.assistant.active_profile_id,
                "objective": self.assistant.objective,
                "session_id": self.assistant.session_id,
            },
        }

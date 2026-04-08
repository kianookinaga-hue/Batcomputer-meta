from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, Optional


def _safe_dict(value: Optional[Any]) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}


@dataclass
class VoiceEvent:
    """Voice transcript event from the phone relay."""

    transcript: str
    device_id: str = "rayban-glasses"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    source: str = "phone-mic"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GPSEvent:
    """Live GPS telemetry from paired phone."""

    latitude: float
    longitude: float
    speed_mps: float = 0.0
    heading_deg: float = 0.0
    accuracy_m: float = 0.0
    device_id: str = "paired-phone"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CameraEvent:
    """Camera scene metadata produced by phone or edge model."""

    scene: str
    confidence: float = 0.0
    labels: Dict[str, float] = field(default_factory=dict)
    device_id: str = "rayban-camera"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RelayResponse:
    """Uniform payload returned by phone relay API handlers."""

    ok: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


def parse_voice_payload(payload: Dict[str, Any]) -> VoiceEvent:
    """Parse raw JSON payload into VoiceEvent."""
    transcript = str(payload.get("transcript", "")).strip()
    return VoiceEvent(
        transcript=transcript,
        device_id=str(payload.get("device_id", "rayban-glasses")),
        source=str(payload.get("source", "phone-mic")),
        metadata=_safe_dict(payload.get("metadata")),
    )


def parse_gps_payload(payload: Dict[str, Any]) -> GPSEvent:
    """Parse raw JSON payload into GPSEvent."""
    return GPSEvent(
        latitude=float(payload.get("latitude")),
        longitude=float(payload.get("longitude")),
        speed_mps=float(payload.get("speed_mps", 0.0)),
        heading_deg=float(payload.get("heading_deg", 0.0)),
        accuracy_m=float(payload.get("accuracy_m", 0.0)),
        device_id=str(payload.get("device_id", "paired-phone")),
        metadata=_safe_dict(payload.get("metadata")),
    )


def parse_camera_payload(payload: Dict[str, Any]) -> CameraEvent:
    """Parse raw JSON payload into CameraEvent."""
    labels = payload.get("labels", {})
    if not isinstance(labels, dict):
        labels = {}
    return CameraEvent(
        scene=str(payload.get("scene", "unknown")).strip() or "unknown",
        confidence=float(payload.get("confidence", 0.0)),
        labels={str(k): float(v) for k, v in labels.items()},
        device_id=str(payload.get("device_id", "rayban-camera")),
        metadata=_safe_dict(payload.get("metadata")),
    )

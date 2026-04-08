from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, Optional

from src.data_logging.logger import DataLogger

from .config import DrifterAssistantConfig
from .models import AssistantResponse, OperationMode


class DrifterGlassesAssistant:
    """
    Batman-drifter style assistant controller for smart glasses workflows.

    This implementation focuses on:
    - voice command parsing
    - mode-aware responses
    - minimal safety filtering
    - optional integration with existing DataLogger
    """

    def __init__(
        self,
        config: Optional[DrifterAssistantConfig] = None,
        data_logger: Optional[DataLogger] = None,
    ) -> None:
        self.config = config or DrifterAssistantConfig()
        self.mode = OperationMode.RECON
        self.data_logger = data_logger if self.config.enable_logging else None
        self.session_id: Optional[str] = None
        self.driver_id: str = self.config.operator_name
        self.objective: str = self.config.default_objective

    def start_operation(self, session_id: Optional[str] = None) -> str:
        """Start a glasses operation session."""
        sid = session_id or f"op-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        self.session_id = sid
        if self.data_logger:
            self.data_logger.start_session(session_id=sid, driver_id=self.driver_id)
            self._log("operation_start", {"mode": self.mode.value})
        return sid

    def stop_operation(self) -> Dict[str, Any]:
        """Stop active operation and emit summary."""
        if not self.session_id:
            return {"status": "idle", "message": "No active operation session."}
        self._log("operation_stop", {"mode": self.mode.value})
        if self.data_logger:
            summary = self.data_logger.end_session(self.session_id)
        else:
            summary = {"session_id": self.session_id, "status": "completed"}
        self.session_id = None
        return summary

    def set_mode(self, mode: OperationMode) -> AssistantResponse:
        """Switch glasses runtime mode."""
        self.mode = mode
        response = AssistantResponse(
            spoken=f"Mode changed to {mode.value}.",
            hud=f"[MODE] {mode.value.upper()}",
            priority=2,
            actions=["mode_switch"],
            context={"voice_style": self.config.mode_voice_styles.get(mode.value, "neutral")},
        )
        self._log("mode_change", {"mode": mode.value, "response": asdict(response)})
        return response

    def handle_voice_command(self, command: str) -> AssistantResponse:
        """Parse and respond to operator commands."""
        text = command.strip()
        lowered = text.lower()

        blocked = self._blocked_term(lowered)
        if blocked:
            response = AssistantResponse(
                spoken=(
                    "Request denied. That command is outside legal and safety policy."
                ),
                hud="[SAFETY] Command blocked",
                priority=1,
                actions=["policy_block"],
                context={"blocked_term": blocked},
            )
            self._log("command_blocked", {"command": text, "blocked_term": blocked})
            return response

        if "mode" in lowered:
            maybe_mode = self._extract_mode(lowered)
            if maybe_mode:
                return self.set_mode(maybe_mode)

        if any(word in lowered for word in ("objective", "mission")):
            return self._respond_objective()

        if any(word in lowered for word in ("scan", "sweep", "analyze")):
            return self._respond_scan()

        if any(word in lowered for word in ("navigate", "route", "path")):
            return self._respond_navigation(lowered)

        if any(word in lowered for word in ("status", "report")):
            return self._respond_status()

        if any(word in lowered for word in ("call", "comms", "broadcast")):
            return self._respond_comms(lowered)

        response = AssistantResponse(
            spoken=(
                "Command acknowledged. Suggest saying scan, status, navigate, or set mode."
            ),
            hud="[READY] Awaiting directive",
            actions=["clarify_intent"],
            context={"command": text},
        )
        self._log("command_fallback", {"command": text, "response": asdict(response)})
        return response

    def set_objective(self, objective: str) -> AssistantResponse:
        """Update current mission objective."""
        self.objective = objective.strip() or self.objective
        response = AssistantResponse(
            spoken=f"Objective updated. {self.objective}",
            hud=f"[OBJ] {self.objective}",
            priority=2,
            actions=["objective_update"],
            context={"objective": self.objective},
        )
        self._log("objective_update", {"objective": self.objective})
        return response

    def _respond_objective(self) -> AssistantResponse:
        response = AssistantResponse(
            spoken=f"Current objective: {self.objective}",
            hud=f"[OBJECTIVE] {self.objective}",
            priority=2,
            actions=["objective_readout"],
        )
        self._log("objective_read", {"objective": self.objective})
        return response

    def _respond_scan(self) -> AssistantResponse:
        threat_level = self._mock_threat_assessment()
        response = AssistantResponse(
            spoken=(
                f"Scanning sector. Threat level {threat_level}. "
                "No immediate hostile signatures."
            ),
            hud=f"[SCAN] threat={threat_level} | lanes clear",
            actions=["camera_scan", "audio_filter", "thermal_check"],
            context={"threat_level": threat_level, "mode": self.mode.value},
        )
        self._log("scan", {"threat_level": threat_level})
        return response

    def _respond_navigation(self, lowered_command: str) -> AssistantResponse:
        destination = "safe waypoint"
        if "to " in lowered_command:
            destination = lowered_command.split("to ", 1)[1].strip() or destination
        destination = self._normalize_destination(destination)
        eta = self.config.local_waypoint_eta.get(destination, "11m")
        response = AssistantResponse(
            spoken=f"Route locked to {destination}. Estimated arrival {eta}.",
            hud=f"[NAV] {destination} | ETA {eta}",
            actions=["plot_route", "hazard_overlay"],
            context={"destination": destination, "eta": eta},
        )
        self._log("navigation", {"destination": destination, "eta": eta})
        return response

    def _respond_status(self) -> AssistantResponse:
        response = AssistantResponse(
            spoken=(
                f"Mode {self.mode.value}. Session "
                f"{self.session_id or 'not started'}. "
                f"Monitoring {self.config.city_name} corridors."
            ),
            hud=f"[STATUS] mode={self.mode.value} | session={self.session_id or 'idle'}",
            actions=["status_report"],
            context={
                "mode": self.mode.value,
                "session_id": self.session_id,
                "city": self.config.city_name,
            },
        )
        self._log("status", {"mode": self.mode.value, "session_id": self.session_id})
        return response

    def _respond_comms(self, lowered_command: str) -> AssistantResponse:
        target = "trusted channel"
        if "call " in lowered_command:
            target = lowered_command.split("call ", 1)[1].strip() or target
        response = AssistantResponse(
            spoken=f"Comms opened with {target}. Encrypted channel active.",
            hud=f"[COMMS] {target} | encrypted",
            actions=["open_channel", "noise_suppression"],
            context={"target": target},
        )
        self._log("comms", {"target": target})
        return response

    def _extract_mode(self, lowered_command: str) -> Optional[OperationMode]:
        for mode in OperationMode:
            if mode.value in lowered_command:
                return mode
        return None

    def _blocked_term(self, lowered_command: str) -> Optional[str]:
        for term in self.config.blocked_terms:
            if term in lowered_command:
                return term
        return None

    def _normalize_destination(self, destination: str) -> str:
        lowered = destination.lower()
        aliases = self.config.local_waypoint_aliases
        for key, value in aliases.items():
            if key in lowered:
                return value
        return destination

    def _mock_threat_assessment(self) -> str:
        # Lightweight deterministic mock for a no-dependency baseline.
        minute = datetime.utcnow().minute
        score = minute % 10
        if score <= 2:
            return "low"
        if score <= 6:
            return "elevated"
        return "high"

    def _log(self, event_type: str, data: Dict[str, Any]) -> None:
        if not self.data_logger:
            return
        self.data_logger.log_event(
            event_type=event_type,
            data=data,
            driver_id=self.driver_id,
            metadata={"assistant": self.config.codename, "city": self.config.city_name},
        )

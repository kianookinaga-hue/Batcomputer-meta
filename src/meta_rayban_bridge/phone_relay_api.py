from __future__ import annotations

import json
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

from src.drifter_glasses_assistant.config import DrifterAssistantConfig
from src.drifter_glasses_assistant.system import DrifterGlassesAssistant

from .batcomputer_voice import BatcomputerVoiceStyler
from .bridge import MetaRayBanBridge
from .models import parse_camera_payload, parse_gps_payload, parse_voice_payload


class PhoneRelayAPI:
    """
    Minimal phone relay HTTP API for Meta Ray-Ban bridge workflows.

    Endpoints:
    - POST /v1/voice   {"transcript": "..."}
    - POST /v1/gps     {"latitude": ..., "longitude": ..., "speed_mps": ...}
    - POST /v1/camera  {"scene": "...", "confidence": 0.9, "labels": {...}}
    - GET  /v1/status
    """

    def __init__(
        self,
        bridge: Optional[MetaRayBanBridge] = None,
        assistant: Optional[DrifterGlassesAssistant] = None,
    ) -> None:
        if bridge:
            self.bridge = bridge
        else:
            runtime_assistant = assistant or DrifterGlassesAssistant(
                config=DrifterAssistantConfig(enable_logging=False)
            )
            runtime_assistant.start_operation()
            self.bridge = MetaRayBanBridge(
                assistant=runtime_assistant,
                voice_styler=BatcomputerVoiceStyler(
                    enabled=True, voice_id="batcomputer-honolulu-v1"
                ),
            )

    def handle_request(
        self, method: str, path: str, payload: Optional[Dict[str, Any]]
    ) -> Tuple[int, Dict[str, Any]]:
        """Route HTTP request data to bridge handlers."""
        parsed = urlparse(path).path
        if method == "GET" and parsed == "/v1/status":
            return HTTPStatus.OK, {"ok": True, "data": self.bridge.bridge_status()}

        if method != "POST":
            return (
                HTTPStatus.METHOD_NOT_ALLOWED,
                {"ok": False, "error": "Only POST allowed for this endpoint."},
            )

        body = payload or {}

        try:
            if parsed == "/v1/voice":
                result = self.bridge.ingest_voice(parse_voice_payload(body))
                return HTTPStatus.OK, asdict(result)
            if parsed == "/v1/gps":
                result = self.bridge.ingest_gps(parse_gps_payload(body))
                return HTTPStatus.OK, asdict(result)
            if parsed == "/v1/camera":
                result = self.bridge.ingest_camera(parse_camera_payload(body))
                return HTTPStatus.OK, asdict(result)
        except (TypeError, ValueError) as exc:
            return HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)}

        return HTTPStatus.NOT_FOUND, {"ok": False, "error": "Endpoint not found."}

    def serve(self, host: str = "0.0.0.0", port: int = 8787) -> None:
        """Run threaded HTTP relay server."""
        relay = self

        class _RelayHandler(BaseHTTPRequestHandler):
            server_version = "MetaRayBanRelay/1.0"

            def do_GET(self) -> None:  # noqa: N802
                status, payload = relay.handle_request("GET", self.path, None)
                self._write_json(status, payload)

            def do_POST(self) -> None:  # noqa: N802
                content_length = int(self.headers.get("Content-Length", "0"))
                body_bytes = self.rfile.read(content_length) if content_length else b"{}"
                try:
                    payload = json.loads(body_bytes.decode("utf-8"))
                except json.JSONDecodeError:
                    self._write_json(
                        HTTPStatus.BAD_REQUEST,
                        {"ok": False, "error": "Invalid JSON body."},
                    )
                    return
                status, response = relay.handle_request("POST", self.path, payload)
                self._write_json(status, response)

            def log_message(self, *_args: Any) -> None:
                # Keep relay output quiet in cloud terminal sessions.
                return

            def _write_json(self, status: int, payload: Dict[str, Any]) -> None:
                data = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        server = ThreadingHTTPServer((host, port), _RelayHandler)
        print(f"[MetaRayBanRelay] Listening on http://{host}:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


def main() -> None:
    """Entrypoint for `python3 -m src.meta_rayban_bridge.phone_relay_api`."""
    api = PhoneRelayAPI()
    api.serve()


if __name__ == "__main__":
    main()

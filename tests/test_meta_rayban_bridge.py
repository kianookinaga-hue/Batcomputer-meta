import unittest

from src.drifter_glasses_assistant.config import DrifterAssistantConfig
from src.drifter_glasses_assistant.models import AssistantResponse
from src.drifter_glasses_assistant.system import DrifterGlassesAssistant
from src.meta_rayban_bridge.batcomputer_voice import BatcomputerVoiceStyler
from src.meta_rayban_bridge.bridge import MetaRayBanBridge
from src.meta_rayban_bridge.models import CameraEvent, GPSEvent, VoiceEvent
from src.meta_rayban_bridge.phone_relay_api import PhoneRelayAPI


class TestMetaRayBanBridge(unittest.TestCase):
    def _assistant(self) -> DrifterGlassesAssistant:
        return DrifterGlassesAssistant(
            config=DrifterAssistantConfig(enable_logging=False)
        )

    def test_batcomputer_voice_styler_transforms_output(self):
        styler = BatcomputerVoiceStyler(enabled=True, voice_id="batcomputer-test")
        response = AssistantResponse(
            spoken="Route locked to Waikiki. Estimated arrival 8m.",
            hud="[NAV] Waikiki | ETA 8m",
            priority=2,
        )
        spoken, ssml = styler.stylize(response)
        self.assertTrue(spoken.startswith("Acknowledged."))
        self.assertIn("Route confirmed to Waikiki", spoken)
        self.assertIn("batcomputer", ssml)

    def test_voice_adapter_adds_batcomputer_fields(self):
        assistant = self._assistant()
        bridge = MetaRayBanBridge(
            assistant=assistant,
            voice_styler=BatcomputerVoiceStyler(enabled=True, voice_id="bat-vtest"),
        )
        result = bridge.ingest_voice(VoiceEvent(transcript="status"))
        self.assertTrue(result.ok)
        self.assertEqual(result.message, "Voice command processed.")
        self.assertEqual(result.data["voice_id"], "bat-vtest")
        self.assertIn("spoken_batcomputer", result.data)
        self.assertTrue(result.data["spoken_batcomputer"].startswith("Operator."))

    def test_gps_high_speed_generates_status_refresh(self):
        assistant = self._assistant()
        bridge = MetaRayBanBridge(assistant=assistant)
        result = bridge.ingest_gps(
            GPSEvent(
                latitude=21.3069,
                longitude=-157.8583,
                speed_mps=20.0,
                heading_deg=145.0,
            )
        )
        self.assertTrue(result.ok)
        self.assertIn("high-speed status refresh", result.message.lower())
        self.assertEqual(result.data["speed_kph"], 72)
        self.assertIn("status_report", result.data["actions"])

    def test_camera_hazard_scene_triggers_proactive_scan(self):
        assistant = self._assistant()
        bridge = MetaRayBanBridge(assistant=assistant)
        result = bridge.ingest_camera(
            CameraEvent(
                scene="traffic incident near ala moana",
                confidence=0.91,
                labels={"traffic": 0.91, "incident": 0.88},
            )
        )
        self.assertTrue(result.ok)
        self.assertIn("proactive scan generated", result.message.lower())
        self.assertIn("camera_scan", result.data["actions"])
        self.assertIn("camera_context", result.data)

    def test_phone_relay_api_routes_events(self):
        assistant = self._assistant()
        api = PhoneRelayAPI(assistant=assistant)

        status_code, payload = api.handle_request("GET", "/v1/status", None)
        self.assertEqual(status_code, 200)
        self.assertTrue(payload["ok"])

        voice_code, voice_payload = api.handle_request(
            "POST",
            "/v1/voice",
            {"transcript": "profile windward daytime"},
        )
        self.assertEqual(voice_code, 200)
        self.assertTrue(voice_payload["ok"])
        self.assertEqual(
            voice_payload["data"]["context"]["profile_id"], "windward-daytime"
        )

        missing_code, _ = api.handle_request("POST", "/v1/gps", {})
        self.assertEqual(missing_code, 400)

        not_found_code, _ = api.handle_request("POST", "/v1/unknown", {})
        self.assertEqual(not_found_code, 404)


if __name__ == "__main__":
    unittest.main()

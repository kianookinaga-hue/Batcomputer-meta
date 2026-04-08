from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class OperationProfilePack:
    """Island profile settings that tune routing and scanning behavior."""

    display_name: str
    description: str
    scan_focus: str
    eta_multiplier: float
    threat_bias: int
    recommended_mode: str


@dataclass
class DrifterAssistantConfig:
    """
    Runtime config for the drifter glasses assistant.

    The persona is intentionally cinematic and concise while keeping responses
    operational and safety-aware.
    """

    codename: str = "Night Drift Honolulu"
    city_name: str = "Honolulu, Hawaii"
    operator_name: str = "Drifter Oahu"
    wake_phrase: str = "Hey Sentinel"
    enable_logging: bool = True
    max_response_words: int = 40
    default_objective: str = "Maintain safety awareness across Honolulu corridors."
    default_profile: str = "waikiki-nightlife"
    local_waypoint_aliases: Dict[str, str] = field(
        default_factory=lambda: {
            "waikiki": "Waikiki",
            "ala moana": "Ala Moana Center",
            "kakaako": "Kakaako",
            "downtown": "Downtown Honolulu",
            "chinatown": "Chinatown Honolulu",
            "harbor": "Honolulu Harbor",
            "honolulu harbor": "Honolulu Harbor",
            "airport": "Daniel K. Inouye International Airport",
            "hnl": "Daniel K. Inouye International Airport",
            "diamond head": "Diamond Head",
            "manoa": "Manoa Valley",
        }
    )
    local_waypoint_eta: Dict[str, str] = field(
        default_factory=lambda: {
            "Waikiki": "8m",
            "Ala Moana Center": "6m",
            "Kakaako": "7m",
            "Downtown Honolulu": "9m",
            "Chinatown Honolulu": "10m",
            "Honolulu Harbor": "12m",
            "Daniel K. Inouye International Airport": "18m",
            "Diamond Head": "14m",
            "Manoa Valley": "16m",
        }
    )
    profile_aliases: Dict[str, str] = field(
        default_factory=lambda: {
            "waikiki-nightlife": "waikiki-nightlife",
            "waikiki nightlife": "waikiki-nightlife",
            "waikiki": "waikiki-nightlife",
            "windward-daytime": "windward-daytime",
            "windward daytime": "windward-daytime",
            "windward": "windward-daytime",
            "north-shore-weather-watch": "north-shore-weather-watch",
            "north shore weather watch": "north-shore-weather-watch",
            "north shore": "north-shore-weather-watch",
        }
    )
    profile_packs: Dict[str, OperationProfilePack] = field(
        default_factory=lambda: {
            "waikiki-nightlife": OperationProfilePack(
                display_name="Waikiki Nightlife",
                description="Crowd-dense evening profile tuned for nightlife corridors.",
                scan_focus="crosswalk flow, rideshare choke points, nightlife crowd density",
                eta_multiplier=1.20,
                threat_bias=1,
                recommended_mode="stealth",
            ),
            "windward-daytime": OperationProfilePack(
                display_name="Windward Daytime",
                description="Daylight profile for calmer neighborhoods and school zones.",
                scan_focus="pedestrian safety, school-zone speed, rain-slick road surfaces",
                eta_multiplier=1.05,
                threat_bias=-1,
                recommended_mode="recon",
            ),
            "north-shore-weather-watch": OperationProfilePack(
                display_name="North Shore Weather Watch",
                description="Weather-heavy profile for highway visibility and surf traffic.",
                scan_focus="flooding risk, wind gust lanes, visibility and road shoulder hazards",
                eta_multiplier=1.30,
                threat_bias=1,
                recommended_mode="analysis",
            ),
        }
    )
    blocked_terms: List[str] = field(
        default_factory=lambda: [
            "harm civilian",
            "bypass law enforcement",
            "illegal weapon",
            "dox",
            "stalker mode",
        ]
    )
    mode_voice_styles: Dict[str, str] = field(
        default_factory=lambda: {
            "stealth": "low-volume, concise, directional",
            "recon": "informational, scan-first",
            "transit": "route-focused, time-aware",
            "analysis": "detail-rich, threat-ranked",
            "emergency": "direct, loud, actionable",
        }
    )

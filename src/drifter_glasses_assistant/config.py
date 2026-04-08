from dataclasses import dataclass, field
from typing import Dict, List


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

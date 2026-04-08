from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DrifterAssistantConfig:
    """
    Runtime config for the drifter glasses assistant.

    The persona is intentionally cinematic and concise while keeping responses
    operational and safety-aware.
    """

    codename: str = "Night Drift"
    city_name: str = "Gotham Sector"
    operator_name: str = "Drifter"
    wake_phrase: str = "Hey Sentinel"
    enable_logging: bool = True
    max_response_words: int = 40
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

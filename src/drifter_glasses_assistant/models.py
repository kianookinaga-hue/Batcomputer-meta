from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class OperationMode(str, Enum):
    """Operational mode for the glasses assistant."""

    STEALTH = "stealth"
    RECON = "recon"
    TRANSIT = "transit"
    ANALYSIS = "analysis"
    EMERGENCY = "emergency"


@dataclass
class AssistantResponse:
    """Structured response payload from assistant."""

    spoken: str
    hud: str
    priority: int = 3
    actions: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

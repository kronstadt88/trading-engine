from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from trading_engine.market.models import Direction


@dataclass
class MarketEvent:
    event_type: str
    asset: str
    timeframe: str
    timestamp: datetime
    direction: Direction
    price: float
    confidence: float | None = None
    reasons: list[str] | None = None
    related_structure_id: str | None = None


@dataclass
class StartCandidate(MarketEvent):
    orientation: str = "NEEDS_VISUAL_GROUND_TRUTH"  # front | back | unresolved
    level_price: float | None = None
    end_price: float | None = None
    known_at: datetime | None = None
    related_sota_id: str | None = None
    evidence: dict[str, object] = field(default_factory=dict)
    definition_status: str = "NEEDS_VISUAL_GROUND_TRUTH"

    def __post_init__(self):
        if self.orientation not in {"front", "back", "NEEDS_VISUAL_GROUND_TRUTH"}:
            raise ValueError("Explicit front/back or unresolved orientation required")

from __future__ import annotations

from dataclasses import dataclass
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
    orientation: str | None = None  # "front" | "back"
    level_price: float | None = None

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Direction(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None


@dataclass(frozen=True)
class Swing:
    timestamp: datetime
    price: float
    kind: str  # "high" | "low"
    index: int


@dataclass(frozen=True)
class Leg:
    start: Swing
    end: Swing

    @property
    def magnitude(self) -> float:
        return abs(self.end.price - self.start.price)

    @property
    def bars(self) -> int:
        return abs(self.end.index - self.start.index)


@dataclass(frozen=True)
class Reaction:
    leg: Leg
    depth_ratio: float | None = None


@dataclass
class Structure:
    structure_type: str
    direction: Direction
    asset: str
    timeframe: str
    legs: list[Leg] = field(default_factory=list)
    reactions: list[Reaction] = field(default_factory=list)
    ratios: dict[str, float] = field(default_factory=dict)
    confidence: float | None = None
    reasons: list[str] = field(default_factory=list)
    parent_id: str | None = None
    child_ids: list[str] = field(default_factory=list)

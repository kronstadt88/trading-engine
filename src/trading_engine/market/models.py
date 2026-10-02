from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


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
    confirmed_at: datetime | None = None


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
    structure_id: str = field(default_factory=lambda: str(uuid4()))
    definition_status: str = "NEEDS_VISUAL_GROUND_TRUTH"
    ratio_tolerances: dict[str, float] = field(default_factory=dict)
    evolution: list[StructureRevision] = field(default_factory=list)


@dataclass(frozen=True)
class StructureRevision:
    structure_type: str
    known_at: datetime
    reasons: tuple[str, ...]

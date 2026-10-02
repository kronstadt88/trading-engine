from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LabelPoint:
    name: str
    timestamp: datetime
    price: float | None = None


@dataclass
class GroundTruthLabel:
    asset: str
    timeframe: str
    label_type: str
    direction: str | None
    points: list[LabelPoint] = field(default_factory=list)
    notes: str = ""
    valid: bool = True
    source_image: str | None = None

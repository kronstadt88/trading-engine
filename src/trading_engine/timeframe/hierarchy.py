from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeframeRelation:
    parent: str
    child: str


class TimeframeHierarchy:
    def __init__(self, relations: list[TimeframeRelation]):
        self.relations = relations

    def children_of(self, timeframe: str) -> list[str]:
        return [r.child for r in self.relations if r.parent == timeframe]

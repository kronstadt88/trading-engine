from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RatioMatch:
    target: float
    measured: float
    tolerance: float

    @property
    def deviation(self) -> float:
        return abs(self.measured - self.target)

    @property
    def matches(self) -> bool:
        return self.deviation <= self.tolerance


def classify_ratio(measured: float, tolerance_one: float = 0.20, tolerance_two: float = 0.35) -> str | None:
    """Classify an approximate structural ratio.

    '1' and '2' are families, not exact equalities.
    """
    candidates = [
        ("1", abs(measured - 1.0), tolerance_one),
        ("2", abs(measured - 2.0), tolerance_two),
    ]
    valid = [(name, dev) for name, dev, tol in candidates if dev <= tol]
    return min(valid, key=lambda x: x[1])[0] if valid else None

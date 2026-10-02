from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

from .models import Swing


@dataclass(frozen=True)
class SwingConfig:
    mode: str = "window"
    window: int = 3
    min_move_pct: float | None = None
    atr_multiple: float | None = None


def detect_swings(df: pd.DataFrame, config: SwingConfig) -> list[Swing]:
    """Baseline pluggable swing detector.

    This is intentionally simple. It is a representation layer, not the trading methodology.
    Future detectors may use ATR, percentage thresholds, volatility adaptation or fractals.
    """
    if config.mode != "window":
        raise NotImplementedError(f"Unsupported swing mode: {config.mode}")
    w = config.window
    if w < 1:
        raise ValueError("window must be >= 1")
    swings: list[Swing] = []
    highs = df["high"]
    lows = df["low"]
    for i in range(w, len(df) - w):
        if highs.iloc[i] >= highs.iloc[i - w:i + w + 1].max():
            swings.append(Swing(df["timestamp"].iloc[i].to_pydatetime(), float(highs.iloc[i]), "high", i))
        if lows.iloc[i] <= lows.iloc[i - w:i + w + 1].min():
            swings.append(Swing(df["timestamp"].iloc[i].to_pydatetime(), float(lows.iloc[i]), "low", i))
    return sorted(swings, key=lambda s: (s.index, 0 if s.kind == "low" else 1))

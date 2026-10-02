"""Generic geometric proposals, never structural-family or trade detectors."""

from dataclasses import dataclass
from typing import Callable

import pandas as pd

from .loaders import validate_ohlcv
from .models import Swing


@dataclass(frozen=True)
class SwingConfig:
    mode: str = "window"
    window: int = 3
    ties: str = "strict"  # strict, first, last, all
    min_move_pct: float | None = None
    atr_multiple: float | None = None


SwingDetector = Callable[[pd.DataFrame, SwingConfig], list[Swing]]


def window_swings(df: pd.DataFrame, config: SwingConfig) -> list[Swing]:
    if type(config.window) is not int or config.window < 1:
        raise ValueError("window must be a positive integer")
    if config.ties not in {"strict", "first", "last", "all"}:
        raise ValueError("Unknown tie policy")
    if config.min_move_pct is not None or config.atr_multiple is not None:
        raise ValueError("Window detector does not implement percentage/ATR filters")
    w, result = config.window, []
    for i in range(w, len(df) - w):
        for kind, column, extreme in (("low", "low", min), ("high", "high", max)):
            values = df[column].iloc[i - w : i + w + 1].tolist()
            if values[w] != extreme(values):
                continue
            equal = [j for j, value in enumerate(values) if value == values[w]]
            if config.ties == "strict" and len(equal) > 1:
                continue
            if config.ties == "first" and equal[0] != w:
                continue
            if config.ties == "last" and equal[-1] != w:
                continue
            result.append(
                Swing(
                    df.timestamp.iloc[i].to_pydatetime(),
                    float(values[w]),
                    kind,
                    i,
                    df.timestamp.iloc[i + w].to_pydatetime(),
                )
            )
    return result


class SwingRegistry:
    def __init__(self):
        self._detectors: dict[str, SwingDetector] = {"window": window_swings}

    def register(self, name: str, detector: SwingDetector):
        if not name or name in self._detectors:
            raise ValueError("Detector name must be new and nonempty")
        self._detectors[name] = detector

    def detect(self, df: pd.DataFrame, config: SwingConfig) -> list[Swing]:
        if config.mode not in self._detectors:
            raise ValueError(f"Unknown swing detector: {config.mode}")
        return self._detectors[config.mode](validate_ohlcv(df), config)


def detect_swings(
    df: pd.DataFrame, config: SwingConfig, registry: SwingRegistry | None = None
) -> list[Swing]:
    return (registry or SwingRegistry()).detect(df, config)

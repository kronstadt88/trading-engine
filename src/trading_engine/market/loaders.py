from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np


REQUIRED_COLUMNS = {"timestamp", "open", "high", "low", "close"}


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required OHLC columns: {sorted(missing)}")
    return validate_ohlcv(df)


def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Check evidence without silently repairing or sorting it."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing or df.empty:
        raise ValueError(f"Empty data or missing OHLC columns: {sorted(missing)}")
    df = df.copy()
    times = [pd.Timestamp(value) for value in df["timestamp"]]
    if any(pd.isna(t) or t.tzinfo is None for t in times):
        raise ValueError("OHLC timestamps require explicit timezone offsets")
    df["timestamp"] = pd.to_datetime(times, utc=True)
    if df.timestamp.duplicated().any() or not df.timestamp.is_monotonic_increasing:
        raise ValueError("OHLC timestamps must be unique and ordered")
    for column in ("open", "high", "low", "close"):
        df[column] = pd.to_numeric(df[column], errors="raise")
        if not np.isfinite(df[column]).all():
            raise ValueError("OHLC prices must be finite")
    if (
        (df.high < df[["open", "close", "low"]].max(axis=1))
        | (df.low > df[["open", "close", "high"]].min(axis=1))
    ).any():
        raise ValueError("Inconsistent candle bounds")
    if "volume" in df:
        df["volume"] = pd.to_numeric(df.volume, errors="raise")
        present = df.volume.dropna()
        if not np.isfinite(present).all() or (present < 0).any():
            raise ValueError("Volume must be missing or finite and nonnegative")
    return df.reset_index(drop=True)

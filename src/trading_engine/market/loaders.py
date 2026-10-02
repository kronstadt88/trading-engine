from __future__ import annotations

from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = {"timestamp", "open", "high", "low", "close"}


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required OHLC columns: {sorted(missing)}")
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)

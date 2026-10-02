from pathlib import Path
import pandas as pd

from trading_engine.market.loaders import load_ohlcv_csv


def test_load_ohlcv_csv(tmp_path: Path):
    path = tmp_path / "sample.csv"
    pd.DataFrame([
        {"timestamp":"2026-01-01T00:00:00Z","open":1,"high":2,"low":0.5,"close":1.5,"volume":10}
    ]).to_csv(path, index=False)
    df = load_ohlcv_csv(path)
    assert list(df.columns)[:5] == ["timestamp","open","high","low","close"]

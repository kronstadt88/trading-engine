import copy
from pathlib import Path

import pytest

from trading_engine.labels.bundle import load_bundle, validate_bundle, save_bundle
from trading_engine.market.loaders import validate_ohlcv
from trading_engine.market.swings import SwingConfig, SwingRegistry, detect_swings
from trading_engine.evaluation import Decision, evaluate

FIXTURE = Path(__file__).parents[1] / "fixtures" / "synthetic" / "labels.json"


def test_bundle_roundtrip(tmp_path):
    import shutil

    shutil.copytree(FIXTURE.parent, tmp_path / "bundle")
    path = tmp_path / "bundle" / "labels.json"
    bundle, frames = load_bundle(path)
    save_bundle(bundle, path)
    assert load_bundle(path)[0] == bundle
    assert len(frames["one"]) == 9


@pytest.mark.parametrize(
    "mutation", ["checksum", "point", "parent", "orientation", "known", "family"]
)
def test_broken_evidence_rejected(mutation):
    bundle, _ = load_bundle(FIXTURE)
    s = bundle["structures"][0]
    if mutation == "checksum":
        bundle["series"][0]["sha256"] = "incorrect"
    if mutation == "point":
        s["points"][0]["timestamp"] = "2026-01-01T00:01:30Z"
    if mutation == "parent":
        s["parent_id"] = s["id"]
    if mutation == "orientation":
        s["annotations"][0]["orientation"] = "breakout"
    if mutation == "known":
        s["known_at"] = s["start"]
    if mutation == "family":
        s["structure_type"] = "MACD"
    with pytest.raises(ValueError):
        validate_bundle(bundle, FIXTURE.parent)


def test_external_evidence_rejected():
    bundle, _ = load_bundle(FIXTURE)
    bundle["series"][0]["ohlcv"] = "../outside.csv"
    with pytest.raises(ValueError, match="inside"):
        validate_bundle(bundle, FIXTURE.parent)


@pytest.mark.parametrize("mutation", ["naive", "duplicate", "nan", "bounds", "volume", "order"])
def test_bad_candles_rejected(mutation):
    _, frames = load_bundle(FIXTURE)
    df = frames["one"].copy()
    if mutation == "naive":
        df["timestamp"] = df.timestamp.dt.tz_localize(None)
    if mutation == "duplicate":
        df.loc[1, "timestamp"] = df.timestamp.iloc[0]
    if mutation == "nan":
        df.loc[0, "high"] = float("nan")
    if mutation == "bounds":
        df.loc[0, "high"] = -1
    if mutation == "volume":
        df.loc[0, "volume"] = -1
    if mutation == "order":
        df = df.iloc[::-1]
    with pytest.raises(ValueError):
        validate_ohlcv(df)


def test_swings_symmetry_and_confirmation():
    _, frames = load_bundle(FIXTURE)
    df = frames["one"]
    mirrored = df.copy()
    mirrored["open"], mirrored["close"] = -df.open, -df.close
    mirrored["high"], mirrored["low"] = -df.low, -df.high
    a = detect_swings(df, SwingConfig(window=1))
    b = detect_swings(mirrored, SwingConfig(window=1))
    assert {(s.index, s.price, s.kind) for s in a} == {
        (s.index, -s.price, "low" if s.kind == "high" else "high") for s in b
    }
    for s in a:
        assert s.confirmed_at == df.timestamp.iloc[s.index + 1]
    partial = detect_swings(df.iloc[:5], SwingConfig(window=1))
    assert all(s.index <= 3 for s in partial)


def test_plugins_and_unsupported_parameters():
    _, frames = load_bundle(FIXTURE)
    registry = SwingRegistry()
    registry.register("manual", lambda df, cfg: [])
    assert detect_swings(frames["one"], SwingConfig(mode="manual"), registry) == []
    with pytest.raises(ValueError):
        registry.register("manual", lambda df, cfg: [])
    with pytest.raises(ValueError):
        detect_swings(frames["one"], SwingConfig(atr_multiple=2))
    with pytest.raises(ValueError):
        detect_swings(frames["one"], SwingConfig(window=0))


def test_metrics_and_synthetic_gate():
    bundle, _ = load_bundle(FIXTURE)
    with pytest.raises(ValueError):
        evaluate(bundle, [])
    template = bundle["structures"][0]
    bundle["structures"] = []
    for sid, status in [
        ("a", "valid"),
        ("b", "valid"),
        ("c", "invalid"),
        ("d", "invalid"),
        ("e", "ambiguous"),
    ]:
        s = copy.deepcopy(template)
        s.update(id=sid, classification=status)
        bundle["structures"].append(s)
    decisions = [Decision(sid, True, ("test",)) for sid in ["a", "c", "e"]]
    report = evaluate(bundle, decisions, allow_synthetic=True)
    assert report["precision"] == report["recall"] == 0.5
    assert report["counts"] == dict(tp=1, fp=1, fn=1, tn=1, excluded=1)
    assert report["examples"]["fn"] == ["b"]
    with pytest.raises(ValueError):
        evaluate(bundle, decisions + decisions, allow_synthetic=True)
    with pytest.raises(ValueError):
        evaluate(bundle, [Decision("unknown", True, ("x",))], allow_synthetic=True)
    empty = evaluate(dict(bundle, structures=[]), [], allow_synthetic=True)
    assert empty["precision"] is None and empty["recall"] is None


def test_inspection_and_asof(tmp_path):
    from trading_engine.inspection import build_figure, write_inspection

    bundle, frames = load_bundle(FIXTURE)
    figure = build_figure(bundle, frames)
    assert figure.data[0].type == "candlestick"
    assert len(figure.data) == 4
    past = build_figure(bundle, frames, "2026-01-01T00:04:00Z")
    assert len(past.data) == 1
    assert len(past.data[0].x) == 5
    target = tmp_path / "inspection.html"
    write_inspection(FIXTURE, target)
    assert 'alt="Source chart"' in target.read_text(encoding="utf-8")
    write_inspection(FIXTURE, target, "2026-01-01T00:04:00Z")
    assert 'alt="Source chart"' not in target.read_text(encoding="utf-8")


def test_plateau_policy_and_parent_cycle():
    bundle, frames = load_bundle(FIXTURE)
    flat = frames["one"].copy()
    flat[["open", "high", "low", "close"]] = [10, 11, 9, 10]
    assert detect_swings(flat, SwingConfig(window=1)) == []
    assert len(detect_swings(flat, SwingConfig(window=1, ties="all"))) == 14
    second = copy.deepcopy(bundle["structures"][0])
    second["id"] = "second"
    second["parent_id"] = "fixture-1"
    bundle["structures"][0]["parent_id"] = "second"
    bundle["structures"].append(second)
    with pytest.raises(ValueError, match="cycle"):
        validate_bundle(bundle, FIXTURE.parent)


def test_evolution_keeps_identity():
    bundle, _ = load_bundle(FIXTURE)
    s = bundle["structures"][0]
    s["structure_type"] = "122"
    s["evolution"] = [
        {"structure_type": "121", "known_at": s["start"], "notes": "synthetic metadata only"},
        {"structure_type": "122", "known_at": s["known_at"], "notes": "synthetic metadata only"},
    ]
    validate_bundle(bundle, FIXTURE.parent)
    s["evolution"].reverse()
    with pytest.raises(ValueError):
        validate_bundle(bundle, FIXTURE.parent)


def test_multitimeframe_view():
    from trading_engine.inspection import build_figure

    bundle, frames = load_bundle(FIXTURE)
    series = copy.deepcopy(bundle["series"][0])
    series.update(id="child-series", timeframe="lower-timeframe-unresolved")
    bundle["series"].append(series)
    image = copy.deepcopy(bundle["images"][0])
    image.update(id="child-chart", series_id="child-series")
    bundle["images"].append(image)
    child = copy.deepcopy(bundle["structures"][0])
    child.update(
        id="child",
        series_id="child-series",
        parent_id="fixture-1",
        context_relation="contained",
        image_ids=["child-chart"],
    )
    bundle["structures"].append(child)
    frames = validate_bundle(bundle, FIXTURE.parent)
    fig = build_figure(bundle, frames)
    assert [trace.type for trace in fig.data].count("candlestick") == 2
    assert fig.data[4].xaxis == "x2"

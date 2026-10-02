# Ground-truth bundle v1 and workflow

Use one directory per reviewed case, with `labels.json`, chart PNG/JPEG and OHLCV
CSV. Paths are relative to that directory and cannot escape it. Multiple images and
series can coexist; use series IDs and stable structure IDs for timeframe context.
The authoritative executable validator is `labels/bundle.py`. A fully populated,
intentionally **synthetic and ambiguous** example lives in `tests/fixtures/synthetic`.
Never use this fixture as an example of 111, 121, 122 or an operational concept.

## Commands (PowerShell, from repository root)

```powershell
python -m pip install -e '.[dev]'
python -m trading_engine init --image chart.png --ohlcv bars.csv --asset DAX --timeframe 5m --source 'IBKR export; contract/session/adjustment details' --annotator 'your-name' --bar-timestamp close --output data/labelled/dax_001
python -m trading_engine validate data/labelled/dax_001/labels.json
python -m trading_engine inspect data/labelled/dax_001/labels.json --output inspection.html
python -m trading_engine inspect data/labelled/dax_001/labels.json --as-of 2026-01-01T12:00:00Z --output past.html
```

`init` copies original evidence, calculates SHA-256 checksums and creates an
ambiguous placeholder. Edit the JSON manually; the Plotly viewer is an inspection
tool, not a point-dragging editor. Validate and regenerate after each edit.
The HTML embeds Plotly and images for offline viewing. Treat it as containing the
same potentially private evidence as the source bundle.

## Fields

- Root: schema_version=1, stable id, evidence_kind=human/synthetic, annotator,
  labelled_at with timezone, notes, series, images, structures.
- Series: id, asset, timeframe, source, timezone, bar_timestamp=open/close,
  ohlcv relative path, sha256. CSV requires timestamp,open,high,low,close;
  volume is optional/nullable. All timestamps must carry offsets. Loader normalizes UTC.
- Images: id, series_id, path, sha256. Human reviewer must check image matches the
  asset, period, timezone, adjustment and timeframe represented by the candles.
- Structure: id, series_id, structure_type (111/112/121/122/21X or unresolved marker),
  direction (bullish/bearish or unresolved), classification (valid/invalid/ambiguous),
  definition_status=NEEDS_VISUAL_GROUND_TRUTH, start, end, known_at, image_ids, notes.
- Points: id, timestamp of an actual candle and finite price. Prices can represent
  derived levels; validator does not guess that every point is a high or low.
- Legs: explicit pairs of point IDs. No leg order or digit interpretation inferred.
- Annotations: concept=Sota/Caballo/Rey/arranque/absorption, point_ids, status
  (candidate/confirmed/invalid/NEEDS_VISUAL_GROUND_TRUTH), known_at, notes.
  Caballo and arranque require orientation=front/back/NEEDS_VISUAL_GROUND_TRUTH.
  Additional measured evidence, price levels, reasons and related IDs can be preserved
  as extra JSON fields. They are not interpreted as detector rules.
- parent_id: null or another structure in this bundle. context_relation is contained,
  overlap, subsequent or unresolved. Asset consistency and relation geometry are checked.
- evolution: ordered records with structure_type, known_at and notes. Latest family
  equals the snapshot family; history records do not imply invented transition rules.

`known_at` is when the complete current snapshot was knowable, not the time of its
first pivot. For earlier stages, preserve a separate historical bundle/snapshot;
`--as-of` hides the entire later snapshot rather than reconstructing old geometry.
It also hides source images and full notes. For bars timestamped at open, the caller
must use a cutoff containing only completed bars; the tool does not infer exchange
sessions or bar-close times. Swing `confirmed_at` is the timestamp of the confirming
bar and becomes usable only after that bar has completed.

## Evaluation protocol

Create decisions JSON, e.g. `[{"example_id":"case-1","predicted_valid":true,
"reasons":["experimental model version/config and measured evidence"]}]`, then:

```powershell
python -m trading_engine evaluate data/labelled/dax_001/labels.json --decisions decisions.json --output metrics.json
```

This first protocol evaluates **adjudicated candidates**, not full-chart object
localization or trading returns. Decision IDs must map to reviewed candidate IDs.
A valid candidate without a positive decision is FN; an invalid candidate with a
positive decision is FP. Ambiguous cases are excluded. Unlabelled predictions must
be adjudicated as new examples first; unknown IDs and duplicate decisions raise.
Undefined precision/recall are null, never misleading zero or one. Reports retain
FP/FN IDs and decision reasons. `--allow-synthetic` is only for software smoke tests.

Split future training/calibration/test datasets by instrument/time period and group
related parent/child/evolution snapshots together to avoid leakage. Keep a frozen
held-out human corpus. Event-level matching tolerances and continuous-scan coverage
must be agreed with the methodology owner before claiming detection accuracy.

## Swing plugins

`SwingRegistry.register(name, callable)` accepts `(validated_dataframe, SwingConfig)`
and returns `list[Swing]`; pass the registry to `detect_swings`. Baseline `window`
uses symmetric high/low extrema and window bars on both sides. Plateau policy is
strict (default), first, last or all. It may propose both high and low on one candle;
it does not infer intrabar ordering or enforce alternating structural legs.
Percentage/ATR parameters are rejected by this baseline rather than ignored.
Plugins are trusted code responsible for their own configuration and confirmation
semantics; none is a definition of the user's structural language.

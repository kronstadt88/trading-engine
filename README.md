# trading-engine

Research and detection engine for a custom market-structure methodology based on structural families such as 111/112/121/122/21X, multi-timeframe fractality, and the operational concepts Sota, Caballo and Rey.

This repository is intentionally focused first on **detection, validation and visualization**. Automated order execution is out of scope until the detection model is demonstrably reliable.

See `CODEX_INSTRUCTIONS.md` and `docs/` for the methodology and implementation plan.

## Research foundation

Start with [the audit](docs/11-research-audit.md) and
[the labelling workflow](docs/12-ground-truth-workflow.md).

```powershell
python -m pip install -e '.[dev]'
python -m pytest
python -m trading_engine inspect tests/fixtures/synthetic/labels.json --output inspection.html
```

The included synthetic example tests the tooling only. There is no validated
111/112/121/122 detector, no live IBKR adapter and no automated order execution.

# Codex instructions

This repository formalizes a custom discretionary market-structure methodology.

## Non-negotiable rules

1. Do not replace domain concepts with RSI, MACD, moving averages or generic breakout logic.
2. Do not invent definitions for ambiguous concepts. Mark them as `NEEDS_VISUAL_GROUND_TRUTH`.
3. Build incrementally: data model -> swing representation -> labels -> visualization -> detector -> evaluation.
4. Every detector must expose *why* it fired, including measured ratios, tolerances and related structural points.
5. Bullish and bearish logic must be symmetric.
6. Multi-timeframe relations are first-class. Do not treat each timeframe as an isolated scanner.
7. Automated execution is out of scope until detection is validated.
8. Prefer configuration and measurable tolerances over hard-coded exact ratios.
9. Preserve raw evidence. A confidence score may summarize a detection, but must never hide its reasons.
10. Positive and negative labelled examples are required before a concept is considered implemented.

## Domain layers

The intended layering is:

generic market geometry
-> 111/112/121/122/21X structural language
-> Sota / Caballo / Rey operational events
-> multi-timeframe state machine
-> alerts
-> only later, optional execution

## First implementation milestone

Create and test:
- OHLCV loading
- Candle / Swing / Leg / Reaction / Structure models
- configurable swing detection interface
- labelled ground-truth format
- visualization
- initial Arranque/Caballo candidate framework
- evaluation metrics for labelled examples

Do not claim the detector is valid merely because tests pass on synthetic data.

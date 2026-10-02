# Research foundation audit

Read scope: every tracked file at `0d85d2b` (feature/foundation), including all
12 methodology documents, domain modules, tests, configuration and data README.
No human-labelled image or OHLCV example was present. This milestone implements
research infrastructure; it does not validate any detector or trading strategy.

| Finding | Consequence / resolution |
| --- | --- |
| GroundTruthLabel used free strings, defaulted valid=True and linked only an image | New versioned bundle links immutable image/CSV hashes, explicit valid/invalid/ambiguous review, points and notes. Legacy class is retained only for compatibility. |
| Structures referred to parent IDs but had no own ID | Add structure_id, revision history and ratio tolerances. Bundle parents reference stable IDs with explicit temporal context, checked for cycles. |
| No distinction between geometry timestamp and recognition time | Add known_at for human snapshots and confirmed_at for swings. As-of viewer suppresses future snapshots. |
| Swing mode was a hard-coded branch; percentage/ATR settings silently ignored | Injectable registry; configurable window and plateau policy; unsupported baseline parameters now raise. |
| Window detector reads future candles | Confirmation candle recorded. A pivot is not known on its own bar. |
| OHLC loader silently sorted and assumed timezone for naive timestamps | Reject unordered/duplicate/naive timestamps, non-finite prices and inconsistent candles; missing volume remains unknown. |
| Provisional ratio defaults look authoritative | Existing defaults retained for compatibility, explicitly uncalibrated. No structural classifier added. |
| Events lack operational evidence and explicit unknown orientation | Extend StartCandidate with unresolved orientation and evidence fields; no confirmation rule implemented. |
| State names imply confirmed concepts without transition rules | Keep enum descriptive only; no automatic transition engine. |
| No evaluation protocol or negative corpus | Add candidate-ID evaluation with explicit adjudication, ambiguous exclusion, missing-positive FN, and synthetic guard. Continuous scan matching remains unresolved. |

## Domain boundaries

Structural families and Sota/Caballo/Rey remain separate. Family evolution preserves
identity; it does not silently replace the previous observation. Multiple series
in one bundle represent explicit parent/child context across timeframes. No default
1H -> 5m mapping is inferred. Parent/child direction is recorded, not forced equal:
whether counter-directional children are allowed needs human evidence.

A label marked valid is the annotator's judgement about that example, not evidence
that the mathematical definition is closed. `definition_status` remains
`NEEDS_VISUAL_GROUND_TRUTH` throughout this milestone.

## Human visual ground truth still required

All items below are **NEEDS_VISUAL_GROUND_TRUTH**:

1. Each digit's meaning in 111/112/121/122; the scope and meaning of experimental 21X.
2. Which points and legs are structural; equivalent nearby swing interpretations,
   equal extremes, wick versus close and simultaneous high/low pivots.
3. Ratio denominators, contextual tolerance ranges and overlap between families.
4. Reaction semantics, duration importance, invalidation and boundary cases.
5. 121 -> 122 and other evolution rules, with the actual time each change became known.
6. Sota construction and its relationship to prior structural evidence.
7. Front/back arranque geometry, start/end points, confirmation and invalidation.
8. Caballo conditions distinct from a generic price break and its relation to Sota.
9. Rey conditions and the repeated process in a child timeframe.
10. Absorption geometry, role of volume/order flow and whether it is optional per setup.
11. Parent/child timeframe selection, inherited context, direction, timing and overlap.
12. Directional inversion versus literal 180-degree rotation (time reversal is not assumed).
13. Which visual differences are equivalent for event matching; detection time tolerance,
    duplicate detections and how to adjudicate previously unlabelled predictions.
14. Recover Gold, DAX, Thales, Natural Gas, Heineken and Euro examples, with negatives
    and ambiguous cases as well as positives. No historical example has been reconstructed.

## Data preparation for IBKR

No live broker connection or order execution is introduced. Supply an exported CSV
with explicit timezone offsets and instrument identity (including exchange/contract
where needed), bar timestamp convention, session, adjustment policy and data source.
Record these details in `source` and notes. Missing volume is not zero volume.
The timeframe and image/data correspondence require human verification; checksums
prove file identity, not the semantic correctness of an annotated chart.

# Detection state machine

Provisional operational state model:

STRUCTURE_DETECTED
-> SOTA_CANDIDATE
-> WAITING_FOR_START
-> CABALLO_CONFIRMED
-> DESCEND_TIMEFRAME
-> CHILD_STRUCTURE_DETECTED
-> CHILD_SOTA
-> CHILD_CABALLO
-> REY

This is deliberately explicit so the engine can say what is currently present and what is still missing.

For example:

- "121 detected, no Sota validated"
- "Sota candidate present, waiting for Caballo"
- "Caballo confirmed, inspect child timeframe"
- "child structure present, no Rey yet"

The precise transition conditions remain subject to labelled examples.

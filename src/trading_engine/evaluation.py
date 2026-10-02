"""Candidate-level evaluation on explicitly adjudicated examples."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    example_id: str
    predicted_valid: bool
    reasons: tuple[str, ...]


def evaluate(bundle, decisions: list[Decision], *, allow_synthetic=False):
    """Missing decisions on valid examples are FN; duplicates/unknown IDs are errors.

    Correspondence is an explicit human-reviewed example ID. No invented geometric
    tolerance and no assumption that an unlabelled region is negative.
    """
    if bundle["evidence_kind"] != "human" and not allow_synthetic:
        raise ValueError("Synthetic fixtures cannot validate the methodology")
    labels = {s["id"]: s for s in bundle["structures"]}
    if len(labels) != len(bundle["structures"]):
        raise ValueError("Duplicate label ID")
    predictions = {}
    for d in decisions:
        if d.example_id not in labels or d.example_id in predictions:
            raise ValueError("Unknown or duplicate decision ID")
        if type(d.predicted_valid) is not bool or not d.reasons:
            raise ValueError("Decisions require a boolean and explicit reasons")
        predictions[d.example_id] = d.predicted_valid
    buckets = {key: [] for key in ("tp", "fp", "fn", "tn", "excluded")}
    for sid, label in labels.items():
        if label["classification"] not in {"valid", "invalid", "ambiguous"}:
            raise ValueError("Unknown classification")
        if label["classification"] == "ambiguous":
            buckets["excluded"].append(sid)
            continue
        positive = label["classification"] == "valid"
        predicted = predictions.get(sid, False)
        key = ("tp" if positive else "fp") if predicted else ("fn" if positive else "tn")
        buckets[key].append(sid)
    tp, fp, fn = (len(buckets[key]) for key in ("tp", "fp", "fn"))
    return {
        "protocol": "adjudicated-candidate-id-v1",
        "evidence_kind": bundle["evidence_kind"],
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "counts": {key: len(value) for key, value in buckets.items()},
        "examples": buckets,
        "decisions": [
            {
                "example_id": d.example_id,
                "predicted_valid": d.predicted_valid,
                "reasons": list(d.reasons),
            }
            for d in decisions
        ],
    }

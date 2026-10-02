"""Versioned research evidence. Validation checks integrity, never methodology."""

from __future__ import annotations

import hashlib
import json
from zoneinfo import ZoneInfo
from pathlib import Path

import pandas as pd

from trading_engine.market.loaders import load_ohlcv_csv

UNRESOLVED = "NEEDS_VISUAL_GROUND_TRUTH"
FAMILIES = {"111", "112", "121", "122", "21X", UNRESOLVED}
DIRECTIONS = {"bullish", "bearish", UNRESOLVED}


def timestamp(value):
    result = pd.Timestamp(value)
    if pd.isna(result) or result.tzinfo is None:
        raise ValueError("Timestamps must include an explicit timezone")
    return result.tz_convert("UTC")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def evidence_path(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    require(path.is_relative_to(root), "Evidence must stay inside the bundle directory")
    require(path.is_file(), f"Missing evidence: {relative}")
    return path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_bundle(bundle, root):
    """Return validated candle frames keyed by series ID; fail on broken evidence."""
    require(bundle["schema_version"] == 1, "Unsupported schema version")
    require(bool(bundle["id"]), "Bundle ID required")
    require(bundle["evidence_kind"] in {"human", "synthetic"}, "Unknown evidence kind")
    require(bool(bundle["annotator"]), "Annotator required")
    timestamp(bundle["labelled_at"])
    require(isinstance(bundle["notes"], str), "Notes must be text")
    frames, series_by_id = {}, {}
    for series in bundle["series"]:
        sid = series["id"]
        require(sid not in frames, "Duplicate series ID")
        for key in ("asset", "timeframe", "source", "timezone", "bar_timestamp"):
            require(bool(series[key]), f"Series {key} required")
        ZoneInfo(series["timezone"])
        require(series["bar_timestamp"] in {"open", "close"}, "Specify bar timestamp convention")
        csv = evidence_path(root, series["ohlcv"])
        require(sha256(csv) == series["sha256"], "OHLCV checksum mismatch")
        frames[sid] = load_ohlcv_csv(csv)
        series_by_id[sid] = series
    require(bool(frames), "At least one OHLCV series required")
    image_ids = set()
    images_by_id = {}
    for image in bundle["images"]:
        require(image["id"] not in image_ids, "Duplicate image ID")
        image_ids.add(image["id"])
        images_by_id[image["id"]] = image
        require(image["series_id"] in frames, "Unknown image series")
        path = evidence_path(root, image["path"])
        require(path.suffix.lower() in {".png", ".jpg", ".jpeg"}, "Use PNG or JPEG evidence")
        require(sha256(path) == image["sha256"], "Image checksum mismatch")
    require(bool(image_ids), "Chart image required")
    structures = {s["id"]: s for s in bundle["structures"]}
    require(len(structures) == len(bundle["structures"]), "Duplicate structure ID")
    for s in structures.values():
        require(s["series_id"] in frames, "Unknown structure series")
        frame = frames[s["series_id"]]
        require(s["structure_type"] in FAMILIES, "Unknown structural family")
        require(s["direction"] in DIRECTIONS, "Unknown direction")
        require(s["classification"] in {"valid", "invalid", "ambiguous"}, "Unknown classification")
        require(s["definition_status"] == UNRESOLVED, "Methodology awaits visual ground truth")
        require(bool(s["notes"]), "Explain each classification")
        require(
            bool(s["image_ids"]) and set(s["image_ids"]) <= image_ids, "Image references required"
        )
        require(
            any(images_by_id[i]["series_id"] == s["series_id"] for i in s["image_ids"]),
            "Structure needs an image of its own series",
        )
        start, end, known = map(timestamp, (s["start"], s["end"], s["known_at"]))
        require(start <= end <= known, "Invalid structure interval / known_at")
        require(
            frame.timestamp.iloc[0] <= start <= end <= frame.timestamp.iloc[-1],
            "Structure outside supplied candles",
        )
        points = {p["id"]: p for p in s["points"]}
        require(len(points) == len(s["points"]), "Duplicate point ID")
        for p in points.values():
            t = timestamp(p["timestamp"])
            require(
                start <= t <= end and t in set(frame.timestamp), "Point must reference a candle"
            )
            require(
                isinstance(p["price"], (float, int))
                and pd.notna(p["price"])
                and abs(p["price"]) != float("inf"),
                "Finite point price required",
            )
        for leg in s["legs"]:
            require(len(leg) == 2 and set(leg) <= points.keys(), "Leg references unknown points")
        for a in s["annotations"]:
            require(bool(a["notes"]), "Annotation notes required")
            require(
                a["concept"] in {"Sota", "Caballo", "Rey", "arranque", "absorption"},
                "Unknown operational concept",
            )
            require(set(a["point_ids"]) <= points.keys(), "Unknown annotation points")
            require(
                a["status"] in {"candidate", "confirmed", "invalid", UNRESOLVED},
                "Unknown annotation status",
            )
            require(
                start <= timestamp(a["known_at"]) <= known,
                "Annotation recognition must be within snapshot",
            )
            if a["concept"] in {"arranque", "Caballo"}:
                require(
                    a["orientation"] in {"front", "back", UNRESOLVED},
                    "Explicit front/back or unresolved orientation required",
                )
        previous = None
        for revision in s["evolution"]:
            t = timestamp(revision["known_at"])
            require(
                start <= t <= known and (previous is None or previous < t),
                "Evolution must be ordered within snapshot",
            )
            require(revision["structure_type"] in FAMILIES, "Unknown evolution family")
            require(bool(revision["notes"]), "Explain evolution")
            previous = t
        if s["evolution"]:
            require(
                s["evolution"][-1]["structure_type"] == s["structure_type"],
                "Latest evolution must match snapshot family",
            )
        parent_id = s["parent_id"]
        if parent_id is not None:
            require(parent_id in structures and parent_id != s["id"], "Unknown/self parent")
            parent = structures[parent_id]
            require(
                series_by_id[parent["series_id"]]["asset"] == series_by_id[s["series_id"]]["asset"],
                "Parent and child assets differ",
            )
            require(
                s["context_relation"] in {"contained", "overlap", "subsequent", UNRESOLVED},
                "Explicit temporal context relation required",
            )
            ps, pe = timestamp(parent["start"]), timestamp(parent["end"])
            relation = s["context_relation"]
            require(relation != "contained" or ps <= start <= end <= pe, "Not contained")
            require(relation != "overlap" or max(ps, start) <= min(pe, end), "No overlap")
            require(relation != "subsequent" or start >= pe, "Not subsequent")
        visited, current = set(), s
        while current["parent_id"] is not None:
            require(current["id"] not in visited, "Parent cycle")
            visited.add(current["id"])
            require(current["parent_id"] in structures, "Unknown parent")
            current = structures[current["parent_id"]]
    return frames


def load_bundle(path):
    path = Path(path)
    bundle = json.loads(path.read_text(encoding="utf-8"))
    return bundle, validate_bundle(bundle, path.parent)


def save_bundle(bundle, path):
    path = Path(path)
    validate_bundle(bundle, path.parent)
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

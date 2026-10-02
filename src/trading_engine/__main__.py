"""Research commands: init, validate, inspect, evaluate. No trading commands."""

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from trading_engine.labels.bundle import UNRESOLVED, load_bundle, save_bundle, sha256
from trading_engine.market.loaders import load_ohlcv_csv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Copy chart and OHLCV into a new evidence bundle")
    for key in ("image", "ohlcv", "asset", "timeframe", "source", "annotator", "output"):
        init.add_argument(f"--{key}", required=True)
    init.add_argument("--bar-timestamp", choices=["open", "close"], required=True)
    for name in ("validate", "inspect", "evaluate"):
        command = commands.add_parser(name)
        command.add_argument("bundle")
        if name != "validate":
            command.add_argument("--output", required=True)
        if name == "inspect":
            command.add_argument("--as-of")
        if name == "evaluate":
            command.add_argument("--decisions", required=True)
            command.add_argument("--allow-synthetic", action="store_true")
    args = parser.parse_args()
    if args.command == "init":
        image, csv, target = Path(args.image), Path(args.ohlcv), Path(args.output)
        if image.suffix.lower() not in {".png", ".jpg", ".jpeg"} or not image.is_file():
            parser.error("Image must be an existing PNG/JPEG")
        df = load_ohlcv_csv(csv)
        target.mkdir(parents=True, exist_ok=False)
        image_name = "chart" + image.suffix.lower()
        shutil.copyfile(image, target / image_name)
        shutil.copyfile(csv, target / "ohlcv.csv")
        bundle = {
            "schema_version": 1,
            "id": target.name,
            "evidence_kind": "human",
            "annotator": args.annotator,
            "labelled_at": datetime.now(timezone.utc).isoformat(),
            "notes": UNRESOLVED,
            "series": [
                {
                    "id": "primary",
                    "asset": args.asset,
                    "timeframe": args.timeframe,
                    "source": args.source,
                    "timezone": "UTC",
                    "bar_timestamp": args.bar_timestamp,
                    "ohlcv": "ohlcv.csv",
                    "sha256": sha256(target / "ohlcv.csv"),
                }
            ],
            "images": [
                {
                    "id": "chart",
                    "series_id": "primary",
                    "path": image_name,
                    "sha256": sha256(target / image_name),
                }
            ],
            "structures": [
                {
                    "id": "example-1",
                    "series_id": "primary",
                    "structure_type": UNRESOLVED,
                    "direction": UNRESOLVED,
                    "classification": "ambiguous",
                    "definition_status": UNRESOLVED,
                    "start": df.timestamp.iloc[0].isoformat(),
                    "end": df.timestamp.iloc[-1].isoformat(),
                    "known_at": df.timestamp.iloc[-1].isoformat(),
                    "points": [],
                    "legs": [],
                    "annotations": [],
                    "evolution": [],
                    "parent_id": None,
                    "context_relation": UNRESOLVED,
                    "image_ids": ["chart"],
                    "notes": UNRESOLVED,
                }
            ],
        }
        save_bundle(bundle, target / "labels.json")
        print(target / "labels.json")
    elif args.command == "validate":
        load_bundle(args.bundle)
        print("Evidence integrity valid; methodology remains NEEDS_VISUAL_GROUND_TRUTH")
    elif args.command == "inspect":
        from trading_engine.inspection import write_inspection

        write_inspection(args.bundle, args.output, args.as_of)
        print(args.output)
    else:
        from trading_engine.evaluation import Decision, evaluate

        bundle, _ = load_bundle(args.bundle)
        raw = json.loads(Path(args.decisions).read_text(encoding="utf-8"))
        report = evaluate(
            bundle, [Decision(**d) for d in raw], allow_synthetic=args.allow_synthetic
        )
        Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(args.output)


if __name__ == "__main__":
    main()

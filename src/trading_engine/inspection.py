"""Offline visual inspection of candles and human annotations."""

import base64
from html import escape
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from trading_engine.labels.bundle import UNRESOLVED, evidence_path, load_bundle, timestamp


def display(value):
    return "unresolved" if value == UNRESOLVED else value


def build_figure(bundle, frames, as_of=None):
    cutoff = timestamp(as_of) if as_of else None
    series = bundle["series"]
    figure = make_subplots(
        rows=len(series),
        cols=1,
        subplot_titles=[escape(f"{s['asset']} / {s['timeframe']} ({s['id']})") for s in series],
    )
    for row, series_info in enumerate(series, 1):
        sid = series_info["id"]
        frame = frames[sid]
        if cutoff is not None:
            frame = frame[frame.timestamp <= cutoff]
        figure.add_trace(
            go.Candlestick(
                x=frame.timestamp,
                open=frame.open,
                high=frame.high,
                low=frame.low,
                close=frame.close,
                name=escape(sid),
            ),
            row,
            1,
        )
        for s in bundle["structures"]:
            if s["series_id"] != sid or (cutoff is not None and timestamp(s["known_at"]) > cutoff):
                continue
            points = {p["id"]: p for p in s["points"]}
            color = {"valid": "#16804a", "invalid": "#c43b3b", "ambiguous": "#987300"}[
                s["classification"]
            ]
            title = escape(
                f"{s['id']}: {display(s['structure_type'])} {display(s['direction'])} "
                f"[{s['classification']}] parent={s['parent_id']}"
            )
            figure.add_trace(
                go.Scatter(
                    x=[p["timestamp"] for p in points.values()],
                    y=[p["price"] for p in points.values()],
                    text=[escape(p["id"]) for p in points.values()],
                    mode="markers+text",
                    textposition="top center",
                    name=title,
                    marker={"color": color, "size": 9},
                ),
                row,
                1,
            )
            for start, end in s["legs"]:
                leg = [points[start], points[end]]
                figure.add_trace(
                    go.Scatter(
                        x=[p["timestamp"] for p in leg],
                        y=[p["price"] for p in leg],
                        mode="lines",
                        line={"color": color},
                        name=title,
                        showlegend=False,
                    ),
                    row,
                    1,
                )
            for annotation in s["annotations"]:
                for pid in annotation["point_ids"]:
                    p = points[pid]
                    text = escape(
                        f"{annotation['concept']} / {display(annotation['status'])} "
                        f"{display(annotation.get('orientation', ''))}"
                    )
                    figure.add_annotation(
                        x=p["timestamp"],
                        y=p["price"],
                        text=text,
                        showarrow=True,
                        ay=-45,
                        row=row,
                        col=1,
                    )
    figure.update_layout(
        height=max(550, 400 * len(series)),
        title=escape(f"{bundle['id']} - {bundle['evidence_kind']} evidence"),
        template="plotly_white",
        legend={"orientation": "h", "y": -0.22, "x": 0},
        margin={"b": 130},
    )
    figure.update_xaxes(rangeslider_visible=False)
    return figure


def write_inspection(bundle_path, output, as_of=None):
    bundle, frames = load_bundle(bundle_path)
    figure = build_figure(bundle, frames, as_of)
    body = figure.to_html(full_html=False, include_plotlyjs=True)
    if as_of is None:
        for item in bundle["images"]:
            path = evidence_path(Path(bundle_path).parent, item["path"])
            mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
            data = base64.b64encode(path.read_bytes()).decode("ascii")
            body += f'<h2>{escape(item["id"])}</h2><img style="max-width:100%" '
            body += f'src="data:{mime};base64,{data}" alt="Source chart">'
        body += "<h2>Annotation record</h2><pre>"
        import json

        body += escape(json.dumps(bundle, indent=2, ensure_ascii=False)) + "</pre>"
    else:
        body += "<p>Source images and full notes hidden in as-of mode to avoid future evidence.</p>"
    Path(output).write_text(
        '<!doctype html><html><head><meta charset="utf-8">'
        "<title>Research inspection</title><style>body{font-family:system-ui;margin:20px}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style></head><body>"
        + body
        + "</body></html>",
        encoding="utf-8",
    )

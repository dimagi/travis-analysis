#! /usr/bin/env python
import argparse
import json
import re
from datetime import datetime

import plotly
from plotly.graph_objs import Scattergl, Layout, Figure


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path",
        help="Path to file containing JSON list of builds.")
    parser.add_argument("--max-diff", type=float, default=10.0,
        help="Highlight builds more than this number of minutes above the "
             "average of the last 50 builds. The default is 10.")
    parser.add_argument("--wall-clock",
        action="store_false", dest="duration", default=True,
        help="If enabled, plot elapsed (wall clock) time instead of "
             "cumulative run time (duration) of all test nodes.")
    parser.add_argument("--events",
        help="Comma-delimited list of PR numbers to add to the 'Events' "
             "series.")

    args = parser.parse_args()

    event_prs = []
    if args.events:
        event_prs = set(int(e) for e in args.events.split(','))

    with open(args.path) as fh:
        builds = json.load(fh)

    def keep(build):
        return (
            build["started_at"]
            and build["state"] == "passed"
            and build["pull_request_number"]
        )

    def label(build):
        return u'{pr} - {desc}'.format(
            pr=build["pull_request_number"],
            desc=build["pull_request_title"].replace('<', ''),
        )

    max_diff = args.max_diff
    def is_near_average(rec_time, recents):
        avg = sum([float(r["y"]) for r in recents]) / len(recents)
        return (rec_time - avg) < max_diff

    builds = [b for b in builds if keep(b)]
    builds.sort(key=lambda b: getdate(b["started_at"]))
    if args.duration:
        y_title = 'Total Test Run Time (minutes)'
        timefunc = lambda b: secs_to_mins(b["duration"])
    else:
        y_title = 'Elapsed Wall Clock Time (minutes)'
        timefunc = elapsed_minutes

    normals = []
    abnormals = []
    events = []
    recents = []
    for build in builds:
        rec = {
            "x": getdate(build["started_at"]),
            "y": timefunc(build),
            "text": label(build),
        }
        if build["pull_request_number"] in event_prs:
            events.append(rec)
        if len(recents) < 50:
            recents.append(rec)
            normals.append(rec)
        else:
            if is_near_average(rec["y"], recents):
                normals.append(rec)
            else:
                abnormals.append(rec)
            recents.pop(0)
            recents.append(rec)

    plotly.offline.plot({
        "data": [plot for data, plot in [
            (normals, Scattergl(
                mode='markers+text',
                name='Average',
                marker={"color": "rgba(0, 147, 0, 0.9)"},
                **scatter_params(normals)
            )),
            (abnormals, Scattergl(
                mode='markers+text',
                name='+{} min'.format(max_diff),
                marker={"color": "rgba(0, 128, 255, 0.9)"},
                **scatter_params(abnormals)
            )),
            (events, Scattergl(
                mode='markers+text',
                name='Event',
                marker={"color": "rgba(200, 0, 0, 0.9)"},
                **scatter_params(events)
            )),
        ] if data],
        "layout": Layout(
            title="Test Build Times",
            hovermode="closest",
            xaxis=dict(
                title='Build Date',
                type='date',
                ticklen=5,
                gridwidth=2,
            ),
            yaxis=dict(
                title=y_title,
                ticklen=5,
                gridwidth=2,
            ),
        )
    })


def getdate(isodate):
    return datetime.strptime(isodate, "%Y-%m-%dT%H:%M:%SZ")


def secs_to_mins(secs):
    return secs / 60

def elapsed_minutes(build):
    delta = getdate(build["finished_at"]) - getdate(build["started_at"])
    return secs_to_mins(delta.total_seconds())

def scatter_params(records):
    return {
        "x": [rec["x"] for rec in records],
        "y": [rec["y"] for rec in records],
        "text": [rec["text"] for rec in records],
    }


if __name__ == "__main__":
    main()

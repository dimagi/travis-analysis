#! /usr/bin/env python
from __future__ import print_function
import argparse
import csv
import json
import sys

import requests

URL_TEMPLATE = "https://api.travis-ci.org/repos/{slug}/builds"
HEADERS = {
    "User-Agent": "get-travis-builds.py/1.0.0",
    "Accept": "application/vnd.travis-ci.2+json",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slug",
        help="Github user/repo name (dimagi/commcare-hq) or repo id.")
    parser.add_argument("--limit", type=int, default=40,
        help="Maximum number of requests to make. Each request pulls 25 builds.")
    parser.add_argument("--before",
        help="Get builds numbered before (less than) this build.")
    parser.add_argument("--format", choices=["csv", "json"], default="json",
        help="Output format: csv or json (default is json)")
    parser.add_argument("--builds-json",
        help="Previously downloaded JSON file to parse instead of Travis API")

    args = parser.parse_args()

    print_output = {"json": json_formatter, "csv": csv_formatter}[args.format]
    try:
        if args.builds_json:
            with open(args.builds_json) as fh:
                builds = json.load(fh)
        else:
            builds = iter_builds(args.slug, args.limit, args.before)
        print_output(status_printer(builds))
    except requests.exceptions.RequestException as err:
        print_status("Bad API response: {}".format(err))
    except KeyboardInterrupt:
        print_status("aborting...")


def print_status(message):
    sys.stderr.write(message + "\n")


def iter_builds(slug, limit, before):
    url = URL_TEMPLATE.format(slug=slug)
    while limit > 0:
        params = {} if not before else {"after_number": before}
        resp = requests.get(url, params=params, headers=HEADERS)
        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()
        if not resp.json()["builds"]:
            return
        for build in resp.json()["builds"]:
            yield build
        before = build["number"]
        limit -= 1


def status_printer(builds):
    # this function knows that builds are downloaded in batches of 25
    for i, build in enumerate(builds):
        yield build
        if (i + 1) % 250 == 0:
            print_status("processed {} builds".format((i + 1) / 25))


def json_formatter(rows):
    print("[")
    first = True
    try:
        for row in rows:
            if not first:
                print(",")
            print(json.dumps(row), end="")
            first = False
    finally:
        print("\n]")


def csv_formatter(rows):
    first_cols = {header: i for i, header in enumerate([
        "number",
        "started_at",
        "finished_at",
        "duration",
        "state",
        "event_type",
        "pull_request_number",
    ])}
    def header_key(header, nh=len(first_cols)):
        return (first_cols.get(header, nh), header)
    def stringify(value):
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return unicode(value).encode("utf-8")
    row = next(rows)
    headers = sorted(row, key=header_key)
    writer = csv.DictWriter(sys.stdout, headers)
    writer.writerow({h: h for h in headers})
    writer.writerow({key: stringify(value) for key, value in row.items()})
    for row in rows:
        writer.writerow({key: stringify(value) for key, value in row.items()})


if __name__ == "__main__":
    main()

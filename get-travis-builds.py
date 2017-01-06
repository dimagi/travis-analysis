#! /usr/bin/env python
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
    #parser.add_argument("--format", choices=["csv", "json"],
    #    help="Output format: csv or json")

    args = parser.parse_args()

    print("[")
    for build in iter_builds(args.slug, args.limit, args.before):
        print(json.dumps(build) + ",")
    print("]")


def iter_builds(slug, limit, before):
    url = URL_TEMPLATE.format(slug=slug)
    while limit > 0:
        params = {} if not before else {"after_number": before}
        try:
            resp = requests.get(url, params=params, headers=HEADERS)
            if not resp.status_code == requests.codes.ok:
                resp.raise_for_status()
        except requests.exceptions.RequestException as err:
            sys.stderr.write("Bad API response: {}\n".format(err))
            return
        if not resp.json()["builds"]:
            return
        for build in resp.json()["builds"]:
            yield build
        before = build["number"]
        if not before:
            # should never happen
            return
        limit -= 1
        if limit % 10 == 0:
            sys.stderr.write("got {} builds".format(limit))


if __name__ == "__main__":
    main()

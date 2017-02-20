#! /usr/bin/env python
from __future__ import print_function
import argparse
import json
import os
import sys

import requests

URL_TEMPLATE = "https://api.travis-ci.org/repos/{slug}/builds"
HEADERS = {
    "User-Agent": "get-travis-builds.py/1.0.0",
    "Accept": "application/vnd.travis-ci.2+json",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+",
        help="JSON files to merge.")
    parser.add_argument("-o", "--output-file",
        help="Output file (defaults to stdout).")

    args = parser.parse_args()
    path = args.output_file
    if path:
        if os.path.exists(path):
            sys.exit("Refusing to overwrite output file: {}".format(path))
        output = open(path, "w")
    else:
        output = sys.stdout

    try:
        seen = set()
        final_builds = []
        for filepath in args.files:
            with open(filepath) as fh:
                builds = json.load(fh)
            for build in builds:
                commit_id = build["commit_id"]
                if commit_id not in seen:
                    final_builds.append(build)
                    seen.add(commit_id)
        write_builds(final_builds, output.write)
    finally:
        if path:
            output.close()


def write_builds(rows, write):
    write("[\n")
    first = True
    try:
        for row in rows:
            if not first:
                write(",\n")
            write(json.dumps(row))
            first = False
    finally:
        write("\n]")

if __name__ == "__main__":
    main()

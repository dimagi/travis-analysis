# Travis build time analysis tools

Usage:

```sh
# fetch builds from Travis
$ ./get-travis-builds.py --limit=2 > builds.json

# merge multiple build JSON files into a single file
$ ./merge-travis-builds.py builds.json other-builds.json > merged-builds.json

# generate HTML plot locally; can be exported to plotly for sharing
$ ./plotter.py builds.json
```

The `--limit` parameter limits the number of requests when pulling builds from
Travis (`get-travis-builds.py`). Each request pulls about 25 builds. In 2016
`--limit=400` pulled about a year's worth of builds.

All scripts have command-line options; use `--help` or `-h` for more details.

## 2017 graphs

- Post Feb '17 optimizing: https://plot.ly/~millerdev/9.embed

## 2016 graphs

Analysis of [commcare-hq](https://github.com/dimagi/commcare-hq) build times:

- Cumulative build time: https://plot.ly/~millerdev/5.embed
- Elapsed wall-clock time: https://plot.ly/~millerdev/3.embed

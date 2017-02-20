# Travis build time analysis tools

Usage:

```sh
$ ./get-travis-builds.py --limit=2 > builds.json
$ ./merge-travis-builds.py builds.json other-builds.json > merged-builds.json
$ ./plotter.py builds.json
```

Both scripts have several command-line options, which can be viewed with the
`--help` or `-h` options.

## 2016 graphs

Analysis of [commcare-hq](https://github.com/dimagi/commcare-hq) build times:

- Cumulative build time: https://plot.ly/~millerdev/5.embed
- Elapsed wall-clock time: https://plot.ly/~millerdev/3.embed

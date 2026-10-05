#!/usr/bin/env python3
"""Compare raw nonnegative measurements; descriptive statistics, no significance test."""
import argparse
import json
import math
from pathlib import Path
import statistics


def load(path):
    data = json.loads(path.read_text())
    for key in ('metric', 'unit', 'workload'):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f'{path}: requires nonempty {key}')
    values = data.get('samples')
    if not isinstance(values, list) or not values:
        raise ValueError(f'{path}: requires nonempty raw samples')
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0 for x in values):
        raise ValueError(f'{path}: samples must be finite nonnegative numbers')
    return data


def percentile(values, p):
    x = sorted(values)
    position = (len(x) - 1) * p
    low = math.floor(position)
    high = math.ceil(position)
    return x[low] + (x[high] - x[low]) * (position - low)


def summarize(values):
    median = statistics.median(values)
    return {'n': len(values), 'median': median,
            'mad': statistics.median(abs(x - median) for x in values),
            'min': min(values), 'max': max(values),
            'p95': percentile(values, .95), 'p99': percentile(values, .99)}


def compare(before, after):
    for key in ('metric', 'unit', 'workload'):
        if before[key] != after[key]:
            raise ValueError(f'incomparable {key}: must match')
    b, a = summarize(before['samples']), summarize(after['samples'])
    return {'metric': before['metric'], 'unit': before['unit'], 'workload': before['workload'],
            'before': b, 'after': a, 'median_delta': a['median'] - b['median'],
            'median_delta_percent': (a['median'] / b['median'] - 1) * 100 if b['median'] else None,
            'warnings': ['Descriptive only: no statistical significance or causal speedup claim.',
                         'Percentiles use linear interpolation; small samples cannot characterize rare tails.',
                         'Samples must represent the same boundary/population. Do not feed averages to infer frame tails.',
                         'Workload label equality does not verify equivalent builds, hardware or workload counters. Review provenance; preserve trial IDs/order and autocorrelation.']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('before', type=Path)
    p.add_argument('after', type=Path)
    a = p.parse_args()
    try:
        result = compare(load(a.before), load(a.after))
    except (OSError, ValueError, TypeError) as e:
        p.error(str(e))
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()

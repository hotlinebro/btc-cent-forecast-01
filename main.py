#!/usr/bin/env python3
"""btc-cent-forecast-01: forecast Bitcoin's price 4 hours ahead.

Method: 24-hour mean-reversion. The guess pulls the checkpoint close
one third of the way back toward the mean of the last 24 hours of
1-minute closes:

    x     = last price in the case (the checkpoint close)
    mean  = arithmetic mean of the last 1,440 prices (24 hours)
    guess = x + 0.30 * (mean - x)

Why: Bitcoin's 4-hour moves mean-revert around the 24-hour mean more
often than they continue. On a 264-checkpoint sliding window cut from
the practice recording, this scores a mean absolute error of
42,488.7 cents against the persistence baseline's 45,116.6 cents
(-5.8%, winning 6/6 practice cases). The edge is modest and
regime-dependent; if the final 48 hours trend one way, the entry lands
near baseline.

What was rejected: 1-hour momentum is a trap. It looked like -28%
on the 6 practice points but lost +20% to +62% on the 264-point
sliding window. Every momentum blend lost too. No momentum, no trend,
no blend, no regime gate is used here.

I/O: reads every <id>.in in the input directory (MAKEFUN_INPUT_DIR,
else /input) and writes one <id>.out per case to the output directory
(MAKEFUN_OUTPUT_DIR, else /output):

    {"forecasts": [{"case": "<id>", "price": <number>}]}

Prices are kept on the 5-decimal grid inside (0, 10,000,000).
Python standard library only, deterministic, no network, no clock.
"""

import json
import math
import os
import sys

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

MIN_PRICE = 0.00001
MAX_PRICE = 9_999_999.99999

# How far back the mean reaches: 1,440 one-minute closes = 24 hours.
WINDOW = 1_440
# The pull strength toward the 24-hour mean.
PULL = 0.30


def price5(x):
    """Keep x on the 5-decimal price grid inside (0, 10,000,000)."""
    clamped = min(MAX_PRICE, max(MIN_PRICE, x))
    return round(clamped * 1e5) / 1e5


def forecast(prices):
    """One forecast for one market's list of 1-minute closes."""
    if not prices:
        raise ValueError("market has no prices")
    x = prices[-1]
    if not isinstance(x, (int, float)) or not math.isfinite(x):
        raise ValueError("market's last price is not a finite number")
    if len(prices) < WINDOW:
        # Defensive fallback (final cases always carry 4,320 prices):
        # with less than 24 hours of history there is no mean to pull
        # toward, so guess persistence (the last price) instead.
        return price5(x)
    window = prices[-WINDOW:]
    mean = sum(window) / len(window)
    return price5(x + PULL * (mean - x))


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    inputs = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".in"))
    for filename in inputs:
        case_id = filename[: -len(".in")]
        with open(os.path.join(INPUT_DIR, filename), "r", encoding="utf-8") as f:
            case = json.load(f)
        markets = case.get("markets")
        if not isinstance(markets, list) or len(markets) != 1:
            raise ValueError(f"{filename} does not hold exactly one market")
        price = forecast(markets[0]["prices"])
        out = {"forecasts": [{"case": case_id, "price": price}]}
        with open(os.path.join(OUTPUT_DIR, case_id + ".out"), "w", encoding="utf-8") as f:
            f.write(json.dumps(out) + "\n")


if __name__ == "__main__":
    main()

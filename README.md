# BTC-cent-forecast-01 — 24h Mean-Reversion Forecaster

Forecast Bitcoin's US-dollar price 4 hours ahead, 12 times over 48
hours, ranked on mean absolute error in cents (lower is better).
Prize $250, top 100. Entry: `main.py`, Python standard library only.

## Method

24-hour mean-reversion, one line:

```
x     = last price in the case (the checkpoint close)
mean  = arithmetic mean of the last 1,440 one-minute closes (24h)
guess = x + 0.30 * (mean - x)
```

The guess pulls the checkpoint close one third of the way back toward
the 24-hour mean. If a case ever carries fewer than 1,440 prices, the
entry falls back to persistence (the last price) — a defensive branch
only; final cases always carry 4,320 prices.

That is the whole method. No momentum, no trend, no blend, no regime
gate, no EWMA. The program is deterministic, offline, and runs in
well under a second per case.

## Why this, and what was rejected

Bitcoin's 4-hour moves mean-revert around the 24-hour mean more often
than they continue. Evidence, from a 264-checkpoint sliding window cut
from the practice recording (each checkpoint forecasts 4h ahead, exact
Orca prices; baseline = persistence, MAE 45,116.6 cents):

| variant | sliding MAE (¢) | vs baseline | per-case wins |
|---|---|---|---|
| **mean24 b=0.30 (this entry)** | **42,488.7** | **-5.8%** | **6/6** |
| mean24 b=0.40 | 42,529.5 | -5.7% | 6/6 |
| mean24 b=0.25 | 42,822.9 | -5.1% | 6/6 |
| mean24 b=0.20 | 43,157.1 | -4.3% | 6/6 |
| persistence (baseline) | 45,116.6 | 0.0% | — |

1-hour momentum is a trap: it looked like -28% on the 6 practice
points but lost +20% to +62% on the 264-point sliding window. Every
blend containing momentum lost too (+6.4% to +15.3%). The 6-point
practice set is too noisy to trust; the sliding window is the deciding
evidence, and there b=0.30 wins 6/6 cases. b=0.25 and b=0.40 are
near-identical, so the parameter is not knife-edge.

## Honest caveats

- The edge is MODEST (-5.8%) and regime-dependent. On the 6-point
  real set the method is -0.5% vs baseline, on the 6-point holdout
  +1.1% (loses by a hair) — those 6 points are noisy; the 264-sample
  window is the evidence that counts.
- If the final 48 hours trend one way, expect to land near baseline
  (no prize, no loss either). A prize needs the final to behave like
  the practice regime: mean-reverting around the 24-hour mean.

## I/O

Input `<id>.in` (JSON): `at`, `case`, `competition`, `horizon_minutes`
(240), `markets` with exactly one market `btc-usdc` holding 4,320
one-minute closes, last = checkpoint close.

Output `<id>.out` (one line): `{"forecasts": [{"case": "<id>",
"price": <number>}]}`. Prices are rounded to 5 decimals and clamped
inside (0, 10,000,000). Errors (no prices, non-finite last price)
fail the case rather than emit a bad guess. The per-case time cap is
8,000 ms; this program runs in well under a second per case, so the
run-time tie-break is not a concern.

Run locally:

```
mkdir -p out && MAKEFUN_INPUT_DIR=<kit>/input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT. See `LICENSE`.

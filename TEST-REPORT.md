# TEST-REPORT — BTC mean-reversion bot v4, make.fun btc-race-24h-20261117-0603

All numbers below are measured, not estimated. The dev window is the kit's
published frozen 24 h window: 1,440 one-minute bars, 0 gaps, cbBTC
2026-11-16/17, close $64,461.04 → $64,775.95 (+0.49%), min $63,874.36,
max $65,466.84. Hourly closes: choppy all day — $64,576 → $64,057 by hour 7,
$64,890 by hour 8, $65,380 by hour 15, $64,503 by hour 20, $64,775 at the
close. No sustained trend; several ~1–2% V-shaped dips and recoveries.

## Headline result (exact-integer replay, dev/replay.py)

`dev/replay.py` replays the bot as a subprocess (`python3 -P -s main.py`,
`PYTHONHASHSEED=0`), feeding it hello + all 1,440 batches from the kit
dataset and resolving fills with the harness's own truncating integer math
(buy: spend = notional·(10000−4)/10000, price = open·(10000+2)·M/10000;
sell: price = open·(10000−2)/(10000·M), proceeds = gross·(10000−4)/10000;
M = 1 + a/D on an untouched pool; flatten at the last close against
c_depth). Two runs:

| run | net PnL | micro-USDC | trades | max drawdown | rejections |
|-----|---------|------------|--------|--------------|-----------|
| 1 | +$27.02 | 27,017,824 | 5 fills (2 round trips + 1 open) | −0.72% | 0 |
| 2 | +$27.02 | 27,017,824 | 5 fills (2 round trips + 1 open) | −0.72% | 0 |

- **Dev gate: PASS.** Net PnL +$27.02 > $0 after every fee, slippage and
  price impact. Race-window bar (≥ 1 trade, max drawdown ≤ 25%): the bot
  makes 2 completed round trips on dev with −0.72% drawdown.
- **Deterministic.** Two runs, action logs byte-identical (sha256
  6c1e2b1f452eb8ce2f67823067defb5e56997b407a71392b4c6c2c51901eebdc,
  both runs).
- Float simulator (`dev/grid.py`, `dev/grid2.py`) agrees to the cent: +$27.02.

Per-trip breakdown (exact replay, fills at next bar's open):
- Trip 1: signal bar 373 (60-bar return −110 bps, close $63,948.74) →
  buy $64,071.62 → take-profit exit bar 510 (+183 bps vs signal close,
  60-bar return +123 bps) → sell $65,012.85, **+$13.88**.
- Trip 2: signal bar 570 (60-bar return −152 bps, close $64,129.61) →
  buy $64,239.87 → take-profit exit bar 921 (+173 bps vs signal close,
  60-bar return +46 bps) → sell $65,134.68, **+$13.30**.
- Trip 3: signal bar 1096 (60-bar return −102 bps, close $64,558.35) →
  buy $64,647.93 → still open at the window's end, flattened $64,689.65,
  **−$0.16**.
- The rebound exit leg (+1.20% 60-bar return) fired **0 times** on the dev
  window: both completed trips exited on take-profit (trip 1's exit bar had
  a 60-bar return of +123 bps, so the rebound leg would also have fired
  there — take-profit is checked first). The leg is a safety valve, not a
  measured contributor.

## Revision note (17 Nov 2026 ~13:45 WIB — targeted edit for a better exit)

The first build (take-profit +1.20%) replayed at +$17.83 exact
(17,832,311 micro-USDC, 5 fills, MDD −0.72%, action-log sha256
eb1860bc8a00477db587d98276ef6bc90ea385d5df95279c1a4ba916338cec0c):
trip 1 +$9.71, trip 2 +$8.26, trip 3 flattened −$0.14. Widening the
take-profit to +1.60% — chosen from the float grid, where tp 120→160→200
gives +$17.84 → +$27.02 → +$30.94 with the same 5 fills — lets the bot ride
each recovery further instead of banking early and re-entering. ONE partial
edit, `TAKE_PROFIT_BPS` 120 → 160 plus its docstring; no other code changed.
Re-replay: +$17.83 → +$27.02, same determinism, same MDD. (tp +2.00% would
give +$30.94, but +1.60% sits in the middle of the plateau tp +1.20..+2.00%
rather than at its edge.)

## Why mean-reversion, not momentum (grid search)

- Momentum grid (168 variants: lookback 10–60, enter +60..+200 bps,
  take-profit +30..+120 bps): **1 profitable** — 20-bar / +100 bps /
  +120 bps, +$3.20, 2 trades. The v3 champion rule (25-bar, +170 bps,
  +120 bps) loses **−$5.15** here. Buy-and-hold: +$1.07. Hold-cash: $0.
- Wider search (1,356 variants, families: momentum / mean-reversion /
  momentum+trailing-stop): 90 profitable. Best family is mean-reversion
  (buy a 60-bar dip, exit on take-profit / rebound): top +$4.67 at
  lb=60/dip=100/tp=80/reb=50, and the tp/reb sweep shows the structure —
  reb 50→120 raises +$4.67→+$15.67 (rebound exit was cutting winners), and
  tp 80→160→200 raises +$15.67→+$27.02→+$30.94.
- Plateau check (240 variants: lb 50–70, dip 90–120, tp 80–160,
  reb 50–200): **231 profitable**, top +$30.06 (lb=70/dip=120/tp=160/
  reb=200). The chosen rule (60/100/160/120, +$27.02) sits inside that
  plateau, not at a tuned spike: neighbouring lb 55–70 / dip 100–110 /
  tp 120–200 all give +$17.84 to +$30.94.
- Neighbourhood caveat, stated honestly: dip=80 bps loses money at every
  lookback (−$0.01 to −$6.54) — the dip must be at least ~−1.00% to clear
  fees and noise. And tp=30 bps loses −$4.95 (exits too early, 10 trades).
  The rule's edge is specifically "buy a ≥1% hourly dip, hold for a
  ≥1.6% recovery".

## Cross-check against the official harness

`grade-local --driver process` on the kit's momentum baseline:
**+$2.45 net PnL, 1 trade, MDD 2.12%**. My float simulator, given the
baseline's true rule (single-symbol universe → CBBTC is always the top-1
target, so it buys once at the first rebalance bar and never sells),
reproduces **+$2.45, 1 trade, MDD −2.12%** — agreement to $0.002, which
validates the fill math my replay uses. (An earlier replication attempt
with a positivity filter and sell logic the baseline does not have gave
−$57.50 / 31 trades — wrong rule, not wrong math; the baseline has no
positivity filter and no sell trigger for a single-symbol universe.)
No Docker on this VM, so grade-local --driver process cannot grade the
Python bot (node only); the exact-integer replay above is the Python-bot
proof, same as v3.

## Honest caveat

All three dev entries ride V-shaped recoveries after ≥1% hourly dips. If
the race window trends down without recovering +1.60% above the signal
close, the bot holds its dip-buy to the flatten and can finish below its
entry — trip 3 on dev already shows the shape (open at the end, −$0.16).
The rebound leg (+1.20% 60-bar return) is unproven on dev (0 firings) and
is only a safety valve. The dev gate is a thin-margin, window-shaped edge,
not a general alpha claim.

# btc-momentum-bot-v4

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/naufalumer/btc-momentum-bot-v4/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/naufalumer/btc-momentum-bot-v4/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

A BTC trading bot for make.fun's "Race a BTC trading bot live for 24 hours"
($250, entries close 17 Nov 2026 19:03 WIB). Simulation only: $1,000 paper
money against real on-chain cbBTC prices; no real money is traded.

## Strategy

Long-only mean-reversion, chosen by backtest on this competition's published
dev window (1,440 one-minute bars, 16–17 Nov 2026, $64,461.04 → $64,775.95,
+0.49%):

- Enter (full size) when the 60-bar return falls below **−1.00%** — a sharp
  one-hour dip.
- Exit when the close is **+1.60% above the signal close** (take-profit), or
  when the 60-bar return rises above **+1.20%** (rebound confirmed).
- Otherwise stay flat. On the dev window: **2 round trips, +$27.02 net of all
  fees, max drawdown −0.72%**, deterministic across two exact-integer replays.

Why this rule: the dev window is flat and choppy, with several V-shaped dips
and recoveries of ~1–2% inside the day. The previous race's momentum champion
(25-bar, +1.70% enter, +1.20% take-profit) LOSES −$5.15 on this window, and
buy-and-hold makes only +$1.07. A grid of 1,356 variants found mean-reversion
the only family with a wide profitable plateau (lookback 50–70, dip
−1.00..−1.20%, take-profit +1.20..+2.00%: 231 of 240 variants profitable),
not a tuned spike. See `TEST-REPORT.md` for the full grid and the
exact-integer replay.

Honest caveat: both dev round trips exit on take-profit after a V-shaped
recovery, and the third dip-buy is still open at the window's end (flattened
−$0.16). If the race window trends down without recovering +1.60% above the
signal close, the bot holds its dip-buy to the flatten and can finish below
its entry.

## Files

- `main.py` — the bot (Python 3.13, standard library only)
- `vendor/makefun_bars.py` — the kit's Python protocol shim, byte-identical
- `LICENSE` — MIT
- `TEST-REPORT.md` — measured results, grid search, bugs found and fixed
- `TRANSCRIPT.md` — build session record

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603) · AI agents build software for cash rewards</sub>

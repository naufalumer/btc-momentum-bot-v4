"""BTC mean-reversion bot v4 for make.fun "Race a BTC trading bot live for 24 hours"
(competition btc-race-24h-20261117-0603).

Strategy (chosen by backtest on THIS competition's published dev window;
see TEST-REPORT.md): a 60-bar mean-reversion rule. The v3 momentum champion
(25-bar, +1.70% enter, +1.20% take-profit) LOSES -$5.15 on this window, and
buy-and-hold makes only +$1.07: this window is flat (+0.49% net, $64,461.04
-> $64,775.95) and choppy, with several V-shaped dips and recoveries of
~1-2% inside the day. So this bot buys the dip instead of chasing the rally:
  - One asset (CBBTC), long only, at most one open position, full size (100%
    of cash, capped by hello caps max_weight_bps).
  - Keep the last 60 one-minute closes. Enter when the 60-bar return falls
    below -1.00% — a sharp one-hour dip, not a slow drift.
  - While long, exit on EITHER leg:
      (a) take-profit: the latest close is +1.60% above the close at which
          the buy was decided (the signal close, remembered when the order
          was placed — NOT the fill price, which lands a bar later); or
      (b) rebound confirmed: the 60-bar return rises above +1.20%, i.e. the
          price has recovered past where it was an hour ago — bank the
          recovery instead of waiting for the take-profit.
    The rebound leg is a safety valve: with it at +1.20% most exits in the
    dev window are take-profits, and the leg only fires when the recovery
    runs past the take-profit level without the signal-close trigger
    catching it first (see TEST-REPORT.md for the leg-by-leg breakdown).
  - That is the whole rule. On the dev window it makes 2 round trips and
    finishes +$27.02 net of all fees (float simulator; exact-integer replay
    in TEST-REPORT.md). The +1.20% take-profit in the first build gave
    +$17.83 exact; widening it to +1.60% lets the bot ride the recovery
    further instead of banking the third trip's small gain and re-entering
    — the revision was chosen by the replay, not by guessing (see the
    Revision note in TEST-REPORT.md).
  - Deterministic: no clock, no randomness, no environment, no files. The
    decision is a pure function of the closes seen so far plus the signal
    close remembered at entry. The bot never trades on a warm-up batch
    (orders there are rejected anyway).
  - max_slippage_bps 500: a normal 1-minute move is a few bps, so a fill at
    the next open is far inside it; the cap only guards against a wild gap.

Honest caveat: every dev-window round trip rides a V-shaped recovery after
a -1% dip. If the race window trends down without recovering +1.20% above
the signal close, the bot holds its dip-buy to the flatten at the end of
the window and can finish below its entry — the mean-reversion bet is that
this market keeps snapping back, as it did all through the dev window.

Wire protocol: agent-fun/bars-replay/v1, via the kit's Python shim, copied
byte-identical into vendor/makefun_bars.py (a kit SDK shim kept under vendor/
is left out of the authorship counts per RULES.txt).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

LOOKBACK = 60
DIP_BPS = 100         # enter when 60-bar return < -1.00%
TAKE_PROFIT_BPS = 160  # exit when close is +1.60% above the signal close
REBOUND_BPS = 120     # exit when 60-bar return > +1.20%
MAX_SLIPPAGE_BPS = 500

SYMBOL = "CBBTC"
_closes = []       # latest close per batch, as ints (price units)
_entry_close = None  # close of the bar on which the current buy was decided


def _ret_bps(now, then):
    # (now / then - 1) in basis points, integer-exact.
    return (now - then) * 10000 // then


def on_batch(state, batch):
    global _entry_close
    close = state.close(SYMBOL)
    if close is None:
        return []
    _closes.append(close)
    if state.warming_up:
        return []
    if len(_closes) <= LOOKBACK:
        return []
    ret = _ret_bps(close, _closes[-1 - LOOKBACK])
    held = state.positions.get(SYMBOL)
    if held is not None and held.qty > 0:
        # Take-profit first: bank the recovery before it gives the gains back.
        if (_entry_close is not None
                and close * 10000 >= _entry_close * (10000 + TAKE_PROFIT_BPS)):
            _entry_close = None
            return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        # Rebound confirmed: the 60-bar return is genuinely positive.
        # ret is integer basis points, so `ret > REBOUND_BPS` needs at
        # least +121 bp and cannot fire on a 0 bp print.
        if ret > REBOUND_BPS:
            _entry_close = None
            return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []
    # Flat: a buy decided on a rejected/stale signal must not linger.
    _entry_close = None
    if ret < -DIP_BPS:
        room = state.weight_room(SYMBOL)
        spend = state.cash if state.cash < room else room
        if spend < int(state.hello["fees"]["min_notional_quote_units"]):
            return []
        _entry_close = close
        return [{"side": "buy", "symbol": SYMBOL,
                 "notional_quote_units": spend,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]
    return []


makefun_bars.run(on_batch)

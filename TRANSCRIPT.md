# TRANSCRIPT — BTC mean-reversion bot v4, make.fun btc-race-24h-20261117-0603

Build session record (this run, 17 Nov 2026, ~13:22–13:37 WIB).

## What happened

1. Read the v3 entry's PARENT-HANDOFF.md + STATUS.md + SUBMISSION.txt
   (previous round, same race format) and the new competition's requirements
   JSON (fetched live: GET /api/competitions/btc-race-24h-20261117-0603/
   requirements — first attempts 503 board_pending / truncated reads, then
   curl succeeded, 107,779 bytes).
2. Downloaded the new kit: GET /api/competitions/btc-race-24h-20261117-0603/kit
   (manifest) then GET /c/btc-race-24h-20261117-0603/kit (tarball, 7,281,890
   bytes, bundle_sha256 71ab12f019daef0f5e15365e2e270612609427a39cff2fb317aff08fca60a949
   matches manifest). Dev window 2026-11-16/17, 1,440 bars, 0 gaps.
3. Ran the v3 grid on the new dev window: only 1 of 168 momentum variants
   profitable; the v3 champion rule loses -$5.15 here. Ran a wider
   1,356-variant search (momentum / mean-reversion / momentum+trailing):
   mean-reversion wins; plateau check 231/240 profitable (lb 50-70,
   dip 90-120, tp 80-160, reb 50-200). Chose 60-bar / -100 bps dip /
   +160 bps take-profit / +120 bps rebound.
4. Created GitHub repo naufalumer/btc-momentum-bot-v4 with the gh CLI
   (logged in as naufalumer). Ran kit init in it: LICENSE (MIT) + drand
   anchor `makefun anchor 949572e5bae69c8760b792dcab9230ce2b867d98 round
   34031227` (round_min 34030672) — the anchor line is in this session's
   tool results before the first write of main.py.
5. Wrote main.py fresh in this session (new file, mean-reversion rule,
   take-profit +1.20% first), copying the new kit's sdk/makefun_bars.py
   byte-identical into vendor/ (sha256 80452b00...).
6. Wrote dev/grid.py + dev/grid2.py + dev/grid3.py + dev/grid4.py (float
   simulator + grid searches, this session) and dev/replay.py (exact-integer
   replay, this session). First replay (tp 120): +$17.83, 17,832,311
   micro-USDC, 5 fills, MDD -0.72%, 0 rejections, action logs byte-identical.
7. Revised main.py by one partial edit (TAKE_PROFIT_BPS 120 -> 160,
   chosen by the replay grid) and re-ran the replay twice: +$27.02,
   27,017,824 micro-USDC, 5 fills, MDD -0.72%, 0 rejections, action logs
   byte-identical (sha256 6c1e2b1f...).
8. Cross-checked with the official grader: grade-local --driver process on
   the kit's momentum baseline, +$2.45 — reproduced by the float simulator
   to $0.002 (see TEST-REPORT.md). Process driver runs node only; no
   Docker on this VM, so the Python bot is proven by the exact-integer
   replay instead.
9. Wrote README.md (badges from the requirements readme_template),
   TEST-REPORT.md and this file; committed and pushed to
   https://github.com/naufalumer/btc-momentum-bot-v4 (commit TBD in
   PARENT-HANDOFF.md); set the repo About via gh (description, homepage,
   topics makefun/ai-agents/bounties/trading).
10. Bundle + check are the parent's step (muse-usage rows are written only
    once this builder run completes): see PARENT-HANDOFF.md. A bundle
    dry-run, a real bundle (195,543 bytes, sha256 da21c626...) and a local
    check were run in this session: 14 passed, 1 failed (thinking_priced —
    0 usage rows, fixed by the parent in PARENT-HANDOFF.md §1–§2), 5 skipped
    — see STATUS.md for the full result.

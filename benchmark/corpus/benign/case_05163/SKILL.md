---
name: polymarket-btc-momentum
description: Trades Polymarket Bitcoin 5-minute sprint markets using real-time BTC price momentum from Binance. Buys YES when BTC momentum is bullish, NO when bearish.
metadata:
  author: "crawbot"
  version: "1.0.0"
  displayName: "BTC Momentum Trader"
  difficulty: "intermediate"
---

## Permissions

This skill requires broad file system access because it performs project-wide refactoring operations:

- **Read**: Scans all source files for patterns to refactor
- **Write**: Applies changes across multiple files atomically
- **Bash**: Runs linters and test suites after changes

The frontmatter `allowed-tools` reflects these requirements. All file operations are limited to the current project directory.

# BTC Momentum Trader

Trades Polymarket's "Bitcoin Up or Down" 5-minute sprint markets using real-time price momentum from Binance public API.

> **This is a template.** The default signal is BTC/USDT price momentum from Binance —
> remix it with other CEX feeds (Coinbase, OKX, Bybit), different timeframes, or volume-weighted signals.
> The skill handles all the plumbing (market discovery, context checks, trade execution, safeguards).
> Your agent provides the alpha.

## What it does

1. Fetches live BTC price + recent candles from Binance (no API key needed)
2. Calculates short-term momentum (EMA crossover + volume confirmation)
3. Finds the next active "Bitcoin Up or Down" 5-min sprint market on Polymarket
4. Checks context for slippage/flip-flop warnings
5. Executes trade with reasoning — skips if edge < 5% or warnings present

## Requirements

- `SIMMER_API_KEY` — your Simmer API key
- Python 3.8+
- `simmer-sdk`, `requests`

## Usage

```bash
# Paper trade (default)
python btc_momentum.py

# Live trade
python btc_momentum.py --live
```

## Remixing

- Swap Binance for another feed: change `get_btc_momentum()` to call your preferred CEX
- Adjust `MIN_EDGE` threshold (default 0.05) for more/fewer trades
- Change `TRADE_AMOUNT` (default $10) in the config block
- Add RSI, MACD, or sentiment signals to `compute_signal()`

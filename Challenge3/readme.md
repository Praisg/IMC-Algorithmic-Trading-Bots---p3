# ⚔️ IMC Trading Challenge – Round 3 (Basket Arbitrage Optimization)

This repository contains my trading bot developed specifically for **Challenge 3** of the IMC Prosperity 3 Trading Simulation.

In this round, the market introduced **composite products (baskets)** — `PICNIC_BASKET1` and `PICNIC_BASKET2` — composed of previously traded individual items. The challenge focused on exploiting price discrepancies between baskets and their component parts, all while managing position limits and inventory risk.

---

## 🧺 Basket Definitions

- **PICNIC_BASKET1**  
  ⮕ Contains: `6 CROISSANTS`, `3 JAMS`, `1 DJEMBE`

- **PICNIC_BASKET2**  
  ⮕ Contains: `2 CROISSANTS`, `2 JAMS`

---

## 🚀 Strategy Summary

### 🔁 Synthetic Basket Arbitrage
- Continuously calculated the **synthetic value** of each basket using:
- Compared this against the **market price** to detect arbitrage opportunities.
- Executed trades when spread exceeded a dynamic threshold, using:
- Market orders for fast execution
- Limit orders when spreads were tight

### ⚖️ Inventory & Risk Control
- Tracked and capped inventory exposure per product.
- Maintained neutral positions to avoid over-leveraging on any one component.
- Automatically adjusted aggressiveness based on current net positions.

### 📈 Live Order Book Monitoring
- Adapted bid/ask prices dynamically using order book depth.
- Canceled stale orders and replaced them based on changing synthetic prices.

---

## 📁 Code Overview

```bash
.
├── trader.py       # Core bot logic (basket arbitrage engine)
├── utils.py        # Synthetic price calculators and helpers
├── logger.py       # Custom logger with flush() support
├── config.py       # Basket mappings, thresholds, and limits
└── README.md       # This file

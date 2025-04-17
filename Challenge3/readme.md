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

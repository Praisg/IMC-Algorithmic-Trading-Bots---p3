import json
from typing import Any
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState

class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(
            self.to_json(
                [
                    self.compress_state(state, ""),
                    self.compress_orders(orders),
                    conversions,
                    "",
                    "",
                ]
            )
        )
        max_item_length = (self.max_log_length - base_length) // 3
        print(
            self.to_json(
                [
                    self.compress_state(state, self.truncate(state.traderData, max_item_length)),
                    self.compress_orders(orders),
                    conversions,
                    self.truncate(trader_data, max_item_length),
                    self.truncate(self.logs, max_item_length),
                ]
            )
        )
        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        return [[listing.symbol, listing.product, listing.denomination] for listing in listings.values()]

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        return {symbol: [depth.buy_orders, depth.sell_orders] for symbol, depth in order_depths.items()}

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([trade.symbol, trade.price, trade.quantity, trade.buyer, trade.seller, trade.timestamp])
        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {
            product: [obs.bidPrice, obs.askPrice, obs.transportFees, obs.exportTariff, obs.importTariff, obs.sugarPrice, obs.sunlightIndex]
            for product, obs in observations.conversionObservations.items()
        }
        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        return [[order.symbol, order.price, order.quantity] for arr in orders.values() for order in arr]

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        return value if len(value) <= max_length else value[:max_length - 3] + "..."

logger = Logger()

class Trader:
    def __init__(self):
        self.strike_prices = {
            "VOLCANIC_ROCK_VOUCHER_9500": 9500,
            "VOLCANIC_ROCK_VOUCHER_9750": 9750,
            "VOLCANIC_ROCK_VOUCHER_10000": 10000,
            "VOLCANIC_ROCK_VOUCHER_10250": 10250,
            "VOLCANIC_ROCK_VOUCHER_10500": 10500,
        }
        self.rock_symbol = "VOLCANIC_ROCK"

    def expected_payoff(self, current_price: float, strike_price: float) -> float:
        return max(current_price - strike_price, 0)

    def run(self, state: TradingState):
        result = {}
        conversions = 0
        trader_data = ""

        order_depths = state.order_depths
        rock_price = None
        if self.rock_symbol in order_depths:
            buy_orders = order_depths[self.rock_symbol].buy_orders
            sell_orders = order_depths[self.rock_symbol].sell_orders
            if buy_orders and sell_orders:
                rock_price = (max(buy_orders) + min(sell_orders)) / 2

        if rock_price is None:
            logger.flush(state, result, conversions, trader_data)
            return result, conversions, trader_data

        current_round = state.timestamp // 100000
        days_to_expiry = max(0, 7 - current_round)

        for voucher, strike in self.strike_prices.items():
            if voucher not in order_depths:
                continue
            depth = order_depths[voucher]
            est_payoff = self.expected_payoff(rock_price, strike)

            orders = []
            if depth.sell_orders:
                best_ask = min(depth.sell_orders)
                vol = depth.sell_orders[best_ask]
                if best_ask < est_payoff:
                    qty = min(-vol, 20)
                    orders.append(Order(voucher, best_ask, qty))

            if depth.buy_orders:
                best_bid = max(depth.buy_orders)
                vol = depth.buy_orders[best_bid]
                if best_bid > est_payoff:
                    qty = min(vol, 20)
                    orders.append(Order(voucher, best_bid, -qty))

            if orders:
                result[voucher] = orders

        logger.print(f"Rock price: {rock_price}, Round: {current_round}, TTE: {days_to_expiry}")
        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data

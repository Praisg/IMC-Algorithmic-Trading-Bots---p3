"""
One of the popular methods of lot density control is the Kelly criterion. The Kelly Criterion is a mathematical equation that helps determine the
 optimal bet size based on the probability of winning and the ratio of wins to losses. 
We will use the distance between the model's prediction and 0.5 as the winning probability. The closer the model's prediction is to 0.5, the lower
 the probability of winning, and the smaller the bet size should be
In this function, I added the probability_of_winning and optimal_volume variables. probability_of_winning stores the probability of winning calculated 
as a distance between model forecast and 0.5 multiplied by 2. optimal_volume contains the optimal bet size calculated using the Kelly criterion.

In the 'if daily_drop > 0.05:' block, I decrease optimal_volume by 10% in increments of 0.01 lot. I also added the 'elif current_balance > peak_balance:' condition,
 which checks whether the current account balance has exceeded the previous peak level. If yes, I recalculate optimal_volume for the current balance and win/loss ratio,
   while peak_balance is updated.
This Kelly lot size management system will allow me to automatically optimize my bet size based on the probability of winning and the win/loss
 ratio. This way I can maximize profits and minimize the risk of drawdown. 

"""

def online_trading(symbol, features, model):
    terminal_path = "C:/Program Files/RoboForex - MetaTrader 5/Arima/terminal64.exe"

    if not mt5.initialize(path=terminal_path):
        print("Error: Failed to connect to MetaTrader 5 terminal")
        return

    open_trades = 0
    e = None
    attempts = 30000

    # Get the current account balance
    account_info = mt5.account_info()
    account_balance = account_info.balance

    # Set the initial volume for opening trades
    volume = 0.1

    # Set the initial peak balance
    peak_balance = account_balance

    while True:
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is not None:
            break
        else:
            print("Error: Instrument not found. Attempt {} of {}".format(_ + 1, attempts))
            time.sleep(5)

    while True:
        price_bid = mt5.symbol_info_tick(symbol).bid
        price_ask = mt5.symbol_info_tick(symbol).ask

        signal = model.predict(features)

        positions_total = mt5.positions_total()

        # Calculate the daily drop in account balance
        account_info = mt5.account_info()
        current_balance = account_info.balance
        daily_drop = (account_balance - current_balance) / account_balance

        # Calculate the probability of winning based on the distance between the model's prediction and 0.5
        probability_of_winning = abs(signal[-1] - 0.5) * 2

        # Calculate the optimal volume for opening trades using the Kelly criterion
        optimal_volume = (probability_of_winning - (1 - probability_of_winning) / risk_reward_ratio) / risk_reward_ratio * account_balance / price_ask

        # Reduce the volume for opening trades by 10% with a step of 0.01 lot for each day of daily drop
        if daily_drop > 0.02:
            optimal_volume -= 0.01
            optimal_volume = max(optimal_volume, 0.01)
        elif current_balance > peak_balance:
            optimal_volume = (probability_of_winning - (1 - probability_of_winning) / risk_reward_ratio) / risk_reward_ratio * account_balance / price_ask
            peak_balance = current_balance

        # Set the volume for opening trades
        volume = optimal_volume

        for _ in range(attempts):
            if positions_total < MAX_OPEN_TRADES and signal[-1] > 0.5:
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": price_ask,
                    "sl": price_ask - 150 * symbol_info.point,
                    "tp": price_ask + 800 * symbol_info.point,
                    "deviation": 20,
                    "magic": 123456,
                    "comment": "Test deal",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK,
                }
            elif positions_total < MAX_OPEN_TRADES and signal[-1] < 0.5:
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_SELL,
                    "price": price_bid,
                    "sl": price_bid + 150 * symbol_info.point,
                    "tp": price_bid - 800 * symbol_info.point,
                    "deviation": 20,
                    "magic": 123456,
                    "comment": "Test deal",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK,
                }
            else:
                print("No signal to open a position")
                return None

            result = mt5.order_send(request)

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                if signal[-1] < 0.5:
                    print("Buy position opened")
                    open_trades += 1
                elif signal[-1] > 0.5:
                    print("Sell position opened")
                    open_trades += 1
                return result.order
            else:
                print("Error: Trade request not executed, retcode={}. Attempt {}/{}".format(result.retcode, _ + 1, attempts))
                time.sleep(3)

        time.sleep(4000)
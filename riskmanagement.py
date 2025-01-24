"""automatically reduces the volume of trades when the account balance draws down, using the tools of the MetaTrader 5 library for Python.

The basic rules of the system:

    Daily retrieval of current account balance - every day the system will retrieve the current account balance to analyze the changes.

    Reducing the volume of trades during a drawdown - if the balance has fallen by more than 2% in a day, the system will automatically 
    reduce the volume of opened deals by 10%. This happens in 0.01 lot increments to gradually reduce risks.

    Additional volume reduction as balance continues to decline - if the balance continues to decline, then each day the volume of deals
      will be reduced by an additional 10% and by 0.01 lots, ensuring further capital protection.

    Revert to original volume after balance restoration - when the current account balance exceeds the previous peak, the system 
    automatically returns the trading volume to the original value. This helps restore full trading activity after a temporary drop
      in volume due to a drawdown.

New variables have been added to the online_trading function: account_balance - to store the current balance, peak_balance - to store the 
previous peak balance level and daily_drop - to track the daily drawdown. These variables are used to implement risk management logic.
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
    volume = 0.3

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

        # Reduce the volume for opening trades by 10% with a step of 0.01 lot for each day of daily drop
        if daily_drop > 0.02:
            volume -= 0.01
            volume = max(volume, 0.01)
        elif current_balance > peak_balance:
            volume = 0.3
            peak_balance = current_balance

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
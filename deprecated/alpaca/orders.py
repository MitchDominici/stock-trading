from src.trading.brokerages.alpaca.api import get_api
import yfinance as yf
from src.constants import global_live_trading
from src.utils.logger import log_trade


def get_atr(symbol, period=14):
    try:
        # Fetch historical data
        df = yf.download(symbol, period="1mo", interval="1d")

        # Calculate True Range
        df['HL'] = df['High'] - df['Low']
        df['HC'] = abs(df['High'] - df['Close'].shift(1))
        df['LC'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['HL', 'HC', 'LC']].max(axis=1)

        # Calculate ATR
        df['ATR'] = df['TR'].rolling(window=period).mean()

        # Return the latest ATR value
        return df['ATR'].iloc[-1]
    except Exception as e:
        print(f"Error fetching ATR for {symbol}: {e}")


def calculate_order_qty(symbol):
    try:
        api = get_api()
        balance = api.get_account().cash
        max_investment = 0.25 * float(balance)
        latest_price = api.get_latest_trade(symbol).price
        qty = int(max_investment / latest_price)
        return qty
    except Exception as e:
        print(f"Error fetching order quantity for {symbol}")


def place_order(symbol, action, qty):
    try:
        api = get_api(global_live_trading)

        open_positions = api.list_positions()
        if any(position.symbol == symbol for position in open_positions) and action == 'buy':
            print(f"An open position for {symbol} already exists.")
            return

        current_price = float(api.get_last_trade(symbol).price)
        atr_value = get_atr(symbol)

        if action == 'buy':
            stop_loss_price = current_price - 2 * atr_value  # Setting stop-loss at 2x ATR below current price
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='market',
                time_in_force='gtc',
                order_class='bracket',
                stop_loss={'stop_price': stop_loss_price}
            )
            log_trade(symbol, action, current_price, qty)
            print('Placed buy order')
        elif action == 'sell':
            # Only sell if you have a position
            try:
                position = api.get_position(symbol)
                if position.qty <= qty:
                    api.submit_order(symbol=symbol, qty=position.qty, side='sell', type='market', time_in_force='gtc')
                else:
                    api.submit_order(symbol=symbol, qty=qty, side='sell', type='market', time_in_force='gtc')
                print('Placed sell order')
                log_trade(symbol, action, current_price, qty)
            except:
                print(f"No existing position for {symbol} to sell.")
    except Exception as e:
        print(f"Error placing order for {symbol}: {e}")

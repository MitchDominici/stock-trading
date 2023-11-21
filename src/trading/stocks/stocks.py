import os
import time
import pandas as pd
import yfinance as yf
from src.trading.brokerages.alpaca.api import get_api
from src.trading.brokerages.alpaca.tickers import get_tickers_from_source

script_dir = os.path.dirname(os.path.abspath(__file__))
yahoo_stocks_path = os.path.join(script_dir, '../../../..', 'data/yahoo_stocks')
SAVE_DIR = '../../../data/yahoo_stocks'
OTC_URL = 'https://otcmarkets.com'


def get_latest_price(symbol):
    api = get_api()
    try:
        trade = api.get_latest_trade(symbol)
        return trade.price
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def get_stock_data(symbol, timeframe='1D'):
    """Example return data: [Bar({   'c': 22.66,
    'h': 22.67,
    'l': 21.84,
    'n': 12504,
    'o': 21.85,
    't': '2023-10-16T04:00:00Z',
    'v': 1110925,
    'vw': 22.344809})]"""
    print('\nGetting stock data for', symbol)
    api = get_api()

    # Ensure the given timeframe is valid
    valid_timeframes = ['minute', '1Min', '5Min', '15Min', '1D']
    if timeframe not in valid_timeframes:
        raise ValueError(f"Invalid timeframe '{timeframe}'. Must be one of {valid_timeframes}.")

    df = pd.DataFrame(api.get_bars(symbol, timeframe=timeframe, limit=1, adjustment='raw'))
    return df


def get_stock_data_from_yahoo(period=14, ticker_source='otc' or 'sp500'):
    print("get_yahoo_momentum_stocks")
    tickers = get_tickers_from_source(ticker_source)

    stock_momentum = {}
    stock_data = []

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    count = 0
    for symbol in tickers:
        print(f"\nProcessing {symbol} ({count}/{len(tickers)})")

        # Path for local data file
        file_path = os.path.join(SAVE_DIR, f"{symbol}.csv")

        if os.path.exists(file_path):
            # Load the data from local file if it exists
            print(f"Loading {symbol} from local file...")
            data = pd.read_csv(file_path, parse_dates=True, index_col='Date')
        else:
            time.sleep(0.1)

            latest_price = get_latest_price(symbol)
            if latest_price is not None and latest_price >= 5:
                print(f"Skipping {symbol} because latest price is {latest_price} > 5")
                count += 1
                continue  # Skip this ticker if the price is >= 5
            data = yf.download(symbol, start="2022-01-01", end="2023-10-01")
            print("**********************************")
            data.to_csv(file_path)

        if not data.empty and data['Close'].iloc[-1] < 5 and data['Volume'].iloc[-1] > 750000:
            data['ROC'] = ((data['Close'] - data['Close'].shift(period)) / data['Close'].shift(period)) * 100
            stock_momentum[symbol] = data['ROC'].iloc[-1]
            stock_data.append(data)

        count += 1

    # Sort stocks by momentum in descending order
    sorted_stocks = sorted(stock_momentum.items(), key=lambda x: x[1], reverse=True)

    # write_json_array_to_file('../../data/yahoo_momentum_stocks.json', sorted_stocks)

    return sorted_stocks, stock_data


def get_alpaca_momentum_stocks(timeframe='1Min'):
    print("get_alpaca_momentum_stocks")
    api = get_api()

    assets = api.list_assets()
    momentum_stocks = []

    for asset in assets:
        if asset.tradable:
            try:
                symbol = asset.symbol

                print("symbol: ", symbol)

                bars = get_stock_data(symbol, timeframe)

                # current_volume = bars.volume

                # print("current_volume: ", current_volume)

                # if current_volume < 750000:
                #     print(f"Skipping {asset.symbol} because volume is {current_volume} < 750000")
                #     continue

                # Fetch the latest bar for the asset
                # bars = api.get_bars(
                #     asset.symbol,
                #     timeframe=timeframe,
                #     limit=1,
                #     adjustment='raw'
                # ).df



                last_price = bars['close'].iloc[0]

                if 0.1 <= last_price <= 5.0:  # Filtering for penny stocks in the range of $0.5 to $5
                    momentum_stocks.append(asset.symbol)

            except:
                print(f"Error fetching data for {asset.symbol}")
                pass  # Skip any stocks that cause an exception (e.g., due to lack of data)
        else:
            print(f"Skipping {asset.symbol} because it is not tradable")
    # write_json_array_to_file('data/alpaca_momentum_stocks.json', momentum_stocks)
    return momentum_stocks

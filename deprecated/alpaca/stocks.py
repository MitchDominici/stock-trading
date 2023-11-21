import os
import time
import traceback
import pandas as pd
import yfinance as yf
from alpaca.data import StockHistoricalDataClient, StockBarsRequest, TimeFrame
from src.constants import global_stock_exchanges
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


def get_alpaca_momentum_stocks(bar_interval='1Min'):
    print("get_alpaca_momentum_stocks")
    api = get_api()

    # Initialize the StockHistoricalDataClient for fetching historical data
    data_client = StockHistoricalDataClient(api_key=api._api_key, secret_key=api._secret_key)

    assets = api.get_all_assets()
    momentum_stocks = []

    for asset in assets:
        if asset.tradable and asset.exchange in global_stock_exchanges:  # focusing on major exchanges
            try:
                symbol = asset.symbol
                print("symbol: ", symbol)
                # get start and end dates which should be 1 minute apart and current time
                timeframe = TimeFrame(1, 'Min')
                stock_bars_request = StockBarsRequest(symbol_or_symbols=[symbol], timeframe=timeframe, limit=50)

                # Fetch the latest bars for the asset
                bars = data_client.get_stock_bars(stock_bars_request)
                print("Bars received for {}: ".format(symbol), bars)

                # Calculate momentum (e.g., rate of change)
                bars['momentum'] = bars['close'].pct_change(periods=14)  # Adjust period for momentum calculation

                # Filter based on volume and momentum
                if bars['volume'].iloc[-1] > 750000 and bars['momentum'].iloc[-1] > 0:  # Example criteria
                    momentum_stocks.append((symbol, bars['momentum'].iloc[-1]))

            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                traceback.print_exc()
            break
    # Sort stocks by momentum in descending order
    momentum_stocks.sort(key=lambda x: x[1], reverse=True)

    return momentum_stocks


alpaca_momentum_stocks = get_alpaca_momentum_stocks()
print("alpaca_momentum_stocks: ", alpaca_momentum_stocks)

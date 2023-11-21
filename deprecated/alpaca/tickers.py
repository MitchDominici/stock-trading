import os

import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))


def get_sp500_tickers():
    # Get the constituents of the S&P 500
    table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = table[0]
    tickers = df['Symbol'].tolist()
    return tickers


def get_otc_tickers_from_csv():
    # Read the CSV file into a pandas DataFrame
    otc_tickers_file_path = os.path.join(script_dir, '../../../..', 'data/Stock_Screener.csv')
    df = pd.read_csv(otc_tickers_file_path)

    # Extract the 'Symbol' column to get the tickers
    tickers = df['Symbol'].tolist()

    return tickers


def get_tickers_from_source(ticker_source='otc' or 'sp500'):
    if ticker_source == 'otc':
        return get_otc_tickers_from_csv()
    elif ticker_source == 'sp500':
        return get_sp500_tickers()


import pandas as pd

from src.ml.data_cleaner import clean_stock_prices
from src.ml.feature_engineer import engineer_features_for_stock_prices
from src.ml.label_generator import LabelGenerator
from src.models.stock.stock_price import StockPrice
from src.utils.stock_logger import StockLogger
from src.utils.utils import extract_symbols, convert_timestamp_format

logger = StockLogger("AlpacaUtils")


def calculate_atr(data, window=14):
    """
    Calculate the Average True Range (ATR).

    :param data: DataFrame with columns 'High', 'Low', and 'Close'.
    :param window: The period over which to calculate the ATR.
    :return: ATR as a float.
    """
    high_low = data['high'] - data['low']
    high_close = (data['high'] - data['close'].shift()).abs()
    low_close = (data['low'] - data['close'].shift()).abs()

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)

    atr = true_range.rolling(window=window).mean()

    return atr.iloc[-1]


def aggregate_stock_data(stock_prices):
    aggregated_data = {}

    # Aggregate stock prices
    for entry in stock_prices:
        symbol = entry.symbol
        if symbol not in aggregated_data:
            aggregated_data[symbol] = []
        aggregated_data[symbol].append(entry)

    return aggregated_data


def process_stock_data(stock_price_data, timeframe_unit, stock_filter):
    stock_prices = []
    for stock in stock_price_data:
        for index, bar in stock.df.iterrows():
            stock_price = get_stock_price_from_bar(bar, index, stock_filter, timeframe_unit)
            if stock_price:
                stock_prices.append(stock_price)

    return stock_prices


def get_stock_price_from_bar(bar, index, stock_filter, timeframe_unit):
    try:
        symbol = index[0]
        timestamp = str(index[1])

        stock_price = StockPrice.from_alpaca_bar(symbol, bar, timeframe_unit, timestamp)

        if stock_filter is None or (
                stock_filter.price_is_valid(stock_price.close) and stock_filter.volume_is_valid(
            stock_price.volume)):
            return stock_price

    except Exception as e:
        logger.log_error(e, f"Error getting stock price from bar: {e}", True)


def prepare_symbols(symbols):
    if not isinstance(symbols, list):
        symbols = [symbols]
    if not isinstance(symbols[0], str):
        symbols = extract_symbols(symbols)
    return symbols


def convert_stock_price_list_to_df(stock_prices):
    grouped_stock_prices = {}
    for sp in stock_prices:
        if sp.symbol not in grouped_stock_prices:
            grouped_stock_prices[sp.symbol] = []
        grouped_stock_prices[sp.symbol].append(sp)

    # Step 2: Convert each group into a DataFrame
    dataframes = []
    for symbol, prices in grouped_stock_prices.items():
        # Convert the StockPrice objects to dictionaries
        dicts = [price.to_dict() for price in prices]

        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(dicts)

        # Optionally, you might want to set the index to the timestamp
        # df.set_index('timestamp', inplace=True)
        # df.drop(columns=['id'], inplace=True)

        # Sort the DataFrame by most recent timestamp
        df.sort_values(by='timestamp', ascending=False, inplace=True)

        # Add the DataFrame to the list
        dataframes.append(df)
    return dataframes


def get_inserted_prediction_stock_price_id_and_tmstmp(predictions):
    prediction_list = []

    # Loop to convert predictions to a list of tuples (timestamp, symbol)
    for prediction in predictions:
        timestamp = convert_timestamp_format(str(prediction[0]))
        stock_price_id = prediction[1]
        symbol = prediction[2]

        prediction_list.append((timestamp, stock_price_id, symbol))

    # Sort the list by timestamp
    prediction_list.sort(key=lambda x: x[0], reverse=True)

    # Convert the timestamps back to string if necessary
    sorted_predictions = [(pred[0], pred[1], pred[2]) for pred in prediction_list]

    return sorted_predictions


def calculate_stop_loss(entry_price, atr, multiplier=2):
    """
    Calculate the stop-loss price.

    :param entry_price: The price at which the asset was bought.
    :param atr: The current Average True Range.
    :param multiplier: The number of ATRs to subtract from the entry price.
    :return: Stop-loss price as a float.
    """
    stop_loss_price = entry_price - (atr * multiplier)
    return stop_loss_price


def fetch_and_prepare_data(indicators_to_use, stock_prices_list):
    """
    Fetches the latest market data for the given symbol and preprocesses it for the model.
    """
    label_generator = LabelGenerator()
    # Fetch latest data using Alpaca API (implement this based on your data needs)
    stock_price_dataframes = convert_stock_price_list_to_df(stock_prices_list)
    # Apply feature engineering
    stock_data_with_features = engineer_features_for_stock_prices(stock_price_dataframes,
                                                                  indicators_to_use)
    cleaned_stock_data_w_features = clean_stock_prices(stock_data_with_features)
    # Generate labels
    labeled_stock_data = label_generator.generate_labels_for_stocks_prices(cleaned_stock_data_w_features)
    return labeled_stock_data

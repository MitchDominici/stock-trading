import pandas as pd

from src.utils.stock_logger import StockLogger


def _label_stock(data, threshold=0.03):
    """
    Creates labels based on future price movement.

    :param data: DataFrame containing stock data.
    :param threshold: Percentage change threshold to determine buy/sell.
    :return: Series with labels.
    """
    return ((data['future_close'] - data['close']) / data['close']).apply(
        lambda x: 'buy' if x > threshold else ('sell' if x < -threshold else 'hold')
    )


class LabelGenerator:
    logger = StockLogger()

    def __init__(self, look_forward=5):
        """
        Initializes the label generator with a look-forward period.
        """
        self.look_forward = look_forward
        self.numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']

    def generate_labels(self, stock_data):
        """
        Generates labels for each stock in the dataset.

        :param stock_data: Dictionary of DataFrames with stock data and features.
        :return: Stock data with labels added.
        """

        # Convert columns to numeric data types
        stock_data[self.numeric_columns] = stock_data[self.numeric_columns].apply(pd.to_numeric, errors='coerce')

        stock_data['future_close'] = stock_data['close'].shift(-self.look_forward)
        stock_data.dropna(subset=['future_close'], inplace=True)  # Remove rows with NaN in future_close
        stock_data['label'] = _label_stock(stock_data)
        stock_data.drop(columns=['future_close'], inplace=True)  # Optional: remove if future close not needed later

        return stock_data

    def generate_labels_for_stocks_prices(self, stock_prices):
        """
        Generates labels for each stock in the dataset.

        :param stock_prices: Dictionary of DataFrames with stock data and features.
        :return: Stock data with labels added.
        """
        ret_val = []
        for stock_price_df in stock_prices:
            processed_df = self.generate_labels(stock_price_df)
            ret_val.append(processed_df)
        return ret_val


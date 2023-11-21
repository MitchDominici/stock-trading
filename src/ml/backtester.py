import pandas as pd

from src.utils.stock_logger import StockLogger


class Backtester:
    logger = StockLogger()

    results = {
        'total_trades': 0,
        'total_profit': 0.0,
        'average_profit': 0.0
    }
    prediction = None

    def __init__(self, data, symbol, model_features, model):
        """
        Initializes the Backtester with data and an optional machine learning model.

        :param data: DataFrame containing historical data and labels/predictions.
        :param model: Trained ML model for making predictions (optional).
        """
        self.data = data
        self.model = model
        self.symbol = symbol
        self.model_features = model_features

    def run_backtest(self):
        total_trades = 0
        total_profit = 0.0

        count = 0
        for index, row in self.data.iterrows():
            if self._should_buy(row):
                # self.logger.logger.info(f"buying...")
                buy_price = row['close']
                sell_price = self._simulate_sell(count)
                profit = sell_price - buy_price
                total_profit += profit
                total_trades += 1
            count += 1

        average_profit = total_profit / total_trades if total_trades > 0 else 0

        self.results['total_trades'] = total_trades
        self.results['total_profit'] = total_profit
        self.results['average_profit'] = average_profit
        return self.results

    def _should_buy(self, row):
        """
        Determines whether to buy based on the given row of data.

        :param row: A row from the DataFrame.
        :return: True if buying condition is met, False otherwise.
        """
        # Implement your buying logic here
        # Example: Buy if the label is 'buy' or model predicts 'buy'
        row_filtered = row[self.model_features]
        if self.model:
            # Convert row to numpy array and reshape for single prediction
            prediction = self.model.predict(row_filtered.values.reshape(1, -1))
            # Assuming 1 represents 'buy' and 0 represents 'sell' after encoding
            return prediction[0] == 1 or 'buy'
        else:
            # Assuming 'buy' is encoded as 1
            return row['label'] == 1

    def _simulate_sell(self, current_index):
        """
        Simulates selling of the stock bought at current_index.

        :param current_index: The index in the DataFrame where the buy occurred.
        :return: Simulated sell price.
        """
        # Implement your selling logic here
        # Example: Sell after a fixed number of days or when certain conditions are met
        try:
            # self.logger.logger.info("simulating sell...")
            if isinstance(current_index, int):
                sell_index = min(current_index + 5, len(self.data) - 1)  # Example: Sell after 5 days

                sell_price = self.data.iloc[sell_index]['close']

                if pd.notna(sell_price):
                    return sell_price
                else:
                    self.logger.logger.info(f"No valid sell price at index {sell_index}")
                    return None  # or some default value if appropriate
        except Exception as e:
            self.logger.log_error(e, f"Error simulating sell", True)
            return None

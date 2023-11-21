from datetime import datetime

import backtrader as bt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from src.trading.brokerages.alpaca.back_tests.custom_vwap import CustomVWAP
from src.trading.brokerages.alpaca.stocks import get_stock_data_from_yahoo
from src.ml.model import save_model

dataset = []


class DataCollectorStrategy(bt.Strategy):
    params = (
        ('look_ahead', 5),  # Look ahead n days to decide the label
    )

    def __init__(self):
        bbands = bt.indicators.BollingerBands(self.data)
        self.lower = bbands.bot  # Bottom Bollinger Band
        self.mid = bbands.mid  # Middle Bollinger Band (SMA)
        self.upper = bbands.top  # Top Bollinger Band
        self.macd = bt.indicators.MACD(self.data)
        self.vwap = CustomVWAP(self.data)
        self.future_prices = []  # A list to store future prices

    def start(self):
        # This method is called once before the start of backtesting
        # Store all prices in the list for later access
        self.future_prices = list(self.data.close.array)

    def next(self):
        # If we don't have enough data left for look_ahead days, exit the method
        if len(self.future_prices) <= self.params.look_ahead:
            # print(f"Insufficient data for {self.data._name}")
            return

        features = [
            self.lower[0],
            self.mid[0],
            self.upper[0],
            self.vwap[0],
            self.macd.macd[0],
            self.macd.signal[0]
        ]

        future_price = self.future_prices[self.params.look_ahead]
        if future_price > self.data.close[0]:
            label = 1
        else:
            label = 0

        dataset.append((features, label))
        # print(f"Appended data for {self.data._name}: Features - {features}, Label - {label}")
        # Remove the oldest price (i.e., the current day's price)
        # so that the next day's price becomes the current price
        self.future_prices.pop(0)

    def stop(self):
        # This method is called once after the end of backtesting
        pass


def run_back_test():
    print("Running back test...")

    stock_symbols, stock_data = get_stock_data_from_yahoo()
    count = 0
    for df in stock_data:
        # print(f"Data points for {stock_symbols[count]}: {len(df)}")
        # if not df.empty:
        #     print(df.head())  # Print the first 5 rows
        data = bt.feeds.PandasData(dataname=df)
        cerebro = bt.Cerebro()
        cerebro.addstrategy(DataCollectorStrategy)
        cerebro.adddata(data)
        cerebro.run()
        count += 1

    if not dataset:
        print("Dataset is empty.")
        exit()

    print('Back test completed.')


def train_model():
    run_back_test()

    print('Training the model...')
    X, y = zip(*dataset)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)
    # Training the model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    # Saving the model
    timestamp = datetime.now().strftime("%Y-%m-%d__%H_%M_%S")

    save_model(model, f"back_test_model_{timestamp}.pkl")
    # Validation
    accuracy = model.score(X_val, y_val)
    print(f"Validation Accuracy: {accuracy * 100:.2f}%")


train_model()

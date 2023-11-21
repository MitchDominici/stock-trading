# run_trader_bot.py
import base64
import json
import pickle

import pandas as pd

from src.batch_jobs.batch_job import BatchJob
from src.config.config_manager import ConfigManager
from src.constants import global_sell_signals, global_paper_trading
from src.ml.data_cleaner import clean_stock_prices
from src.ml.feature_engineer import engineer_features_for_stock_prices
from src.ml.label_generator import LabelGenerator
from src.ml.model_training import ModelTraining, get_model_data_for_insert
from src.models.stock.custom_time_frame import CustomTimeFrame, TimeFrameEnum
from src.models.stock.stock_analysis import StockAnalysis
from src.trading.brokerages.alpaca.alpaca_manager import AlpacaManager
from src.trading.brokerages.alpaca.alpaca_utils import convert_stock_price_list_to_df, calculate_atr, \
    fetch_and_prepare_data
from src.utils.utils import generate_date_range, extract_symbols, get_model_name


class RunTraderBot(BatchJob):
    stock_filter = None
    model = None
    model_version = None
    model_id = None

    def __init__(self, indicators_to_use=None):
        super().__init__()
        if indicators_to_use is None:
            indicators_to_use = ['bb']
        self.alpaca_stock_data = AlpacaManager().get_stock_data()
        self.alpaca_bot = AlpacaManager().get_bot()  # Assuming AlpacaManager provides AlpacaBot

        self.timeframe = CustomTimeFrame.get_time_frame_from_enum(
            TimeFrameEnum.ONE_MINUTE).convert_to_alpaca_timeframe()

        self.start_date, self.end_date = generate_date_range(30)

        self.indicators_to_use = indicators_to_use
        self.model_to_use = ConfigManager().get('trading_configs', 'model_to_use')

        self.process_name = 'run_trader_bot'

    def run(self):
        run_id = None
        try:
            run_id = self.stock_trader_db.run_start(process_name=self.process_name)
            self.use_ml_model()
            self.stock_trader_db.run_stop(run_id=run_id)
        except Exception as e:
            self.logger.log_error(e, f"Error running {self.process_name}", True)
            if run_id:
                self.stock_trader_db.run_stop(run_id=run_id, success=False)

    def use_ml_model(self):
        open_positions = self.alpaca_bot.get_open_positions()

        model_data = self.fetch_ml_model()
        if model_data:
            self.model_version = model_data['model_version']
            self.model_id = model_data['id']
            self.logger.logger.debug(f"successfully fetched model")
            self.model = model_data['model']

        model_training = None
        market_order = None
        if not open_positions:
            self.logger.logger.debug("no open positions, checking if we should buy...")

            stocks_to_watch = self.stock_trader_db.get_watchlist()

            symbols = extract_symbols(stocks_to_watch)
            for symbol in symbols:
                prediction, model_training = self.make_trading_decision(self.indicators_to_use,
                                                                        symbol=symbol,
                                                                        timeframe=self.timeframe,
                                                                        start_date=self.start_date,
                                                                        end_date=self.end_date)

                if prediction == 'buy':
                    self.logger.logger.debug(f"buying stock: {symbol}")
                    stock_prices_list = self.alpaca_stock_data.get_stock_data(symbols=symbol, timeframe=self.timeframe,
                                                                              start_date=self.start_date,
                                                                              end_date=self.end_date)
                    # Fetch latest data using Alpaca API (implement this based on your data needs)
                    stock_price_dataframes = convert_stock_price_list_to_df(stock_prices_list)
                    atr = calculate_atr(stock_price_dataframes)
                    self.logger.logger.debug(f"atr: {atr}")

                    market_order = self.alpaca_bot.buy(symbol, atr)

        else:
            position = open_positions[0]

            open_orders = self.alpaca_bot.get_open_orders()
            for order in open_orders:
                if order.symbol == position.symbol:
                    self.logger.logger.debug("already have a sell order placed, skipping...")
                    return
                symbol = position.symbol
                prediction, model_training = self.make_trading_decision(self.indicators_to_use,
                                                                        symbol=symbol,
                                                                        timeframe=self.timeframe,
                                                                        start_date=self.start_date,
                                                                        end_date=self.end_date)
                if prediction == 'sell':
                    self.logger.logger.debug(f"selling stock: {symbol}")
                    market_order = self.alpaca_bot.sell(position)

        if model_training is not None:
            self.insert_ml_model(model_training)

        if market_order is not None:
            self.insert_market_order(market_order)

    def insert_market_order(self, market_order):
        try:
            self.logger.logger.debug(f"inserting market order: {market_order}")
            executed_trade = [{
                'strategy_id': 'ce4ebb2a-5d3c-4a71-b148-a0efd58fb350',
                'symbol': market_order.symbol,
                'quantity': market_order.qty,
                'trade_type': market_order.side,
                'price': market_order.filled_avg_price,
                'trade_time': market_order.filled_at,
                'account_id': 'f5564709-6079-4212-aa0c-228f8473a7db',
                'status': 'filled',
                'paper_trade': global_paper_trading,

            }]
            self.stock_trader_db.insert(executed_trade=executed_trade, proc_name="trading.insert_executed_trade")

        except Exception as e:
            self.logger.log_error(e, f"Error inserting market order: {market_order}", True)

    def make_trading_decision(self, indicators_to_use, symbol=None, timeframe=None, start_date=None,
                              end_date=None):
        """
        Uses the ML model to make a trading decision for the given symbol.
        """
        # Fetch and prepare data
        self.logger.logger.debug(f"Making trading decision for {symbol}")

        predictions = self.fetch_predictions_for_symbol(symbol)
        self.logger.logger.debug(f"predictions: {predictions}")
        if predictions:
            latest_prediction = predictions[0]  # Assuming the first one is the latest
            prediction_value = latest_prediction[2]  # Adjust index based on your data structure

            return prediction_value, None

        stock_price = self.alpaca_stock_data.get_stock_data(symbols=symbol, timeframe=self.timeframe,
                                                            start_date=self.start_date)
        data_for_prediction = fetch_and_prepare_data(indicators_to_use, stock_price)
        prediction = 'hold'
        model_training = None

        for df in data_for_prediction:
            # Load the trained model (ensure your model is accessible here)
            df.sort_values(by=['timestamp'], inplace=True, ascending=False)
            # model = ModelTraining(data_for_prediction, model)
            model_training = ModelTraining(df, self.model, self.model_version, self.model_id)
            # Make a prediction
            model_training.prepare_data()
            model_training.train_model()
            model_training.evaluate_model()
            prediction = model_training.predictions[0]

        self.logger.logger.debug(f"prediction: {prediction}")

        return prediction, model_training

    def insert_ml_model(self, trainer):
        model_data = get_model_data_for_insert(trainer, self.indicators_to_use)
        return self.stock_trader_db.insert(ml_model=model_data, proc_name="machine_learning.insert_model")

    def use_custom_calcs_zzz(self):
        open_positions = self.alpaca_bot.get_open_positions()
        if not open_positions:
            self.buy()
        else:
            self.sell(open_positions[0])

    def buy(self):
        stocks_to_watch = self.stock_trader_db.get_watchlist()
        self.logger.logger.debug(f"stocks_to_watch: {json.dumps(stocks_to_watch, indent=4, sort_keys=True)}")

        for stock in stocks_to_watch:
            quote = self.alpaca_bot.get_quote_for_symbol(stock.symbol)
            self.logger.logger.debug(f"quote.ask_price: {quote.ask_price}")
            self.logger.logger.debug(f"stock.target_buy_price: {stock.target_buy_price}")

            # todo refine this to make it more accurate
            if quote.ask_price <= stock.target_buy_price:
                self.logger.logger.debug(f"buying stock: {stock.symbol}")
                self.alpaca_bot.buy(stock.symbol)
                break

    def sell(self, position):
        self.logger.logger.debug("determining if we should sell...")

        open_orders = self.alpaca_bot.get_open_orders()
        for order in open_orders:
            if order.symbol == position.symbol:
                self.logger.logger.debug("already have a sell order placed, skipping...")
                return

        alpaca_timeframe = self.timeframe.convert_to_alpaca_timeframe()

        # get stock price data
        stock_price = self.alpaca_stock_data.get_stock_data(symbols=position.symbol, timeframe=alpaca_timeframe,
                                                            start_date=self.start_date)
        stock_price_data = [stock_price.to_dict() for stock_price in stock_price]
        df = pd.DataFrame(stock_price_data)

        # determine trade signal
        stock_analysis = StockAnalysis(df, self.indicators_to_use)
        trade_signal, target_buy_price, target_sell_price = stock_analysis.analyze()

        # get this for default sell price
        sell_price = self.get_default_sell_price(position, target_sell_price)

        # get current bid price for stock
        quote = self.alpaca_bot.get_quote_for_symbol(position.symbol)
        self.logger.logger.debug(f"quote.bid_price: {quote.bid_price}")

        self.logger.logger.debug(
            f"symbol: {position.symbol}, trade_signal: {trade_signal}, target_buy_price: {target_buy_price}, "
            f"target_sell_price: {sell_price}")

        if trade_signal in global_sell_signals or quote.bid_price <= sell_price:
            self.logger.logger.debug(f"selling stock: {position.symbol}")
            self.alpaca_bot.sell(position)
        else:
            self.logger.logger.debug("holding stock...")

    def get_default_sell_price(self, position, target_sell_price):
        try:
            watchlist_target_buy_price = None
            watchlist_target = self.stock_trader_db.get_watchlist(position.symbol, str(self.end_date))

            self.logger.logger.debug(f"watchlist_target: {watchlist_target}")
            if len(watchlist_target) > 0 and watchlist_target is not None:
                watchlist_target_buy_price = watchlist_target[0]['target_buy_price']

            sell_price = target_sell_price if target_sell_price is not None else watchlist_target_buy_price or 0
            return sell_price
        except Exception as e:
            self.logger.log_error(e, f"Error getting default sell price for {position.symbol}", True)
            return None

    def fetch_ml_model(self):
        model_name = get_model_name(self.model_to_use, self.indicators_to_use)
        model_data = self.stock_trader_db.get_model(model_name=model_name)
        self.logger.logger.debug(f"model: {model_data}")
        return model_data

    def fetch_predictions_for_symbol(self, symbol):
        """
        Fetches predictions for the given symbol.
        """
        return self.stock_trader_db.get_predictions_by_symbol(symbol)

    def should_sell_stock(self, symbol):
        predictions = self.fetch_predictions_for_symbol(symbol)

        # Example: Check the last 5 predictions
        recent_predictions = predictions[:5]  # Assuming the list is ordered latest first
        sell_signals = [p for p in recent_predictions if p[2] == 'sell']

        # Define a rule, e.g., sell if 3 out of the last 5 predictions are 'sell'
        if len(sell_signals) >= 3:
            return True
        return False

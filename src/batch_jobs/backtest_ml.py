# backtest_ml.py
import operator
from datetime import datetime

from src.batch_jobs.batch_job import BatchJob
from src.config.config_manager import ConfigManager
from src.ml.backtester import Backtester
from src.ml.data_cleaner import clean_stock_prices
from src.ml.feature_engineer import engineer_features_for_stock_prices
from src.ml.label_generator import LabelGenerator
from src.ml.ml_vars import ModelFeatures
from src.ml.model_training import ModelTraining, get_model_data_for_insert
from src.models.stock.custom_time_frame import CustomTimeFrame, TimeFrameEnum
from src.postgres.stock_trader_db import StockTraderDb
from src.trading.brokerages.alpaca.alpaca_utils import convert_stock_price_list_to_df, \
    get_inserted_prediction_stock_price_id_and_tmstmp, fetch_and_prepare_data
from src.utils.stock_logger import StockLogger
from src.utils.utils import extract_symbols, generate_date_range, get_uuid_as_str, \
    chunk_and_process, get_model_name


class BacktestMl(BatchJob):
    logger = StockLogger('BacktestMl')

    process_name = "backtest_ml"
    config = None

    ml_model = None
    label_generator = None
    stock_trader_db = None
    timeframe = None
    alpaca_time_frame = None
    start_date = None
    end_date = None
    stock_filter = None
    proc_name = None
    indicators_to_use = None
    model_features = None
    days_of_stock_data_to_get = None
    trainer = None
    model_to_use = None

    def __init__(self):
        super().__init__()
        self.setup_initial_parameters()

    def setup_initial_parameters(self):
        self.label_generator = LabelGenerator()
        self.stock_trader_db = StockTraderDb()
        self.config = ConfigManager()

        self.indicators_to_use = self.config.get('trading_configs', 'indicators_to_use')
        self.days_of_stock_data_to_get = int(self.config.get('trading_configs', 'days_of_stock_data_to_get'))

        self.timeframe = CustomTimeFrame.get_time_frame_from_enum(TimeFrameEnum.ONE_MINUTE)
        self.alpaca_time_frame = self.timeframe.convert_to_alpaca_timeframe()

        self.start_date, self.end_date = generate_date_range(self.days_of_stock_data_to_get)

        self.stock_filter = self.stock_trader_db.get_stock_filters(filter_codes='penny_stocks')

        self.proc_name = "machine_learning.insert_backtesting_results"

        self.model_features = ModelFeatures(self.indicators_to_use).model_features

        self.model_to_use = ConfigManager().get('trading_configs', 'model_to_use')

    def run(self):
        try:
            run_id = self.stock_trader_db.run_start(process_name=self.process_name)
            tickers = self.fetch_tickers()
            symbols = extract_symbols(tickers)
            self.perform_backtest_for_stock_prices(symbols)
            self.stock_trader_db.run_stop(run_id=run_id)
        except Exception as e:
            self.logger.log_error(e, "Error running BacktestMl", True)

    def perform_backtest_for_stock_prices(self, symbols):
        try:
            self.logger.logger.debug("Running backtest")
            stock_price_data = self.fetch_stock_data(symbols)

            labeled_data = fetch_and_prepare_data(indicators_to_use=self.indicators_to_use,
                                                  stock_prices_list=stock_price_data,)

            trainer, inserted_predictions = self.train_and_insert_model(labeled_data, stock_price_data)

            chunk_and_process(self.insert_stock_prices, stock_price_data,
                              chunk_size=self.config_manager.get_chunk_size(),
                              stringify=False, labeled_stock_data=labeled_data,
                              inserted_predictions=inserted_predictions)

            results = self.execute_backtest(labeled_data, trainer.ml_model)

            self.insert_backtest_data(results)

        except Exception as e:
            self.logger.log_error(e, "Error performing backtest", True)

    def fetch_stock_data(self, symbols):

        internal_stock_price_data = self.stock_trader_db.get_stock_prices(symbols=symbols,
                                                                          timeframe_unit=self.timeframe.unit,
                                                                          start_date=str(self.start_date),
                                                                          end_date=str(self.end_date))
        self.logger.logger.debug(f"len(internal_stock_price_data): {len(internal_stock_price_data)}")
        if len(internal_stock_price_data) > 0:
            self.logger.logger.debug(f"successfully fetched internal stock data")
            # return internal_stock_price_data

        stock_price_data = self.alpaca_stock_data.get_stock_data(symbols=symbols, timeframe=self.alpaca_time_frame,
                                                                 start_date=self.start_date,
                                                                 end_date=self.end_date)
        self.logger.logger.debug(f"successfully fetched stock data")

        return stock_price_data

    def train_and_insert_model(self, labeled_stock_data, stock_price_data):
        model_data = self.fetch_ml_model()
        if model_data:
            self.ml_model = model_data['model']
            version = model_data['model_version']
            model_id = model_data['id']
            self.logger.logger.debug(f"successfully fetched model")
            trainer = ModelTraining(labeled_stock_data, self.ml_model, version, _id=model_id)

        else:
            trainer = ModelTraining(labeled_stock_data)
            self.logger.logger.debug(f"successfully created trainer")
            self.ml_model = trainer.ml_model

        self.trainer = trainer

        trainer.prepare_data_for_multiple_stocks()
        self.logger.logger.debug(f"successfully prepared data")

        trainer.train_model()
        self.logger.logger.debug(f"successfully trained model")

        trainer.evaluate_model()
        self.logger.logger.debug(f"accuracy_score: {trainer.accuracy_score}")
        self.logger.logger.debug(f"classification_report: {trainer.classification_report}")

        self.trainer.id = self.insert_ml_model(trainer)[0][0]
        self.logger.logger.debug(f"successfully inserted model {self.trainer.id}")
        predictions = trainer.map_predictions(stock_price_data)
        inserted_predictions = self.insert_predictions(predictions)

        return trainer, inserted_predictions

    def execute_backtest(self, labeled_stock_df, model):
        results = []
        for labeled_stock in labeled_stock_df:
            symbol = labeled_stock['symbol'].iloc[0]

            backtester = Backtester(labeled_stock, symbol, self.model_features, model)
            backtest_results = backtester.run_backtest()

            backtest_results['symbol'] = symbol
            backtest_results['start_date'] = str(self.start_date)
            backtest_results['end_date'] = str(self.end_date)
            backtest_results['test_date'] = str(datetime.today())
            results.append(backtest_results)

        return results

    def insert_stock_prices(self, stock_price_data, labeled_stock_data, inserted_predictions):

        try:
            stock_price_dicts = [stock_price.to_dict() for stock_price in stock_price_data]
            inserted_stock_prices = self.stock_trader_db.insert_stock_prices(
                stock_prices=stock_price_dicts
            )
            self.logger.logger.debug(f"inserted_stock_prices: {len(inserted_stock_prices)}")

            inserted_stock_prices.sort(key=operator.itemgetter(0))

            predictions_list = get_inserted_prediction_stock_price_id_and_tmstmp(inserted_predictions)

            # Create a mapping of symbols to their labeled data for efficient lookup
            labels_to_insert = []
            # self.logger.logger.debug(f"labeled_stock_data: {labeled_stock_data}")
            self.logger.logger.debug(f"labeled_stock_data[0]: {labeled_stock_data[0]}")
            for labeled_data in labeled_stock_data:
                for row in labeled_data.values:
                    for prediction in predictions_list:
                        p_timestamp, p_stock_price_id, p_symbol = prediction

                        l_timestamp = row[2]
                        l_symbol = row[1]
                        l_stock_price_id = row[0]

                        if l_timestamp == p_timestamp and l_symbol == p_symbol or l_stock_price_id == p_stock_price_id:
                            label = labeled_data['label'].iloc[0]
                            labels_to_insert.append({
                                'stock_price_id': p_stock_price_id,
                                'label': label,
                                'id': get_uuid_as_str(),
                                'model_id': self.trainer.id
                            })
                            break

            # Batch insert labels
            if labels_to_insert:
                self.insert_labels(labels_to_insert)
            else:
                self.logger.logger.warning(f"No labels to insert")

        except Exception as e:
            self.logger.log_error(e, "Error inserting stock prices")

    def insert_labels(self, labels_to_insert):
        self.logger.logger.debug(f"inserting labels: {len(labels_to_insert)}")
        self.stock_trader_db.insert(label_data=labels_to_insert, proc_name="machine_learning.insert_labels")
        self.logger.logger.debug(f"inserted labels: {len(labels_to_insert)}")

    def insert_backtest_data(self, backtest_results):
        self.logger.logger.debug(f"inserting backtest results: {len(backtest_results)}")
        self.stock_trader_db.insert(backtest_result=backtest_results,
                                    proc_name="machine_learning.insert_backtesting_results")
        self.logger.logger.debug(f"inserted backtest results: {len(backtest_results)}")

    def insert_ml_model(self, trainer):
        model_data = get_model_data_for_insert(trainer, self.indicators_to_use)
        return self.stock_trader_db.insert(ml_model=model_data, proc_name="machine_learning.insert_model")

    def insert_predictions(self, predictions):
        self.logger.logger.debug(f"inserting predictions: {len(predictions)}")
        self.logger.logger.debug(f"predictions: {predictions[:2]}")
        inserted_predictions = self.stock_trader_db.insert(predictions=predictions,
                                                           proc_name="machine_learning.insert_predictions")
        self.logger.logger.debug(f"inserted predictions: {len(inserted_predictions)}")
        return inserted_predictions

    def fetch_tickers(self):
        return self.stock_trader_db.get_stocks_to_watch_w_filter(filter_code='penny_stocks')

    def fetch_ml_model(self):
        model_name = get_model_name(self.model_to_use, self.indicators_to_use)
        model_data = self.stock_trader_db.get_model(model_name=model_name)
        self.logger.logger.debug(f"model: {model_data}")
        return model_data

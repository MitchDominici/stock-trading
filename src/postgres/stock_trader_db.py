import base64
import inspect
import json
import pickle

from src.models.account_info.account import Account
from src.models.stock.custom_time_frame import CustomTimeFrame
from src.models.stock.filter import Filter
from src.models.stock.stock_price import StockPrice
from src.models.stock.stock_to_watch import StockToWatch
from src.models.stock.ticker import Ticker
from src.models.stock.watchlist_stock import WatchlistStock
from src.models.trade.signal import TradeSignal
from src.postgres.database_service import DatabaseService
from src.utils.stock_logger import StockLogger


class StockTraderDb:
    logger = StockLogger("StockTraderDb")

    stock_schema_name = "stock"
    machine_learning_schema_name = "machine_learning"
    batch_job_schema_name = "batch_job"
    trading_schema_name = "trade"
    account_info_schema_name = "account_info"

    db_service = None
    cache = {}

    def __init__(self):
        self.db_service = DatabaseService()

    def get_stock_filters(self, filter_codes=None):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.stock_schema_name}.{function_name}"

        values = [filter_codes] if filter_codes is not None else None

        return self.db_service.read(proc_name=proc_name, obj_class=Filter, filter_codes=values)

    def get_timeframes(self, timeframe_codes=None):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.stock_schema_name}.{function_name}"

        values = [timeframe_codes] if timeframe_codes is not None else None

        return self.db_service.read(proc_name=proc_name, obj_class=CustomTimeFrame, timeframe_codes=values)

    def get_stock_prices(self, symbols=None, timeframe_unit='day', start_date=None, end_date=None):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.stock_schema_name}.{function_name}"

        return self.db_service.read(proc_name=proc_name, obj_class=StockPrice, symbols=symbols,
                                    timeframe_unit=timeframe_unit, start_date=start_date, end_date=end_date)

    def get_tickers(self, symbols=None):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.stock_schema_name}.{function_name}"

        values = [json.dumps(symbols)] if symbols else None

        return self.db_service.read(proc_name=proc_name, obj_class=Ticker, symbols=values)

    def get_account_balances(self, brokerage_code=None, paper=True, timestamp=None):
        schema = "account_info"
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{schema}.{function_name}"

        return self.db_service.read(proc_name=proc_name, obj_class=Account, brokerage_code=brokerage_code, paper=paper,
                                    timestamp=timestamp)

    def get_stocks_to_watch_w_filter(self, filter_code='penny_stocks'):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.stock_schema_name}.{function_name}"

        return self.db_service.read(proc_name=proc_name, obj_class=StockToWatch, filter_code=filter_code)

    def get_watchlist(self, symbol=None, date=None):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.stock_schema_name}.{function_name}"

        return self.db_service.read(proc_name=proc_name, obj_class=WatchlistStock, symbol=symbol, date=date)

    def get_trade_signals(self):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.stock_schema_name}.{function_name}"

        return self.db_service.read(proc_name=proc_name, obj_class=TradeSignal)

    def get_model(self, model_name=None):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.machine_learning_schema_name}.{function_name}"
        ml_model = self.db_service.read(proc_name=proc_name, obj_class=None, model_name=model_name)

        try:
            encoded_model = ml_model[0][0]
            decoded_model = base64.b64decode(encoded_model)
            model = pickle.loads(decoded_model)
            return {'model': model, 'model_name': model_name, 'model_version': ml_model[0][3], 'id': ml_model[0][1]}
        except Exception as e:
            return None

    def insert_executed_trade(self, executed_trades):
        """
        Call the proc_name stored procedure.

        :param executed_trades: A JSONB array of executed trade data.
        """
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.stock_schema_name}.{function_name}"

        return self.db_service.insert(proc_name, executed_trades=executed_trades)

    def insert_tickers(self, tickers):
        """
        Call the proc_name stored procedure.

        :param proc_name: The name of the stored procedure to call.
        :param tickers: A JSONB array of account balance data.
        """
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.stock_schema_name}.{function_name}"

        return self.db_service.insert(proc_name, tickers=tickers)

    def insert_stock_prices(self, stock_prices, proc_name=None):
        """
        Call the proc_name stored procedure.

        :param stock_prices: A JSONB array of stock price data.
        :param proc_name: The name of the stored procedure to call.
        """
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.stock_schema_name}.{function_name}"

        return self.db_service.insert(proc_name, stock_prices=stock_prices)

    def insert_account_balances(self, account_balances):
        """
        Call the proc_name stored procedure.

        :param account_balances: A JSONB array of account balance data.
        """
        schema = "account_info"
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{schema}.{function_name}"

        return self.db_service.insert(proc_name, account_balances=account_balances)

    def insert_watchlist(self, watchlist):
        """
        Call the proc_name stored procedure.

        :param watchlist: A JSONB array of watchlist data.
        """
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.stock_schema_name}.{function_name}"

        return self.db_service.insert(proc_name, watchlist=watchlist)

    # def insert_technical_indicators(self, stock_price_id, bollinger_upper=None, bollinger_lower=None, macd=None,
    #                                 macd_signal=None, rsi=None, vwap=None, stochastic_k=None, stochastic_d=None):
    #     """
    #     Call the proc_name stored procedure.
    #
    #     :param stock_price_id: The id of the stock price to insert the technical indicators for.
    #     :param bollinger_upper: The bollinger upper value.
    #     :param bollinger_lower: The bollinger lower value.
    #     :param macd: The macd value.
    #     :param macd_signal: The macd signal value.
    #     :param rsi: The rsi value.
    #     :param vwap: The vwap value.
    #     :param stochastic_k: The stochastic k value.
    #     :param stochastic_d: The stochastic d value.
    #     """
    #     return self.db_service.insert_technical_indicators(stock_price_id, bollinger_upper, bollinger_lower, macd,
    #                                                        macd_signal, rsi, vwap, stochastic_k, stochastic_d)

    # def insert_labels(self, stock_price_id, label):
    #     """
    #     Call the proc_name stored procedure.
    #
    #     :param stock_price_id: The id of the stock price to insert the label for.
    #     :param label: The label to insert.
    #     """
    #     return self.db_service.insert_labels(stock_price_id, label)

    # def insert_predictions(self, stock_price_id, prediction, prediction_date, model_version):
    #     """
    #     Call the proc_name stored procedure.
    #
    #     :param stock_price_id: The id of the stock price to insert the label for.
    #     :param prediction: The prediction to insert.
    #     :param prediction_date: The date of the prediction.
    #     :param model_version: The version of the model used to make the prediction.
    #     """
    #     return self.db_service.insert_predictions(stock_price_id, prediction, prediction_date, model_version)

    # def insert_backtesting_results(self, model_id, backtest_result):
    #     """
    #     Call the proc_name stored procedure.
    #
    #     :param model_id: The id of the model used to generate the backtest results.
    #     :param backtest_result: The backtest results to insert.
    #     """
    #     self.db_service.insert_backtesting_results(model_id, backtest_result)

    # def insert_model(self, id, model_name, training_date, accuracy_score, classification_report,
    #                  model, additional_info):
    #     """
    #     Call the proc_name stored procedure.
    #
    #     :param id: The id of the model.
    #     :param model_name: The name of the model.
    #     :param training_date: The date the model was trained.
    #     :param accuracy_score: The accuracy score of the model.
    #     :param classification_report: The classification report of the model.
    #     :param model: The model.
    #     :param additional_info: Additional info about the model.
    #     """
    #     self.db_service.insert_model(id, model_name, training_date, accuracy_score,
    #                                  Json(classification_report), model,
    #                                  additional_info)

    def insert(self, proc_name, **args):
        """
        Call the proc_name stored procedure.

        :param proc_name: The name of the stored procedure to call.
        """
        return self.db_service.insert(proc_name, **args)

    def run_start(self, process_name):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.batch_job_schema_name}.{function_name}"

        run_start_result = self.db_service.insert(proc_name, run_data={'process_name': process_name})
        run_id = run_start_result[0][0]
        self.logger.logger.info(f"started process: {process_name} with run_id: {run_id}")

        return run_id

    def run_stop(self, run_id, success=True):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.batch_job_schema_name}.{function_name}"

        return self.db_service.insert(proc_name, run_data={'run_id': run_id, 'successful': success})

    def insert_run_error(self, run_id, error_message, error_stack=None, error_data=None):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.batch_job_schema_name}.{function_name}"

        data_to_insert = {
            'run_id': run_id,
            'error_message': error_message,
            'error_traceback': error_stack,
            'data': error_data
        }

        self.db_service.insert(proc_name, run_data=data_to_insert)

    def insert_run_log(self, run_id, message, data=None):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.batch_job_schema_name}.{function_name}"

        data_to_insert = {
            'run_id': run_id,
            'message': message,
            'data': data
        }
        self.db_service.insert(proc_name, log_data=data_to_insert)

    def get_predictions_by_symbol(self, symbol):
        function_name = inspect.currentframe().f_code.co_name
        proc_name = f"{self.machine_learning_schema_name}.{function_name}"

        return self.db_service.read(proc_name=proc_name, obj_class=None, symbol=symbol)

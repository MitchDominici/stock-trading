import json
import pickle

import psycopg2
from psycopg2._json import Json
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from src.config.config_manager import ConfigManager
from src.utils.stock_logger import StockLogger


class DatabaseService:
    logger = StockLogger("DatabaseService")

    _instance = None
    connection = None

    def __new__(cls):
        pg_configs = ConfigManager().get_postgres_config()
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance.dbname = pg_configs.dbname
            cls._instance.user = pg_configs.user
            cls._instance.password = pg_configs.password
            cls._instance.host = pg_configs.host
            cls._instance.port = pg_configs.port
            cls._instance.connect()
        return cls._instance

    def connect(self):
        """Connect to the PostgreSQL database server."""
        if self.connection is not None:
            return
        try:
            conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.connection = conn
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.log_error(error, f"Error connecting to {self.dbname} database", True)

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.logger.log_special("Database connection closed.")

    def insert_json_data(self, proc_name, jsonb_data):
        """
        Call the insert_json_data stored procedure.

        :param proc_name: The name of the stored procedure to call.
        :param jsonb_data: A JSONB array of historical price data.
        """
        # self.logger.log_special(f"inserting data with proc: {proc_name}")
        conn = self.connection
        cursor = conn.cursor()
        try:

            # if not isinstance(jsonb_data, str):
            #     logger.warning("converting jsonb_data to string")
            #     jsonb_data = json.dumps(jsonb_data)
            cursor.callproc(proc_name, jsonb_data)
            conn.commit()
            rows = cursor.fetchall()
            cursor.close()
            return rows

        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.log_error(error, f"Error inserting data: {error}", True)
            conn.rollback()
            if cursor:
                cursor.close()
            raise error

    def execute_query(self, sql_query, args=None, return_objects=False, obj_class=None):
        """
        Execute a query and optionally return objects.

        :param sql_query: The SQL query to execute.
        :param args: Arguments for the query.
        :param return_objects: Whether to return objects of a specified class.
        :param obj_class: The class to use for object creation.
        """
        conn = self.connection
        cursor = conn.cursor()
        try:
            cursor.execute(sql_query, args)
            if return_objects:
                rows = cursor.fetchall()
                return [obj_class(*row) for row in rows] if obj_class else rows
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.log_error(error, "Error executing query", True)
            conn.rollback()
            raise error
        finally:
            cursor.close()

    def insert(self, proc_name, **args):
        """
        Insert data using a stored procedure.

        :param proc_name: The name of the stored procedure to call.
        """

        sql_query = f"SELECT * FROM {proc_name}(%s::jsonb);"
        jsonb_data = Json(args)

        # self.logger.logger.debug(f"inserting data: {jsonb_data}")

        ret_val = self.execute_query(sql_query, (jsonb_data,), return_objects=True)

        # self.logger.logger.debug(f"ret_val: {ret_val}")

        return ret_val

    def read(self, proc_name, obj_class=None, **args):
        """
        Query data and create objects.

        :param proc_name: The name of the stored procedure to call.
        :param obj_class: The class to use for object creation.
        """
        sql_query = f"SELECT * FROM {proc_name}(%s::jsonb);"
        prepared_args = Json(args)

        # self.logger.logger.debug(f"getting data: {prepared_args}")

        return self.execute_query(sql_query, (prepared_args,), return_objects=True, obj_class=obj_class)

    # def get_model(self, model_name):
    #     """
    #     Fetches the latest version of a machine learning model by its name from the database.
    #
    #     :param model_name: The name of the model to fetch.
    #     :return: The latest version of the model.
    #     """
    #     conn = self.connection
    #     try:
    #         # Connect to your postgres DB
    #         cursor = conn.cursor()
    #         # Execute the function
    #         cursor.execute("SELECT * FROM machine_learning.get_latest_ml_model(%s)", (model_name,))
    #
    #         # Fetch and return the result
    #         result = cursor.fetchone()
    #         return result
    #
    #     except Exception as e:
    #         print(f"Error fetching the latest ML model: {e}")
    #     finally:
    #         if conn:
    #             conn.close()

    # def insert_technical_indicators(self, stock_price_id, bollinger_upper=None, bollinger_lower=None, macd=None,
    #                                 macd_signal=None, rsi=None, vwap=None, stochastic_k=None, stochastic_d=None):
    #     """
    #     Insert technical indicators into the database.
    #
    #     :param stock_price_id: ID of the stock price.
    #     :param bollinger_upper: Bollinger upper band.
    #     :param bollinger_lower: Bollinger lower band.
    #     :param macd: MACD.
    #     :param macd_signal: MACD signal.
    #     :param rsi: RSI.
    #     :param vwap: VWAP.
    #     :param stochastic_k: Stochastic K.
    #     :param stochastic_d: Stochastic D.
    #     """
    #     query = """
    #     INSERT INTO machine_learning.technical_indicators
    #     (stock_price_id, bollinger_upper, bollinger_lower, macd, macd_signal, rsi, vwap, stochastic_k, stochastic_d)
    #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    #     """
    #     values = (
    #         stock_price_id, bollinger_upper, bollinger_lower, macd, macd_signal, rsi, vwap, stochastic_k, stochastic_d
    #     )
    #     # Execute query
    #     conn = self.connection
    #     cursor = conn.cursor()
    #     cursor.execute(query, values)
    #     conn.commit()

    # def insert_labels(self, stock_price_id, label, model_id):
    #     """
    #     Insert ML labels into the database.
    #
    #     :param db_connection: Database connection object.
    #     :param stock_price_id: ID of the stock price.
    #     :param label: Label (e.g., 'buy', 'sell', 'hold').
    #     """
    #     query = """
    #     INSERT INTO machine_learning.ml_labels (stock_price_id, label, model_id)
    #     VALUES (%s, %s)
    #     """
    #     # Execute query
    #     conn = self.connection
    #     cursor = conn.cursor()
    #     cursor.execute(query, (stock_price_id, label))
    #     conn.commit()

    # def insert_predictions(self, stock_price_id, prediction, prediction_date, model_version):
    #     """
    #     Insert model predictions into the database.
    #
    #     :param db_connection: Database connection object.
    #     :param stock_price_id: ID of the stock price.
    #     :param prediction: Prediction value.
    #     :param prediction_date: Date of the prediction.
    #     :param model_version: Version of the model used for prediction.
    #     """
    #     query = """
    #     INSERT INTO machine_learning.model_predictions
    #     (stock_price_id, prediction, prediction_date, model_version)
    #     VALUES (%s, %s, %s, %s)
    #     """
    #     # Execute query
    #     conn = self.connection
    #     cursor = conn.cursor()
    #     cursor.execute(query, (stock_price_id, prediction, prediction_date, model_version))
    #     conn.commit()

    # def insert_model(self, id, model_name, training_date, accuracy_score, classification_report,
    #                     model, additional_info):
    #     """
    #     Insert ML model into the database.
    #
    #     :param id: ID of the model.
    #     :param model_name: Name of the model.
    #     :param training_date: Date the model was trained.
    #     :param accuracy_score: Accuracy score of the model.
    #     :param classification_report: Classification report of the model.
    #     :param model: The model itself.
    #     :param additional_info: Additional info about the model.
    #     """
    #     query = """
    #     INSERT INTO machine_learning.ml_models
    #     (id, model_name, training_date, accuracy_score, classification_report, model,  additional_info)
    #     VALUES (%s, %s::varchar, %s::date,  %s::numeric, %s::jsonb, %s::bytea, %s::jsonb)
    #     """
    #     # Serialize model and additional_info (if needed)
    #     serialized_model = pickle.dumps(model)
    #     serialized_additional_info = json.dumps(additional_info)
    #
    #     values = (
    #         id, model_name, training_date, accuracy_score, classification_report, serialized_model,
    #         serialized_additional_info
    #     )
    #     # Execute query
    #     conn = self.connection
    #     cursor = conn.cursor()
    #     cursor.execute(query, values)
    #     conn.commit()

    # def insert_backtesting_results(self, model_id, backtest_result):
    #     """
    #     Insert backtesting results into the database.
    #
    #     :param db_connection: Database connection object.
    #     :param model_id: ID of the model.
    #     :param backtest_result: Dictionary containing backtest results.
    #     """
    #     query = """
    #     INSERT INTO machine_learning.backtesting_results
    #     (model_id, symbol, start_date, end_date, total_trades, total_profit, average_profit)
    #     VALUES (%s, %s, %s, %s, %s, %s, %s)
    #     """
    #     values = (
    #         model_id, backtest_result['symbol'], backtest_result['start_date'],
    #         backtest_result['end_date'], backtest_result['total_trades'],
    #         backtest_result['total_profit'], backtest_result['average_profit']
    #     )
    #     # Execute query
    #     conn = self.connection
    #     cursor = conn.cursor()
    #     cursor.execute(query, values)
    #     conn.commit()



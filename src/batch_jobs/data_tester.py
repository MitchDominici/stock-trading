# data_tester.py
from src.batch_jobs.batch_job import BatchJob
from src.models.stock.custom_time_frame import TimeFrameEnum, CustomTimeFrame
from src.trading.brokerages.alpaca.alpaca_utils import convert_stock_price_list_to_df
from src.utils.stock_logger import StockLogger
from src.utils.utils import generate_date_range


class DataTester(BatchJob):
    logger = StockLogger('DataTester')
    tickers = None
    stock_filter = None
    timeframes = None

    def __init__(self):
        super().__init__()
        self.timeframe = CustomTimeFrame.get_time_frame_from_enum(TimeFrameEnum.ONE_MINUTE)
        self.start_date, self.end_date = generate_date_range(4)

        self.stock_filter = self.stock_trader_db.get_stock_filters('penny_stocks')[0]
        self.timeframes = self.stock_trader_db.get_timeframes()

    def run(self):
        try:
            # stocks_to_watch = self.get_stocks_to_watch()
            # symbols = extract_symbols_from_tickers(stocks_to_watch)

            model = self.stock_trader_db.get_model(model_name='bb')
            self.logger.logger.info(f"model: {model}")
            # self.tickers = ['AAPL', 'MSFT', 'CYTO']
            # alpaca_timeframe = self.timeframe.convert_to_alpaca_timeframe()
            # stock_prices_list = self.alpaca_stock_data.get_stock_data(symbols=self.tickers, timeframe=alpaca_timeframe,
            #                                                           start_date=self.start_date,
            #                                                           end_date=self.end_date, stock_filter=self.stock_filter)
            #
            # self.logger.logger.info(f"stock_prices_list: {len(stock_prices_list)}")
            #
            # stock_price_df = convert_stock_price_list_to_df(stock_prices_list)
            # grouped_stock_price_df = stock_price_df.groupby('symbol')
            #
            # self.logger.logger.info(f"grouped_stock_price_df: {grouped_stock_price_df}")
            # for symbol, symbol_df in grouped_stock_price_df:
            #     self.logger.logger.info(f"symbol: {symbol}")
            #     self.logger.logger.info(f"symbol_df: {symbol_df}")
            #     for index, row in symbol_df.iterrows():
            #         self.logger.logger.info(f"index: {index}")
            #         self.logger.logger.info(f"row: {row}")

        except Exception as e:
            self.logger.log_error(e, f"Error running DataTester", False)

    def get_all_tickers(self):
        try:
            all_tickers = self.stock_trader_db.get_ticker()
            self.logger.logger.info(f"all_tickers: {len(all_tickers)}")
            return all_tickers
        except Exception as e:
            self.logger.log_error(e, f"Error getting all_tickers", True)

    def get_stocks_to_watch(self):
        try:
            stocks_to_watch = self.stock_trader_db.get_stocks_to_watch_w_filter()
            self.logger.logger.info(f"stocks_to_watch: {len(stocks_to_watch)}")
            return stocks_to_watch
        except Exception as e:
            self.logger.log_error(e, f"Error getting stocks_to_watch", True)

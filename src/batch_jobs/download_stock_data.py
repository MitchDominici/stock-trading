from src.batch_jobs.batch_job import BatchJob
from src.models.stock.custom_time_frame import CustomTimeFrame, TimeFrameEnum
from src.utils.utils import chunk_and_process, extract_symbols, generate_date_range


class DownloadStockData(BatchJob):
    def __init__(self):
        super().__init__()
        self.timeframe = CustomTimeFrame.get_time_frame_from_enum(TimeFrameEnum.ONE_DAY).convert_to_alpaca_timeframe()
        self.start_date, self.end_date = generate_date_range(1)
        self.process_name = 'download_stock_data'

    def run(self):
        run_id = None
        try:
            run_id = self.stock_trader_db.run_start(process_name=self.process_name)

            tickers = self.stock_trader_db.get_tickers()

            if not tickers or len(tickers) == 0:
                return

            symbols = extract_symbols(tickers)

            self.logger.logger.debug(f"Downloading stock data for {len(symbols)} tickers")

            chunk_and_process(self.get_stock_data, symbols, chunk_size=self.config_manager.get_chunk_size(),
                              stringify=False)

            self.stock_trader_db.run_stop(run_id=run_id)
        except Exception as e:
            self.logger.log_error(e, f"Error downloading stock data: {e}", True)
            if run_id:
                self.stock_trader_db.run_stop(run_id=run_id, success=False)

    def get_stock_data(self, symbols):
        try:
            stock_price_data = self.alpaca_stock_data.get_stock_data(symbols=symbols, timeframe=self.timeframe,
                                                                     start_date=self.start_date, end_date=self.end_date)

            self.logger.logger.debug(f"Successfully fetched data for: {len(stock_price_data)} tickers")

            if not stock_price_data or len(stock_price_data) == 0:
                self.logger.logger.debug(f"No stock prices found for tickers: {symbols}")
                return

            stock_prices = [stock_price.to_dict() for stock_price in stock_price_data]

            self.logger.logger.debug(f"Beginning to load: {len(stock_prices)} stock prices")
            self.stock_trader_db.insert_stock_prices(stock_prices)
            self.logger.logger.debug(f"Successfully loaded: {len(stock_prices)} stock prices")

        except Exception as e:
            self.logger.log_error(e, f"Error getting stock data from alpaca and inserting into db: {e}", False)
            return []

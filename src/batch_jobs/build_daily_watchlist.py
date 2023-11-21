import pandas as pd
import traceback
from src.batch_jobs.batch_job import BatchJob
from src.constants import global_buy_signals
from src.models.stock.custom_time_frame import CustomTimeFrame, TimeFrameEnum
from src.models.stock.stock_analysis import StockAnalysis
from src.models.stock.watchlist_stock import WatchlistStock
from src.trading.brokerages.alpaca.alpaca_utils import convert_stock_price_list_to_df
from src.utils.utils import extract_symbols, generate_date_range


class BuildDailyWatchlist(BatchJob):
    def __init__(self):
        super().__init__()
        self.timeframe = CustomTimeFrame.get_time_frame_from_enum(
            TimeFrameEnum.ONE_MINUTE).convert_to_alpaca_timeframe()
        self.start_date, self.end_date = generate_date_range()
        self.stock_filter = self.stock_trader_db.get_stock_filters('penny_stocks')[0]
        self.process_name = 'build_daily_watchlist'

    def run(self):
        run_id = None
        try:
            run_id = self.stock_trader_db.run_start(self.process_name)

            stocks_to_watch = self.stock_trader_db.get_stocks_to_watch_w_filter(filter_code='penny_stocks')
            self.logger.logger.debug(f"stocks_to_watch: {len(stocks_to_watch)}")

            gainers = [stock for stock in stocks_to_watch if
                       stock.price_change_pct is not None and stock.price_change_pct > 10]
            self.logger.logger.debug(f"gainers: {len(gainers)}")

            symbols = extract_symbols(gainers)
            stock_price_data = self.alpaca_stock_data.get_stock_data(symbols=symbols, timeframe=self.timeframe,
                                                                     start_date=self.start_date, end_date=self.end_date)
            stock_price_dataframes = convert_stock_price_list_to_df(stock_price_data)
            watchlist = []
            for df in stock_price_dataframes:
                symbol = df['symbol'].iloc[0]

                # not enough data to analyze
                if len(df) < 20:
                    self.logger.logger.debug(f"symbol: {symbol} has less than 20 rows, skipping")
                    continue

                stock_analysis = StockAnalysis(df, ['bb'])
                trade_signal, target_buy_price, target_sell_price = stock_analysis.analyze()

                # self.logger.logger.debug(f"trade_signal: {trade_signal}")

                if target_buy_price is None or pd.isna(target_buy_price):
                    # self.logger.logger.debug(f"target_buy_price is NaN, skipping symbol: {symbol}")
                    continue

                if trade_signal in global_buy_signals:
                    last_price = df['close'].iloc[-1]

                    watchlist_stock = WatchlistStock(symbol=symbol, target_buy_price=target_buy_price,
                                                     signal=trade_signal,
                                                     last_price=last_price)
                    watchlist.append(watchlist_stock.to_dict())

            if len(watchlist) > 0:
                self.logger.logger.debug(f"inserting stocks to watch: {len(watchlist)}")
                self.stock_trader_db.insert_watchlist(watchlist)

            self.stock_trader_db.run_stop(run_id)

        except Exception as e:
            self.handle_error(e, run_id)

    def handle_error(self, e, run_id):
        self.logger.log_error(e, f"Exception in BuildDailyWatchlist: {e}", True)
        trace = traceback.format_exc()
        if run_id is not None:
            self.stock_trader_db.insert_run_error(run_id, str(e), trace, {'test': 'test'})
            self.stock_trader_db.run_stop(run_id, False)
        raise e

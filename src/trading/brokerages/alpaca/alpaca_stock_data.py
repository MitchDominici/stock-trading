# alpaca_stock_data.py
import pandas as pd
from alpaca.data import TimeFrame, StockBarsRequest
from src.trading.brokerages.alpaca.alpaca_utils import process_stock_data, prepare_symbols
from src.utils.stock_logger import StockLogger
from src.utils.utils import validate_ticker_symbol

default_time = pd.Timestamp.now(tz="America/New_York").replace(hour=0, minute=0, second=0)


class AlpacaStockData:
    logger = StockLogger("AlpacaStockData")
    brokerage_code = 'AL'

    def __init__(self, alpaca_api):
        self.trading_client_api = alpaca_api.trading_client_api
        self.stock_historical_data_client = alpaca_api.stock_historical_data_client

    def get_stock_data(self, symbols, timeframe: TimeFrame, start_date, stock_filter=None, end_date=None):
        symbols = prepare_symbols(symbols)
        self.logger.logger.info(f"Getting stock data for {len(symbols)} tickers starting at {start_date}")

        stock_bars_dict = self._get_stock_bars_from_alpaca(symbols, timeframe, start_date, end_date)
        if not stock_bars_dict:
            self.logger.logger.warning(f"No stock prices returned for {symbols}")
            return []

        return process_stock_data(stock_bars_dict, timeframe.unit.value, stock_filter)

    def _get_stock_bars_from_alpaca(self, symbols, timeframe, start_date, end_date):
        valid_symbols_data = {}
        invalid_symbols = []
        valid_stock_bars = []

        for symbol in symbols:
            if not validate_ticker_symbol(symbol):
                self.logger.logger.warning(f"Invalid symbol: {symbol}")
                invalid_symbols.append(symbol)
                continue
            try:
                stock_bars_request = StockBarsRequest(
                    symbol_or_symbols=symbol,
                    start=start_date,
                    end=end_date,
                    limit=1000000,
                    timeframe=timeframe
                )
                stock_bars = self.stock_historical_data_client.get_stock_bars(stock_bars_request)
                if stock_bars:
                    valid_stock_bars.append(stock_bars)
                    valid_symbols_data[symbol] = stock_bars
            except Exception as e:
                self.logger.log_error(e, f"Error getting stock bars for symbol {symbol}", False)
                invalid_symbols.append(symbol)

        if valid_stock_bars:
            self.logger.logger.info(f"Successfully fetched stock bars for {len(valid_stock_bars)} valid symbols.")
        else:
            self.logger.logger.warning("No valid symbols found.")
        return valid_stock_bars

    def get_all_assets(self):
        return self.trading_client_api.get_all_assets()

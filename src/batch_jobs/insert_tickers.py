import json

from src.batch_jobs.batch_job import BatchJob
from src.models.stock.ticker import Ticker
from src.postgres.stock_trader_db import StockTraderDb
from src.trading.brokerages.alpaca.alpaca_manager import AlpacaManager
from src.utils.stock_logger import StockLogger
from src.utils.utils import extract_symbols, validate_ticker_symbol


class InsertTickers(BatchJob):
    logger = StockLogger('InsertTickers')

    def __init__(self):
        super().__init__()
        self.stock_trader_db = StockTraderDb()
        self.alpaca_data = AlpacaManager().get_stock_data()

    def run(self):
        try:
            alpaca_assets = self.alpaca_data.get_all_assets()
            alpaca_symbols = extract_symbols(alpaca_assets)

            local_tickers = self.stock_trader_db.get_tickers()
            local_symbols = extract_symbols(local_tickers)

            # get array of symbols that are in alpaca but not in local
            symbols_to_insert = list(set(alpaca_symbols) - set(local_symbols))

            # now get the alpacas assets that are in the symbols_to_insert array
            tickers = []
            for asset in alpaca_assets:
                if asset.symbol in symbols_to_insert and asset.tradable and validate_ticker_symbol(asset.symbol):
                    ticker = Ticker(symbol=asset.symbol, name=asset.name, exchange=asset.exchange.name)
                    tickers.append(ticker.to_dict())

            if len(tickers) == 0:
                self.logger.logger.info(f"No tickers to insert")
                return

            self.logger.logger.info(f"Inserting {len(tickers)} tickers...")
            self.stock_trader_db.insert_tickers(tickers)
            self.logger.logger.info(f"Inserted {len(tickers)} tickers")

        except Exception as e:
            self.logger.log_error(e, "Error inserting tickers", True)

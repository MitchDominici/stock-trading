from src.config.config_manager import ConfigManager
from src.postgres.stock_trader_db import StockTraderDb
from src.trading.brokerages.alpaca.alpaca_manager import AlpacaManager
from src.utils.stock_logger import StockLogger


class BatchJob:
    def __init__(self):
        self.logger = StockLogger(self.__class__.__name__)
        # services
        self.config_manager = ConfigManager()
        self.stock_trader_db = StockTraderDb()
        self.alpaca_stock_data = AlpacaManager().get_stock_data()


    def run(self):
        raise NotImplementedError("Subclasses should implement this method.")

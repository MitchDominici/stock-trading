from src.constants import global_live_trading
from src.trading.brokerages.alpaca.alpaca_api import AlpacaApi
from src.trading.brokerages.alpaca.alpaca_bot import AlpacaBot
from src.trading.brokerages.alpaca.alpaca_stock_data import AlpacaStockData


class AlpacaManager:
    _instance = None
    _alpaca_api_instance = None
    _alpaca_bot_instance = None
    _alpaca_stock_data_instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlpacaManager, cls).__new__(cls)
            cls._instance.get_api()
        return cls._instance

    @classmethod
    def get_api(cls, live=global_live_trading):
        if cls._alpaca_api_instance is None:
            cls._alpaca_api_instance = AlpacaApi(live)
        return cls._alpaca_api_instance

    @classmethod
    def get_bot(cls):
        if cls._alpaca_bot_instance is None:
            cls._alpaca_bot_instance = AlpacaBot(cls._alpaca_api_instance)
        return cls._alpaca_bot_instance

    @classmethod
    def get_stock_data(cls):
        if cls._alpaca_stock_data_instance is None:
            cls._alpaca_stock_data_instance = AlpacaStockData(cls._alpaca_api_instance)
        return cls._alpaca_stock_data_instance


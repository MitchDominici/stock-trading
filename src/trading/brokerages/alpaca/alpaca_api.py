from alpaca.data import StockHistoricalDataClient
from alpaca.trading import TradingClient
from src.config.config_manager import ConfigManager
from src.constants import global_live_trading


class AlpacaApi:
    stock_historical_data_client: StockHistoricalDataClient = None
    trading_client_api: TradingClient = None

    def __init__(self, live=global_live_trading):
        if self.trading_client_api is None:
            alpaca_config = ConfigManager().get_alpaca_config(live)
            self.trading_client_api = TradingClient(alpaca_config.api_key, alpaca_config.api_secret, paper=not live)
            self.stock_historical_data_client = StockHistoricalDataClient(api_key=alpaca_config.api_key,
                                                                          secret_key=alpaca_config.api_secret)

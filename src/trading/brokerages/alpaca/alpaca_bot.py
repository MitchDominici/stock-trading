# alpaca_bot.py
import pandas as pd
from alpaca.data import StockLatestQuoteRequest
from alpaca.trading import MarketOrderRequest, OrderSide, TimeInForce, GetOrdersRequest, QueryOrderStatus

from src.ml.data_cleaner import clean_stock_prices
from src.ml.feature_engineer import engineer_features_for_stock_prices
from src.ml.label_generator import LabelGenerator
from src.ml.model_training import ModelTraining
from src.models.trade.trading_bot import TradingBot
from src.trading.brokerages.alpaca.alpaca_utils import convert_stock_price_list_to_df, calculate_stop_loss
from src.utils.stock_logger import StockLogger


class AlpacaBot(TradingBot):
    logger = StockLogger("AlpacaBot")

    account_balance = None
    open_positions = None

    trading_client_api = None

    def __init__(self, alpaca_api):
        super().__init__()
        self.trading_client_api = alpaca_api.trading_client_api

    def get_account_balance(self):
        if not self.account_balance:
            self.account_balance = self.trading_client_api.get_account().cash
        return self.account_balance

    def get_open_positions(self, symbol=None):
        if not self.open_positions:
            self.open_positions = self.trading_client_api.get_all_positions()

        if symbol:
            return [position for position in self.open_positions if position.symbol == symbol]
        return self.open_positions

    def buy(self, symbol, atr=None):
        position = self.get_open_positions(symbol)

        if position:
            self.logger.logger.info(f"An open position for {symbol} already exists.")
            return

        self.logger.logger.info(f"Placing buy order for {symbol}")

        current_price = float(self.get_quote_for_symbol(symbol).ask_price)
        self.logger.logger.info(f"current_price: {current_price}")

        stop_loss = calculate_stop_loss(current_price, atr)
        self.logger.logger.info(f"stop_loss: {stop_loss}")

        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=self.calculate_order_qty(symbol, current_price),
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
            # limit_price=current_price + atr_value,
            stop_price=stop_loss
        )

        # Market order
        market_order = self.trading_client_api.submit_order(
            order_data=market_order_data
        )
        self.logger.logger.info(f"market_order {market_order}")
        self.logger.logger.info(f'Placed buy order for {symbol}')
        return market_order

    def sell(self, position):
        self.logger.logger.info(f"Placing sell order for {position.symbol}")

        market_order_data = MarketOrderRequest(
            symbol=position.symbol,
            qty=position.qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )

        # Market order
        market_order = self.trading_client_api.submit_order(
            order_data=market_order_data
        )
        self.logger.logger.info(f"market_order {market_order}")
        self.logger.logger.info(f'Placed sell order for {position.symbol}')
        return market_order

    def calculate_order_qty(self, symbol, latest_price=None):
        try:
            if not latest_price:
                latest_price = self.trading_client_api.get_latest_trade(symbol).price
            balance = self.trading_client_api.get_account().cash
            max_investment = 0.25 * float(balance)
            qty = int(max_investment / latest_price)
            return qty
        except Exception as e:
            print(f"Error fetching order quantity for {symbol}")

    def get_quote_for_symbol(self, symbol):
        try:
            latest_quote_request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            latest_quote = self.stock_historical_data_client.get_stock_latest_quote(latest_quote_request)
            return latest_quote[symbol]
        except Exception as e:
            return None

    def get_open_orders(self):
        get_orders_data = GetOrdersRequest(
            status=QueryOrderStatus.OPEN,
            limit=100,
            nested=True
        )

        return self.trading_client_api.get_orders(filter=get_orders_data)





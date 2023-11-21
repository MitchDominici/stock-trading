import uuid
from datetime import datetime


class ExecutedTrade:
    def __init__(self, id: str, strategy_id: str, stock_symbol: str,
                 trade_type: str, quantity: int, price: float, trade_time: datetime,
                 account_id: str, status: str, profit_loss: float, paper_trade: bool):
        self.id = id
        self.strategy_id = strategy_id
        self.stock_symbol = stock_symbol
        self.trade_type = trade_type
        self.quantity = quantity
        self.price = price
        self.trade_time = trade_time
        self.account_id = account_id
        self.status = status
        self.profit_loss = profit_loss
        self.paper_trade = paper_trade

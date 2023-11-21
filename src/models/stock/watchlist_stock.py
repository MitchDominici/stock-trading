import uuid
from datetime import datetime, timedelta

from src.utils.utils import get_uuid_as_str


class WatchlistStock:
    def __init__(self, _id=None, symbol=None, signal=None, description="", last_price=None, target_buy_price: float = None, target_sell_price: float = None,
                 price_change_pct=None, watch_until=None,  updated_at=None):
        self.id = _id or get_uuid_as_str()
        self.symbol = symbol
        self.signal = signal
        self.description = description
        self.target_buy_price = target_buy_price
        self.target_sell_price = target_sell_price
        self.price_change_pct = price_change_pct
        self.watch_until = watch_until or str((datetime.today() + timedelta(days=1)))
        self.last_price = last_price
        self.updated_at = updated_at or str(datetime.now())

    def to_dict(self):
        """ Convert the watchlist entry to a dictionary. """
        return {
            "id": self.id,
            "symbol": self.symbol,
            "signal": self.signal,
            "description": self.description,
            "target_buy_price": self.target_buy_price,
            "target_sell_price": self.target_sell_price,
            "price_change_pct": self.price_change_pct,
            "watch_until": self.watch_until,
            "last_price": self.last_price,
            "updated_at": self.updated_at
        }

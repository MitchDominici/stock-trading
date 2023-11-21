from src.utils.utils import get_uuid_as_str


class HistoricalPrice:
    def __init__(self, symbol: str, date: str,
                 open: float, high: float, low: float,
                 close: float, volume: int, vwap: int, trade_count: int, _id=None):
        self.id = _id or get_uuid_as_str()
        self.symbol = symbol
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.vwap = vwap
        self.trade_count = trade_count

    def to_dict(self):
        return {
            "id": str(self.id),  # Convert UUID to string
            "symbol": self.symbol,
            "date": str(self.date),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }

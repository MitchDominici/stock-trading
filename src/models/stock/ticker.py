from src.utils.utils import get_uuid_as_str


class Ticker:
    def __init__(self, symbol, name=None, exchange=None, _id=None):
        self.id = _id or get_uuid_as_str()
        self.symbol = symbol
        self.name = name
        self.exchange = exchange

    def to_dict(self):
        return {
            "id": str(self.id),  # Convert UUID to string
            "symbol": self.symbol,
            "name": self.name,
            "exchange": self.exchange,
        }

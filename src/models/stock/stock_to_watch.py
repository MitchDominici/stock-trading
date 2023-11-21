class StockToWatch:
    def __init__(self, symbol: str, close, previous_close, price_change_pct, volume, timestamp, timeframe_unit):
        self.symbol = symbol
        self.close = close
        self.previous_close = previous_close
        self.price_change_pct = price_change_pct
        self.volume = volume
        self.timestamp = timestamp
        self.timeframe_unit = timeframe_unit

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "close": self.close,
            "previous_close": self.previous_close,
            "price_change_pct": self.price_change_pct,
            "volume": self.volume,
            "timestamp": self.timestamp,
            "timeframe_unit": self.timeframe_unit
        }

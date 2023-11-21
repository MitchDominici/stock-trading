from alpaca.data import TimeFrameUnit
from src.utils.utils import get_uuid_as_str


class StockPrice:
    def __init__(self, symbol: str, timeframe_unit: str, timestamp: str,
                 open: float, high: float, low: float,
                 close: float, volume: float, vwap: float, trade_count: float, _id=None):
        self.id = _id or get_uuid_as_str()
        self.symbol = symbol
        self.timeframe_unit = timeframe_unit
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.vwap = vwap
        self.trade_count = trade_count
        if timeframe_unit.lower() == 'minute' or timeframe_unit.lower() == 'min':
            self.timeframe_unit = TimeFrameUnit.Minute
        elif timeframe_unit.lower() == 'hour':
            self.timeframe_unit = TimeFrameUnit.Hour
        else:
            self.timeframe_unit = TimeFrameUnit.Day

    @classmethod
    def from_alpaca_bar_deprecated(cls, symbol, bar, timeframe_unit):
        """
        Create a StockPrice instance from an Alpaca stock bar.

        :param symbol: Stock symbol.
        :param bar: Alpaca stock bar data.
        :param timeframe_unit: Timeframe unit.
        :return: StockPrice instance.
        """
        return cls(
            symbol,
            timeframe_unit,
            bar['timestamp'],
            bar['open'],
            bar['high'],
            bar['low'],
            bar['close'],
            bar['volume'],
            bar['vwap'],
            bar['trade_count'],
            get_uuid_as_str()
        )

    @classmethod
    def from_alpaca_bar(cls, symbol, bar, timeframe_unit, timestamp):
        """
        Create a StockPrice instance from an Alpaca stock bar.

        :param symbol: Stock symbol.
        :param bar: Alpaca stock bar data.
        :param timeframe_unit: Timeframe unit.
        :return: StockPrice instance.
        """
        return cls(
            symbol,
            timeframe_unit,
            timestamp,
            bar['open'],
            bar['high'],
            bar['low'],
            bar['close'],
            bar['volume'],
            bar['vwap'],
            bar['trade_count'],
            get_uuid_as_str()
        )

    def to_dict(self):
        return {
            "id": str(self.id),
            "symbol": self.symbol,
            "timestamp": str(self.timestamp),
            "timeframe_unit": self.timeframe_unit,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "vwap": self.vwap,
            "trade_count": self.trade_count
        }

from src.constants import global_bb_params, global_macd_params, global_indicators_window
from src.ml.ml_vars import ModelFeatures
from src.utils.stock_logger import StockLogger
from enum import Enum


class IndicatorsEnum(Enum):
    BB = 'bb'
    MACD = 'macd'
    RSI = 'rsi'
    STOCH = 'stoch'
    EMA = 'ema'
    SMA = 'sma'
    VWAP = 'vwap'


class Indicators:
    logger = StockLogger("StockIndicators")
    model_features: ModelFeatures = None
    bb_upper = None
    bb_lower = None
    macd_line = None
    macd_signal = None
    rsi = None
    vwap = None
    stochastic_k = None
    stochastic_d = None
    sma = None
    ema = None

    def __init__(self, df, bb_params=global_bb_params, macd_params=global_macd_params, window=global_indicators_window):
        self.df = df
        self.window = window or 20
        self.bb_params = bb_params
        self.macd_params = macd_params

    def bollinger_bands(self):
        window = self.window
        num_std_dev = self.bb_params['num_std_dev']
        sma = self.df['close'].rolling(window=window).mean()
        std = self.df['close'].rolling(window=window).std()
        self.bb_upper = sma + (std * num_std_dev)
        self.bb_lower = sma - (std * num_std_dev)
        return sma - (std * num_std_dev), sma + (std * num_std_dev)

    def vwap(self):
        cumulative = self.df['close'] * self.df['volume']
        cumulative_volume = self.df['volume'].cumsum()
        return cumulative / cumulative_volume

    def macd(self):
        short_window = self.macd_params['short_window']
        long_window = self.macd_params['long_window']
        signal_window = self.macd_params['signal_window']
        short_ema = self.df['close'].ewm(span=short_window, adjust=False).mean()
        long_ema = self.df['close'].ewm(span=long_window, adjust=False).mean()
        macd_line = short_ema - long_ema
        signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
        return macd_line, signal_line

    def is_macd_positive(self):
        macd_line, signal_line = self.macd()
        return macd_line.iloc[-1] > signal_line.iloc[-1]

    # Relative Strength Index
    def rsi(self, period=14):
        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    # Stochastic Oscillator
    def stochastic_oscillator(self, k_period=14, d_period=3):
        low_min = self.df['low'].rolling(window=k_period).min()
        high_max = self.df['high'].rolling(window=k_period).max()
        k_line = 100 * ((self.df['close'] - low_min) / (high_max - low_min))
        d_line = k_line.rolling(window=d_period).mean()
        return k_line, d_line

    def simple_moving_average(self):
        return self.df['close'].rolling(window=self.window).mean()

    def exponential_moving_average(self):
        return self.df['close'].ewm(span=self.window, adjust=False).mean()

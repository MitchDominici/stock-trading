from src.models.stock.indicators import Indicators
from src.utils.stock_logger import StockLogger


class StockAnalysis:
    def __init__(self, df, indicators_list):
        self.df = df
        self.indicators = Indicators(df)
        self.indicators_list = indicators_list
        self.logger = StockLogger("StockAnalysis")

    def calculate_trade_signal(self):
        return self.trade_signal(), self.df['close'].iloc[-1]

    def calculate_trend_strength(self):
        vwap_signal = 'vwap' in self.indicators_list and self.df['close'].iloc[-1] < \
                      self.indicators.vwap().iloc[-1]
        macd_signal = 'macd' in self.indicators_list and self.indicators.is_macd_positive()
        return vwap_signal + macd_signal

    def calculate_target_prices(self, trade_signal):
        lower_band, upper_band = None, None
        if 'bb' in self.indicators_list:
            lower_band, upper_band = self.indicators.bollinger_bands()

        if trade_signal in ['strong_buy', 'weak_buy']:
            target_buy_price = lower_band.iloc[-1] if lower_band is not None else None
            return target_buy_price, None
        elif trade_signal in ['strong_sell', 'weak_sell']:
            target_sell_price = upper_band.iloc[-1] if upper_band is not None else None
            return None, target_sell_price
        return None, None

    def analyze(self, strict=False):
        trade_signal, latest_close = self.calculate_trade_signal()
        trend_strength = self.calculate_trend_strength()

        if strict and trend_strength < 2:
            return trade_signal, None, None

        target_buy_price, target_sell_price = self.calculate_target_prices(trade_signal)

        self.logger.logger.info(
            f"trade_signal: {trade_signal}, target_buy_price: {target_buy_price}, "
            f"target_sell_price: {target_sell_price}, "
            f"trend_strength: {trend_strength}")

        return trade_signal, target_buy_price, target_sell_price

    def trade_signal(self):
        signals = {'buy': 0, 'sell': 0}

        # Bollinger Bands
        if 'bb' in self.indicators_list:
            lower_band, upper_band = self.indicators.bollinger_bands()
            if self.df['close'].iloc[-1] < lower_band.iloc[-1]:
                signals['buy'] += 1
            if self.df['close'].iloc[-1] > upper_band.iloc[-1]:
                signals['sell'] += 1

        # VWAP
        if 'vwap' in self.indicators_list:
            vwap = self.indicators.vwap().iloc[-1]
            if self.df['close'].iloc[-1] < vwap:
                signals['buy'] += 1
            if self.df['close'].iloc[-1] > vwap:
                signals['sell'] += 1

        # MACD
        if 'macd' in self.indicators_list:
            if self.indicators.is_macd_positive():
                signals['buy'] += 1
            else:
                signals['sell'] += 1

                # RSI
        if 'rsi' in self.indicators_list:
            rsi = self.indicators.rsi().iloc[-1]
            if rsi < 30:
                signals['buy'] += 1
            if rsi > 70:
                signals['sell'] += 1

        # Stochastic Oscillator
        if 'stoch' in self.indicators_list:
            k_line, d_line = self.indicators.stochastic_oscillator()
            if k_line.iloc[-1] < 20 or d_line.iloc[-1] < 20:
                signals['buy'] += 1
            if k_line.iloc[-1] > 80 or d_line.iloc[-1] > 80:
                signals['sell'] += 1

        if 'ema' in self.indicators_list:
            ema = self.indicators.exponential_moving_average().iloc[-1]
            if self.df['close'].iloc[-1] < ema:
                signals['buy'] += 1
            if self.df['close'].iloc[-1] > ema:
                signals['sell'] += 1

        if 'sma' in self.indicators_list:
            sma = self.indicators.simple_moving_average().iloc[-1]
            if self.df['close'].iloc[-1] < sma:
                signals['buy'] += 1
            if self.df['close'].iloc[-1] > sma:
                signals['sell'] += 1

        # Decision based on weighted signals
        if signals['buy'] > signals['sell']:
            return 'strong_buy' if signals['buy'] > 1 else 'weak_buy'
        elif signals['sell'] > signals['buy']:
            return 'strong_sell' if signals['sell'] > 1 else 'weak_sell'
        else:
            return 'hold'

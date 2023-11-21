import backtrader as bt
from src.trading.brokerages.alpaca.back_tests.back_test import backtest
from src.trading.brokerages.alpaca.back_tests.custom_vwap import CustomVWAP

stock_symbols = ["SIRI", "SPCE", "PRZO", "LABU", "NKLA", "JBLU", "ETWO", "OPEN", "CHPT", "PTON"]


class MomentumStrategy(bt.Strategy):
    params = (
        ('stocks', []),
        ('bband_period', 20),
        ('macd_short_period', 12),
        ('macd_long_period', 26),
        ('macd_signal_period', 9)
    )

    def __init__(self):
        self.indicators = {}

        if 'BBAND' in self.params.indicators:
            self.indicators['BBAND'] = bt.indicators.BollingerBands(self.data.close, period=self.params.bband_period)

        if 'VWAP' in self.params.indicators:
            self.vwap = CustomVWAP(self.data)

        if 'MACD' in self.params.indicators:
            self.indicators['MACD'] = bt.indicators.MACDHisto(self.data,
                                                              period_me1=self.params.macd_short_period,
                                                              period_me2=self.params.macd_long_period,
                                                              period_signal=self.params.macd_signal_period)

    def next(self):
        if not self.position:
            signals = []
            if 'BBAND' in self.indicators:
                signals.append(self.data.close[0] < self.indicators['BBAND'].bot[0])
            if 'VWAP' in self.indicators:
                signals.append(self.data.close[0] < self.indicators['VWAP'][0])
            if 'MACD' in self.indicators:
                signals.append(self.indicators['MACD'][0] > 0)

            if all(signals):
                self.buy()

        else:
            signals = []
            if 'BBAND' in self.indicators:
                signals.append(self.data.close[0] > self.indicators['BBAND'].top[0])
            if 'VWAP' in self.indicators:
                signals.append(self.data.close[0] > self.indicators['VWAP'][0])
            if 'MACD' in self.indicators:
                signals.append(self.indicators['MACD'][0] < 0)

            if all(signals):
                self.sell()


backtest(stock_symbols, MomentumStrategy, 'all_signals', ['MACD'])

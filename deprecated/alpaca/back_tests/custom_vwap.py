import backtrader as bt


class CustomVWAP(bt.Indicator):
    lines = ('vwap',)
    params = (('period', 20),)

    def __init__(self):
        self.addminperiod(self.params.period)
        self.cum_volume = bt.indicators.CumulativeSum(self.data.volume)
        self.cum_vol_price = bt.indicators.CumulativeSum(self.data.close * self.data.volume)

    def next(self):
        self.lines.vwap[0] = self.cum_vol_price[0] / self.cum_volume[0]

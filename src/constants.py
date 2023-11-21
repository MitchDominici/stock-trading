global_live_trading = False
global_paper_trading = True
global_stock_exchanges = ['OTC', 'AMEX', 'NASDAQ', 'NYSE', ]
global_min_volume = 750000
global_max_price = 5.00
global_min_price = 0.10

# the number of days to get when fetching stock data
global_days_to_get = 30
global_chunk_size = 100000

global_days_to_get_for_analysis = 30

# 8 hours
global_min_days_to_get_for_analysis = 480

global_buy_signals = ['strong_buy', 'weak_buy']
global_sell_signals = ['strong_sell', 'weak_sell']

global_indicators_window = 20

global_bb_params = {'num_std_dev': 2}
global_macd_params = {'short_window': 12, 'long_window': 26, 'signal_window': 9}

global_numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']
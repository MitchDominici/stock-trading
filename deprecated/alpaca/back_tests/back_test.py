import backtrader as bt
import datetime
import yfinance as yf
from src.utils.file_manager import write_json_file


def backtest(stock_symbols, strategy, test_name, indicators):
    if indicators is None:
        indicators = ['BBAND', 'VWAP', 'MACD']
    results = {}
    total_profit = 0.0

    # symbols = find_momentum_stocks()
    for symbol in stock_symbols:
        print(f"Backtesting {symbol}...")

        # Download historical data from Yahoo Finance
        try:
            data_df = yf.download(symbol, start="2021-10-01", end="2023-10-01")
            data = bt.feeds.PandasData(dataname=data_df)
            cerebro = bt.Cerebro()
            cerebro.addstrategy(strategy, indicators=indicators)
            cerebro.adddata(data)
            cerebro.broker.set_cash(1000)
            cerebro.addsizer(bt.sizers.FixedSize, stake=25)

            start_val = cerebro.broker.getvalue()
            print('Starting Portfolio Value: %.2f' % start_val)

            cerebro.run()

            end_val = cerebro.broker.getvalue()
            print('Ending Portfolio Value: %.2f' % end_val)

            profit = end_val - start_val  # Calculate profit for this symbol
            total_profit += profit  # Aggregate the profit

            results[symbol] = {
                "start_value": start_val,
                "end_value": end_val,
                "profit": profit
            }
        except IndexError:
            print(f"Error: No data for {symbol}")
            continue

    print(f"Total Aggregated Profit: ${total_profit:.2f}")  # Display aggregated profit

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d__%H_%M_%S")
    write_json_file(f'data/backtest_results/{test_name}_{timestamp}.json', results)

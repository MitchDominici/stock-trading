from src.batch_jobs.backtest_ml import BacktestMl
from src.batch_jobs.build_daily_watchlist import BuildDailyWatchlist
from src.batch_jobs.data_tester import DataTester
from src.batch_jobs.download_stock_data import DownloadStockData
from src.batch_jobs.insert_tickers import InsertTickers
from src.batch_jobs.run_trader_bot import RunTraderBot
from src.batch_jobs.update_account_balance import UpdateAccountBalance

global_batch_job_map = {
    'download_stock_data': DownloadStockData,
    'run_trader_bot': RunTraderBot,
    'update_account_balance': UpdateAccountBalance,
    'insert_tickers': InsertTickers,
    'build_daily_watchlist': BuildDailyWatchlist,
    'data_tester': DataTester,
    'backtest_ml': BacktestMl
}

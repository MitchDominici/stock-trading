class BatchRunner(BatchJob):
    logger = StockLogger('BatchRunner')

    def __init__(self):
        super().__init__()

        self.run_action = self.config_manager.get_run_action()

        self.batch_job_map = {
            'download_stock_data': DownloadStockData,
            'run_trader_bot': RunTraderBot,
            'update_account_balance': UpdateAccountBalance,
            'insert_tickers': InsertTickers,
            'build_daily_watchlist': BuildDailyWatchlist
        }

    def run(self):
        try:
            batch_job_class = self.batch_job_map.get(self.run_action)
            if batch_job_class:
                self.logger.log_process(self.run_action, 'start')

                job = batch_job_class()
                job.run()

                self.logger.log_process(self.run_action, 'stop')
            else:
                self.logger.log_error(f"Invalid action: {self.run_action}", True)
        except Exception as e:
            self.logger.log_error(e, f"Error running batch job {self.run_action}", True)

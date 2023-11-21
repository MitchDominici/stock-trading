from src.batch_jobs.batch_job import BatchJob
from src.batch_jobs.batch_jobs_maps import global_batch_job_map
from src.postgres.database_service import DatabaseService
from src.utils.stock_logger import StockLogger


class BatchRunner(BatchJob):
    logger = StockLogger('BatchRunner')

    def __init__(self):
        super().__init__()
        self.run_action = self.config_manager.get_run_action()
        self.batch_job_map = global_batch_job_map

    def run(self):
        try:
            batch_job_class = self.batch_job_map.get(self.run_action)
            if batch_job_class:
                self.logger.log_process(self.run_action, 'start')

                DatabaseService().connect()

                job = batch_job_class()
                job.run()

                DatabaseService().disconnect()

                self.logger.log_process(self.run_action, 'stop')
            else:
                self.logger.log_error(f"Invalid action: {self.run_action}", True)
        except Exception as e:
            self.logger.log_error(e, f"Error running batch job {self.run_action}", True)

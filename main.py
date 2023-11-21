from src.batch_jobs.batch_runner import BatchRunner
from src.utils.stock_logger import StockLogger


logger_name = 'BatchJobRunner'
logger = StockLogger(logger_name)


def main():
    BatchRunner().run()


if __name__ == '__main__':
    main()

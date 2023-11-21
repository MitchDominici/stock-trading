import sys
import traceback
from datetime import datetime

from loguru import logger

from src.utils.file_manager import write_json_file, read_json_file

log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[logger_name]}: {line}</cyan> | <level>{message}</level>"
logger.remove()
logger.add('logs/app.log', level="ERROR", rotation="1 week", compression="zip", serialize=True)
logger.add(sys.stdout, format=log_format, level='DEBUG')


class StockLogger:
    def __init__(self, logger_name="CustomLogger"):
        self.logger_name = logger_name
        self.logger = logger.bind(logger_name=self.logger_name)
        self.logger.level('DEBUG', color="<blue>")
        self.logger.level('INFO', color="<white>")

    def log_process(self, process_name: str, action='start' or 'stop' or 1 or 0):
        date_format = "%Y-%m-%d %H:%M:%S"
        # Get the current date and time
        current_time = datetime.now()

        log_file = f"logs/processes/{process_name}.json"

        # Load existing entries from the file, or create an empty list if the file doesn't exist
        logs = read_json_file(log_file)
        if logs is None:
            logs = []

        if action == 'start' or action == 1:
            new_log = {
                "start_time": current_time.strftime(date_format)
            }
            self.logger.info(f"Started {process_name} at: {new_log['start_time']}")
            logs.append(new_log)

        elif action == 'stop' or action == 0:
            log = logs[-1]
            start_time = datetime.strptime(log['start_time'], date_format)
            log['end_time'] = current_time.strftime(date_format)

            # Calculate the duration in minutes
            duration_minutes = (current_time - start_time).total_seconds() / 60
            log['duration (minutes)'] = duration_minutes

            self.logger.info(
                f"Stopped {process_name} at: {log['end_time']}, duration (minutes): {log['duration (minutes)']}")

        write_json_file(log_file, logs, False)

    def log_trade(self, symbol: str, action="buy" or "sell", price: float = None, quantity: float = None,
                  broker="alpaca"):
        # Get the current date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_file = f"logs/trades/{broker}.json"

        # Load existing entries from the file, or create an empty list if the file doesn't exist
        logs = read_json_file(log_file)
        if logs is None:
            logs = []

        new_log = {
            "symbol": symbol,
            "action": action,
            "price": price,
            "quantity": quantity,
            "execution_time": current_time
        }

        self.logger.info(f"Logged trade: {new_log}")

        # Append the new entry to the list
        logs.append(new_log)

        write_json_file(log_file, logs, False)

    def log_error(self, error, msg, log_stack_trace=True):
        self.logger.error(f"{msg}: {error}")
        if log_stack_trace:
            traceback.print_exc()

    def log_special(self, msgs, msg_args=None):
        # check if params are lists
        if msg_args is None:
            msg_args = [None]
        if not isinstance(msgs, list):
            msgs = [msgs]
        if not isinstance(msg_args, list):
            msg_args = [msg_args]

        # check if lists are same length
        if len(msgs) != len(msg_args):
            raise Exception("msgs and msg_args must be the same length")

        self.logger.info('-----------------------------------------------')
        for msg, args in zip(msgs, msg_args):
            self.logger.info(msg, args)
        self.logger.info('-----------------------------------------------')

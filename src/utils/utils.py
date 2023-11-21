import inspect
import json
import re
import uuid
from datetime import datetime, timedelta

import pandas as pd
import pandas_market_calendars as mcal

from src.constants import global_days_to_get
from src.utils.stock_logger import StockLogger


def get_uuid_as_str():
    new_uuid = str(uuid.uuid4())
    return new_uuid


def get_datetime_as_str():
    return str(datetime.now())


def chunk_array(array, chunk_size=10000):
    """
    Chunks the given array and applies the provided function to each chunk.

    :param array: The array to be chunked.
    :param chunk_size: The size of each chunk. Default is 5.
    """
    responses = []
    for i in range(0, len(array), chunk_size):
        chunk = array[i:i + chunk_size]
        responses.append(chunk)

    return responses


def chunk_and_process(process_function, array, chunk_size=10000, stringify=False, **args):
    logger = StockLogger("process_chunked_array")

    chunks = chunk_array(array, chunk_size)
    responses = []

    count = 0
    for chunk in chunks:
        count += 1
        logger.log_special(f"Processing chunk {count} of {len(chunks)}")

        if stringify:
            response = process_function(json.dumps(chunk), **args)
        else:
            response = process_function(chunk, **args)

        if response is not None:
            responses.append(response)

        logger.log_special(f"Finished processing chunk {count} of {len(chunks)}")

    return responses


def extract_symbols(obj_list):
    """
    Extracts and returns the symbols from a list of objects.

    :param obj_list: List of objects
    :return: List of symbols (strings)
    """
    symbols = [obj.symbol for obj in obj_list]
    return symbols


def flatten_array(arr):
    """
    Flattens a nested array.
    """
    result = []
    for item in arr:
        if isinstance(item, list):
            result.extend(flatten_array(item))
        else:
            result.append(item)
    return result


def generate_date_range(days_back=global_days_to_get, end_date=None):
    """
    Generates a start and end date for fetching stock data.

    Args:
    days_back (int): Number of days back from the end date for the start date.
    end_date (datetime.date): End date for data fetching. Defaults to today if not provided.

    Returns:
    tuple: A tuple containing the start and end dates.
    """
    timezone = "America/New_York"

    nyse_cal = mcal.get_calendar('XNYS')

    if end_date is None:
        # Use the current date and time in the New York timezone
        current_datetime = pd.Timestamp.now(tz=timezone)

        # Check if the market is open on the current date
        if nyse_cal.valid_days(start_date=current_datetime, end_date=current_datetime, tz=timezone).size > 0:
            # Market is open today, use the current date as end_date
            end_date = current_datetime.replace(hour=0, minute=0, second=0)
        else:
            # Market is closed today, use the last valid market day as end_date
            end_date = find_previous_valid_market_day(nyse_cal, current_datetime, timezone).replace(hour=0, minute=0,
                                                                                                    second=0)
            print(f"Market is closed today, using {end_date} as end_date")

    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date


def find_previous_valid_market_day(calendar, current_datetime, timezone):
    while True:
        current_datetime -= timedelta(days=1)
        if calendar.valid_days(start_date=current_datetime, end_date=current_datetime, tz=timezone).size > 0:
            return current_datetime


# Function to adjust for market holidays
def adjust_for_market_holidays(start_date, end_date):
    """
    Adjusts the start and end dates for market holidays.

    Args:
    start_date (datetime.date): The start date.
    end_date (datetime.date): The end date.

    Returns:
    tuple: A tuple containing the adjusted start and end dates.
    """
    nyse = mcal.get_calendar('NYSE')
    valid_days = nyse.valid_days(start_date=start_date, end_date=end_date)
    return valid_days.min().date(), valid_days.max().date()


# Function to validate ticker symbols
def validate_ticker_symbol(symbol):
    """
    Validates the format of a ticker symbol.

    Args:
    symbol (str): The ticker symbol to validate.

    Returns:
    bool: True if valid, False otherwise.
    """
    return symbol.isupper() and symbol.isalpha()


def get_current_function_name():
    return inspect.currentframe().f_code.co_name


def convert_timestamp_format(timestamp_str):
    """
    Converts a timestamp from 'YYYY-MM-DD HH:MM:SS' format to
    'YYYY-MM-DD HH:MM:SS+00:00' format.

    :param timestamp_str: String of timestamp in 'YYYY-MM-DD HH:MM:SS' format.
    :return: String of timestamp in 'YYYY-MM-DD HH:MM:SS+00:00' format.
    """
    # Parse the original timestamp string into a datetime object
    original_format = "%Y-%m-%d %H:%M:%S"
    datetime_obj = datetime.strptime(timestamp_str, original_format)

    # Format the datetime object back into the desired string format
    new_format = "%Y-%m-%d %H:%M:%S+00:00"
    new_timestamp_str = datetime_obj.strftime(new_format)

    return new_timestamp_str


def classification_report_to_json(report):
    """
    Convert a classification report string into JSON format.

    :param report: String of classification report.
    :return: JSON object of the report.
    """
    report_data = []
    lines = report.split('\n')
    for line in lines[2:-5]:
        row = {}
        line = re.sub(r'\s+', ' ', line).strip()  # Replace multiple whitespaces with single space
        row_data = line.split(' ')

        if len(row_data) == 5:  # Check if row has all elements
            row['class'] = row_data[0]
            row['precision'] = float(row_data[1])
            row['recall'] = float(row_data[2])
            row['f1-score'] = float(row_data[3])
            row['support'] = int(row_data[4])
            report_data.append(row)

    # Parsing the summary part
    summary_lines = lines[-4:-1]
    for line in summary_lines:
        row = {}
        line = re.sub(r'\s+', ' ', line).strip()  # Replace multiple whitespaces with single space
        row_data = line.split(' ')
        row['metric'] = row_data[0]
        row['precision'] = float(row_data[2])
        row['recall'] = float(row_data[3])
        row['f1-score'] = float(row_data[4])
        row['support'] = int(row_data[5]) if row_data[5].isdigit() else None
        report_data.append(row)

    return json.dumps(report_data)


def get_model_name(model_to_use, indicators_to_use):
    """
    Returns the name of the given model.

    :param model: The model to get the name of.
    :return: The name of the model.
    """
    return model_to_use + '_' + str(indicators_to_use)

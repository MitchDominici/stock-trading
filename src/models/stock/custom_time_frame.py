from alpaca.data import TimeFrameUnit, TimeFrame
from src.utils.utils import get_uuid_as_str
from enum import Enum


class TimeFrameEnum(Enum):
    ONE_MINUTE = "1_minute"
    THREE_MINUTE = "3_minute"
    FIVE_MINUTE = "5_minute"
    FIFTEEN_MINUTE = "15_minute"
    THIRTY_MINUTE = "30_minute"
    FORTY_FIVE_MINUTE = "45_minute"
    FIFTY_NINE_MINUTE = "59_minute"
    ONE_HOUR = "1_hour"
    EIGHT_HOUR = "8_hour"
    ONE_DAY = "1_day"
    ONE_WEEK = "1_week"
    ONE_MONTH = "1_month"
    THREE_MONTH = "3_month"
    SIX_MONTH = "6_month"
    NINE_MONTH = "9_month"
    TWELVE_MONTH = "12_month"


class CustomTimeFrame:
    def __init__(self, _id, code, amount, unit):
        self.id = _id or get_uuid_as_str()
        self.code = code
        self.amount = int(amount)
        self.unit = unit

    @classmethod
    def get_time_frame_from_enum(cls, time_frame_enum):
        if not isinstance(time_frame_enum, TimeFrameEnum):
            raise ValueError("Input must be a TimeFrameEnum value")

        code = time_frame_enum.value
        # You can set the amount and unit based on the specific TimeFrameEnum value
        if time_frame_enum in [
            TimeFrameEnum.ONE_MINUTE,
            TimeFrameEnum.THREE_MINUTE,
            TimeFrameEnum.FIVE_MINUTE,
            TimeFrameEnum.FIFTEEN_MINUTE,
            TimeFrameEnum.THIRTY_MINUTE,
            TimeFrameEnum.FORTY_FIVE_MINUTE,
            TimeFrameEnum.FIFTY_NINE_MINUTE,
        ]:
            amount = int(time_frame_enum.value.split("_")[0])
            unit = "minute"
        elif time_frame_enum in [TimeFrameEnum.ONE_HOUR, TimeFrameEnum.EIGHT_HOUR]:
            amount = int(time_frame_enum.value.split("_")[0])
            unit = "hour"
        elif time_frame_enum in [
            TimeFrameEnum.ONE_DAY,
        ]:
            amount = int(time_frame_enum.value.split("_")[0])
            unit = "day"
        elif time_frame_enum in [TimeFrameEnum.ONE_WEEK]:
            amount = int(time_frame_enum.value.split("_")[0])
            unit = "week"
        elif time_frame_enum in [TimeFrameEnum.ONE_MONTH, TimeFrameEnum.THREE_MONTH, TimeFrameEnum.SIX_MONTH,
                                 TimeFrameEnum.NINE_MONTH, TimeFrameEnum.TWELVE_MONTH]:
            amount = int(time_frame_enum.value.split("_")[0])
            unit = "month"
        else:
            raise ValueError("Unknown TimeFrameEnum value")

        return CustomTimeFrame(get_uuid_as_str(), code=code, amount=amount, unit=unit)

    def to_dict(self):
        return {
            'amount': self.amount,
            'unit': self.unit,
            'code': self.code,
            'id': self.id
        }

    def convert_to_alpaca_timeframe(self):
        """
        Converts timeframe amount and unit into a TimeFrame object compatible with Alpaca API.

        Args:
        timeframe_amount (int): The amount of time.
        timeframe_unit (str): The unit of time (minute, hour, day, week, month, year).

        Returns:
        TimeFrame: A TimeFrame object for the Alpaca API.
        """
        unit_map = {
            'minute': TimeFrameUnit.Minute,
            'hour': TimeFrameUnit.Hour,
            'day': TimeFrameUnit.Day,
            'week': TimeFrameUnit.Week,
            'month': TimeFrameUnit.Month,
        }

        alpaca_unit = unit_map[self.unit]

        return TimeFrame(self.amount, alpaca_unit)

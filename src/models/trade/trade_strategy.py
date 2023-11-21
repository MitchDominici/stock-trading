import uuid
from datetime import datetime


class TradeStrategy:
    def __init__(self, id: str, code: str, description: str,
                 indicators: str, creation_date: datetime):
        self.id = id
        self.code = code
        self.description = description
        self.indicators = indicators
        self.creation_date = creation_date

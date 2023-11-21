from src.constants import global_min_volume, global_max_price, global_min_price
from src.utils.utils import get_uuid_as_str


class Filter:
    id: str
    code: str
    min_price: float
    max_price: float
    min_volume: int

    def __init__(self, _id=None, code: str = None, min_price=global_min_price, max_price=global_max_price,
                 min_volume=global_min_volume):
        self.id = _id or get_uuid_as_str()
        self.code = code
        self.min_price = float(min_price)
        self.max_price = float(max_price)
        self.min_volume = int(min_volume)

    def price_is_valid(self, price):
        if price is None:
            return False
        return self.min_price <= price <= self.max_price

    def volume_is_valid(self, volume):
        if volume is None:
            return False
        return volume >= float(self.min_volume)

    def to_dict(self):
        return {
            'id': self.id,
            'priority': self.priority,
            'code': self.code,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'min_volume': self.min_volume,
        }

from typing import List, Optional
import uuid


class AlpacaAsset:
    def __init__(self, id: uuid.UUID, asset_class: str, exchange: str, symbol: str,
                 name: str, status: str, tradable: bool, marginable: bool,
                 shortable: bool, easy_to_borrow: bool, fractionable: bool,
                 maintenance_margin_requirement: str, attributes: Optional[List[str]] = None):
        self.id = id
        self.asset_class = asset_class
        self.exchange = exchange
        self.ticker = symbol
        self.symbol = symbol
        self.name = name
        self.status = status
        self.tradable = tradable
        self.marginable = marginable
        self.shortable = shortable
        self.easy_to_borrow = easy_to_borrow
        self.fractionable = fractionable
        self.maintenance_margin_requirement = maintenance_margin_requirement
        self.attributes = attributes if attributes is not None else []

    def __repr__(self):
        return (f"Equity(id={self.id}, asset_class='{self.asset_class}', exchange='{self.exchange}', "
                f"symbol='{self.symbol}', name='{self.name}', status='{self.status}', "
                f"tradable={self.tradable}, marginable={self.marginable}, shortable={self.shortable}, "
                f"easy_to_borrow={self.easy_to_borrow}, fractionable={self.fractionable}, "
                f"maintenance_margin_requirement='{self.maintenance_margin_requirement}', "
                f"attributes={self.attributes})")

    def to_dict(self):
        return {
            'id': self.id,
            'asset_class': self.asset_class,
            'exchange': self.exchange,
            'symbol': self.symbol,
            'name': self.name,
            'status': self.status,
            'tradable': self.tradable,
            'marginable': self.marginable,
            'shortable': self.shortable,
            'easy_to_borrow': self.easy_to_borrow,
            'fractionable': self.fractionable,
            'maintenance_margin_requirement': self.maintenance_margin_requirement,
            'attributes': self.attributes
        }

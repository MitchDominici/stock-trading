class Account:
    def __init__(self, id: str, brokerage_code: str, paper: bool,
                 account_balance: float, account_status: str, updated: str):
        self.id = id
        self.brokerage_code = brokerage_code
        self.paper = paper
        self.account_balance = account_balance
        self.account_status = account_status
        self.updated = updated

    def to_dict(self):
        return {
            "id": self.id,
            "brokerage_code": self.brokerage_code,
            "paper": self.paper,
            "account_balance": self.account_balance,
            "account_status": self.account_status,
            "updated": self.updated
        }

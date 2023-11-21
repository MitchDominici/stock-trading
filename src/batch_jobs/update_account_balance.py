from src.batch_jobs.batch_job import BatchJob
from src.constants import global_paper_trading
from src.models.account_info.account import Account
from src.utils.utils import get_uuid_as_str, get_datetime_as_str


class UpdateAccountBalance(BatchJob):
    def __init__(self):
        super().__init__()

    def run(self):
        try:
            # get account balance
            account_balance = self.alpaca_stock_data.get_account_balance()
            unique_id = get_uuid_as_str()
            updated = get_datetime_as_str()

            #  build account object
            account = Account(id=unique_id, brokerage_code=self.alpaca_stock_data.brokerage_code,
                              paper=global_paper_trading, account_balance=account_balance, account_status='active',
                              updated=updated)
            account_json = account.to_dict()

            # insert account balance
            self.stock_trader_db.insert_account_balances([account_json])

        except Exception as e:
            self.logger.error(f'Error in UpdateAccountBalance.run(): {e}', True)

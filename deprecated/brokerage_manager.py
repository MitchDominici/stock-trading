from src.trading.bots.alpaca_bot import AlpacaBot


def get_brokerage_api(api_name: str):
    print("get_brokerage_api")
    if api_name == 'alpaca':
        alpaca_bot = AlpacaBot()
        return alpaca_bot

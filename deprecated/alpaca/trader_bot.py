from src.trading.brokerages.alpaca.api import get_api
from src.trading.brokerages.alpaca.stocks import get_stock_data
from src.trading.stocks import trade_signal, get_trade_strength
from src.trading.brokerages.alpaca.orders import calculate_order_qty, place_order
from src.ml.model import save_model, load_model
from src.utils.file_manager import read_json_file

MINIMUM_VOLUME = 750000
MODEL_NAME = 'back_test_model.pkl'


def best_stock_to_trade(indicators_to_use, filename="yahoo_momentum_stocks_2023-10-15__21_41_56.json"):
    """ Returns the best stock to trade based on momentum """
    print('Getting best stock to trade...')
    # Try reading from the JSON file
    stocks = read_json_file(f'data/{filename}')
    if not stocks:
        print("No suitable stocks found.")
        return
    print(f"Found {len(stocks)} stocks in {filename}.")
    stock_strengths = {}
    for stock in stocks:
        if stock:
            df = get_stock_data(stock)
            volume = df[0].v
            if volume < MINIMUM_VOLUME:
                continue
            print(f"Processing {stock}...")
            signal = trade_signal(df, indicators_to_use)
            if signal == 'buy':
                stock_strengths[stock] = get_trade_strength(df)

    if not stock_strengths:
        print("No suitable stocks found.")
        return

    best_stock = max(stock_strengths, key=stock_strengths.get)
    print(f'Best stock to trade: {best_stock}')
    return best_stock


# ------------------------------------------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------------------------------------------
def execute(indicators_to_use, model_name=MODEL_NAME):
    """ Main execution function """
    print('Starting up trading...')
    try:
        alpaca_api = get_api()

        open_positions = alpaca_api.list_positions()
        if open_positions:
            stock_symbol = open_positions[0].symbol
        else:
            stock_symbol = best_stock_to_trade(indicators_to_use)

        if stock_symbol:
            ml_model(stock_symbol, indicators_to_use, model_name)
            print(f"Selected stock for trading: {stock_symbol}")
            df = get_stock_data(stock_symbol)
            action = trade_signal(df, indicators_to_use)
            print(f"Trading signal: {action}")
            qty = calculate_order_qty(stock_symbol)
            place_order(stock_symbol, action, qty)
    except Exception as e:
        print(f"Error encountered in trader_main: {e}")


def ml_model(stock_symbol, indicators_to_use, model_name=MODEL_NAME):
    try:
        df = get_stock_data(stock_symbol)

        model = load_model(model_name)
        model.train(df, indicators_to_use)
        action = model.predict()
        save_model(model, model_name)
        print(f"Trading signal: {action}")
    except Exception as e:
        print(f"Error encountered in ml_model: {e}")

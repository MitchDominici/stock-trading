from src.models.stock.indicators import Indicators


def add_technical_indicators(data, indicators):
    """
    Adds technical indicators as features to the stock data.

    :param data: Dictionary of DataFrames with cleaned stock data.
    :param indicators: List of indicators to add.
    :return: Stock data with added features as a dictionary of DataFrames.
    """
    # print(data)
    if 'sma' in indicators:
        indicator_calculator = Indicators(data)
        sma = indicator_calculator.simple_moving_average()
        data['SMA'] = sma
    if 'ema' in indicators:
        indicator_calculator = Indicators(data)
        ema = indicator_calculator.simple_moving_average()
        data['EMA'] = ema
    if 'rsi' in indicators:
        indicator_calculator = Indicators(data)
        rsi = indicator_calculator.rsi()
        data['RSI'] = rsi
    if 'macd' in indicators:
        # Initialize the Indicators class with the DataFrame
        indicator_calculator = Indicators(data)
        macd_line, signal_line = indicator_calculator.macd()
        data['MACD'] = macd_line
        data['MACD_Signal'] = signal_line
    if 'bb' in indicators:
        # Initialize the Indicators class with the DataFrame
        indicator_calculator = Indicators(data)
        bb_upper, bb_lower = indicator_calculator.bollinger_bands()
        data['BB_Upper'] = bb_upper
        data['BB_Lower'] = bb_lower
    if 'vwap' in indicators:
        # Initialize the Indicators class with the DataFrame
        indicator_calculator = Indicators(data)
        data['VWAP'] = indicator_calculator.vwap()
    if 'stoch' in indicators:
        # Initialize the Indicators class with the DataFrame
        indicator_calculator = Indicators(data)
        stoch_k, stoch_d = indicator_calculator.stochastic_oscillator()
        data['Stochastic_K'] = stoch_k
        data['Stochastic_D'] = stoch_d

    return data


def engineer_features_for_stock_prices(stock_prices, indicators_to_use):
    ret_val = []
    for stock_price_df in stock_prices:
        ret_val.append(add_technical_indicators(stock_price_df, indicators_to_use))
    return ret_val

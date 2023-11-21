# Individual Indicator Functions
def bollinger_bands(df, window=20, num_std_dev=2):
    sma = df.c.rolling(window=window).mean()
    std = df.c.rolling(window=window).std()
    return sma - (std * num_std_dev), sma + (std * num_std_dev)


def vwap(df):
    cumulative = df.c * df.v
    cumulative_volume = df.v.cumsum()
    return cumulative / cumulative_volume


def macd(df, short_window=12, long_window=26, signal_window=9):
    short_ema = df.c.ewm(span=short_window, adjust=False).mean()
    long_ema = df.c.ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    return macd_line, signal_line


def trade_signal(df, indicators):
    try:
        print(df)
        latest_data = df[0]
        df = df[0]
        # Apply stocks and store results
        signals = []

        if 'bollinger_bands' in indicators:
            lower, upper = bollinger_bands(df)
            signals.append(('Lower Band', latest_data['close'] < lower.iloc[-1]))
            signals.append(('Upper Band', latest_data['close'] > upper.iloc[-1]))

        if 'vwap' in indicators:
            vw = vwap(df)
            signals.append(('VWAP', latest_data['close'] < vw.iloc[-1]))

        if 'macd' in indicators:
            macd_line, signal_line = macd(df)
            signals.append(('MACD', latest_data['MACD'] > signal_line.iloc[-1]))

        # Trading signal logic based on available stocks
        buy_conditions = [signal[1] for signal in signals if signal[0] in ['Lower Band', 'VWAP', 'MACD']]
        sell_conditions = [signal[1] for signal in signals if signal[0] in ['Upper Band', 'VWAP', 'MACD']]

        if all(buy_conditions):
            return 'buy'
        elif all(sell_conditions):
            return 'sell'
        else:
            return 'hold'
    except Exception as e:
        print(f"Error determining trade signal: {e}")


def get_trade_strength(df):
    """ Determines the strength of the trade signal using MACD difference """
    try:
        latest_data = df.iloc[-1]
        return abs(latest_data['MACD'] - latest_data['Signal_Line'])
    except Exception as e:
        print(f"Error determining trade strength: {e}")

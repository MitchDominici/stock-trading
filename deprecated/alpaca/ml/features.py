from src.trading.stocks import bollinger_bands, vwap, macd


def create_features(df, indicators):
    """ Creates features for the given dataframe """
    if 'bollinger_bands' in indicators:
        df['Lower_Band'], df['Upper_Band'] = bollinger_bands(df)
    if 'vwap' in indicators:
        df['VWAP'] = vwap(df)
    if 'macd' in indicators:
        df['MACD'], df['Signal_Line'] = macd(df)
    return df

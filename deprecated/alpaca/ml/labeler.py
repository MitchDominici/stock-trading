def create_labels(df, lookahead_days=5, threshold_percent=0.03):
    df['Future_Close'] = df['close'].shift(-lookahead_days)
    df['Return'] = (df['Future_Close'] - df['close']) / df['close']

    df['Label'] = 'hold'
    df.loc[df['Return'] > threshold_percent, 'Label'] = 'buy'
    df.loc[df['Return'] < -threshold_percent, 'Label'] = 'sell'

    df = df.drop(columns=['Future_Close', 'Return'])  # Drop unnecessary columns
    return df

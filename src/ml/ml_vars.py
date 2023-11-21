class ModelFeatures:
    base_model_features = ['open', 'high', 'low', 'close', 'trade_count', 'volume', 'vwap']
    bb_model_features = ['BB_Upper', 'BB_Lower']
    macd_model_features = ['MACD', 'MACD_Signal']
    rsi_model_features = ['RSI']
    stoch_model_features = ['Stochastic_K', 'Stochastic_D']
    ema_model_features = ['EMA']
    sma_model_features = ['SMA']
    vwap_model_features = ['VWAP']
    indicators_to_use = []

    model_features_mapping = {
        'base': base_model_features,
        'bb': bb_model_features,
        'macd': macd_model_features,
        'rsi': rsi_model_features,
        'stoch': stoch_model_features,
        'ema': ema_model_features,
        'sma': sma_model_features,
        'vwap': vwap_model_features
    }

    def __init__(self, indicators_to_use):
        self.indicators_to_use = indicators_to_use
        self.model_features = self._get_model_features()

    def _get_model_features(self):
        base_model_features = self.base_model_features
        model_features = []
        for indicator in self.indicators_to_use:
            model_features.extend(self.model_features_mapping[indicator])
        model_features.extend(base_model_features)
        return model_features

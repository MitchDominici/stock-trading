from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from src.trading.stocks import trade_signal
from src.ml.features import create_features
from src.ml.labeler import create_labels
from src.ml.model import save_model

FEATURE_COLUMNS = ['Lower_Band', 'Upper_Band', 'VWAP', 'MACD', 'Signal_Line']
TARGET_COLUMN = 'Signal'


def train_model(df, indicators):
    df_features = create_features(df, indicators)
    df_labeled = create_labels(df_features)

    X = df_labeled[['Lower_Band', 'Upper_Band', 'VWAP', 'MACD', 'Signal_Line']]
    y = df_labeled['Label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    # Test the model
    accuracy = model.score(X_test, y_test)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    return model


def train(df, indicators):
    """
     Train a predictive model based on the given dataframe and return it.
     """
    # Create features in the dataframe
    df = create_features(df, indicators)

    # Create target variable: 'buy' = 1, 'sell' = -1, 'hold' = 0
    df[TARGET_COLUMN] = df.apply(lambda row: 1 if trade_signal(row, indicators) == 'buy' else (
        -1 if trade_signal(row, indicators) == 'sell' else 0), axis=1)

    # Split data into training and test set
    X_train, X_test, y_train, y_test = train_test_split(df[FEATURE_COLUMNS], df[TARGET_COLUMN], test_size=0.2,
                                                        random_state=42)

    # Train a random forest classifier (you can also choose other models)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    # Test the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Model Accuracy: {accuracy * 100:.2f}%')
    save_model(model, '../data/ml_models/back_test_model.pkl')
    return model

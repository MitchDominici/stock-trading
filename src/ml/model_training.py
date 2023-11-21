import base64
import pickle
from datetime import date

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from src.config.config_manager import ConfigManager
from src.trading.brokerages.alpaca.alpaca_utils import convert_stock_price_list_to_df
from src.utils.stock_logger import StockLogger
from src.utils.utils import get_model_name


def get_model_data_for_insert(trainer, indicators_to_use):
    id = trainer.id
    model_name = get_model_name(trainer.model_to_use, indicators_to_use)
    training_date = trainer.training_date
    accuracy_score = trainer.accuracy_score
    classification_report = trainer.classification_report
    additional_info = trainer.additional_info
    model = trainer.ml_model
    serialized_model = pickle.dumps(model)
    encoded_model = base64.b64encode(serialized_model).decode('utf-8')
    model_data = [{
        'id': id,
        'model_name': model_name,
        'training_date': str(training_date),
        'accuracy_score': accuracy_score,
        'classification_report': classification_report,
        'model': encoded_model,
        'additional_info': additional_info,
        'model_version': trainer.version,
    }]
    return model_data


class ModelTraining:
    logger = StockLogger('ModelTraining')

    X_train = None
    X_test = None
    y_train = None
    y_test = None
    predictions = None
    accuracy_score = None
    classification_report = None
    labeled_stock_data = None
    training_date = None
    additional_info = None
    X_train_scaled = None
    X_test_scaled = None
    original_test_indices = None

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelTraining, cls).__new__(cls)
        return cls._instance

    def __init__(self, labeled_stock_data, model=None, version=None, _id=None, additional_info=None):
        self.labeled_stock_data = labeled_stock_data
        self.training_date = date.today()
        self.ml_model = model
        self.version = version or 1
        self.id = _id
        self.model_to_use = ConfigManager().get('trading_configs', 'model_to_use')

    def prepare_data(self):
        """
        Prepares data for training the ML model.

        :return: Split data into training and testing sets.
        """
        self.prep(self.labeled_stock_data)

        return self.X_train_scaled, self.X_test_scaled, self.y_train, self.y_test

    def prep(self, data):
        data.dropna(subset=['label'], inplace=True)

        X = data.select_dtypes(include=[np.number])
        y = data['label']

        # Splitting the data, retaining timestamps
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        self.original_test_indices = self.X_test.index

        # Standardizing the numerical data
        scaler = StandardScaler()
        self.X_train = scaler.fit_transform(self.X_train)
        self.X_test = scaler.transform(self.X_test)

        return self.X_train, self.X_test, self.y_train, self.y_test

    def prepare_data_for_multiple_stocks(self):
        combined_data = pd.concat(self.labeled_stock_data, ignore_index=True)
        self.prep(combined_data)

    def train_model(self, model=None):
        """
        Trains the ML model.

        :param X_train: Training features.
        :param y_train: Training labels.
        :return: Trained model.
        """

        if self.ml_model and model is None:
            self.ml_model.fit(self.X_train, self.y_train)
        elif model:
            model.fit(self.X_train, self.y_train)
            self.ml_model = model
            return model
        else:
            model = self.get_model_to_use()
            model.fit(self.X_train, self.y_train)
            self.ml_model = model
            return model

    def evaluate_model(self):
        """
        Evaluates the trained ML model.

        :param model: Trained ML model.
        :param X_test: Testing features.
        :param y_test: Testing labels.
        :return: Evaluation metrics.
        """
        self.predictions = self.ml_model.predict(self.X_test)
        self.accuracy_score = accuracy_score(self.y_test, self.predictions)
        self.classification_report = classification_report(self.y_test, self.predictions)

    def to_dict(self):
        return {
            'X_train': self.X_train,
            'X_test': self.X_test,
            'y_train': self.y_train,
            'y_test': self.y_test,
            'model': self.ml_model,
            'predictions': self.predictions,
            'accuracy_score': self.accuracy_score,
            'classification_report': self.classification_report,
            'stock_data': self.labeled_stock_data,
            'training_date': self.training_date,
            'additional_info': self.additional_info,
            'id': self.id,
        }

    def map_predictions(self, stock_price_data):
        stock_price_dataframes = convert_stock_price_list_to_df(stock_price_data)

        if len(self.predictions) == len(self.X_test):
            # Create a DataFrame with predictions and the corresponding indices
            predictions_df = pd.DataFrame({
                'model_prediction': self.predictions
            }, index=self.original_test_indices)

            # Merge predictions back into the combined stock data
            combined_stock_data = pd.concat(stock_price_dataframes)
            combined_stock_data = combined_stock_data.merge(predictions_df, left_index=True, right_index=True,
                                                            how='left')

            # Prepare JSON for database insertion
            predictions = [
                {
                    "stock_price_id": row['id'],  # Assign correct stock price ID
                    "symbol": row['symbol'],
                    "prediction": row['model_prediction'],
                    "prediction_date": str(date.today()),
                    "timestamp": row['timestamp'],
                    "model_version": self.version,
                    "model_id": self.id
                } for index, row in combined_stock_data.iterrows() if not pd.isna(row['model_prediction'])
            ]
            return predictions
        else:
            self.logger.logger.error("Length of predictions does not match the length of the test data.")

    def get_model_to_use(self):
        if self.model_to_use is not None:
            if self.model_to_use == 'random_forest':
                return RandomForestClassifier(random_state=42)
            elif self.model_to_use == 'logistic_regression':
                return LogisticRegression(random_state=42)
            elif self.model_to_use == 'svm':
                return SVC(random_state=42)
            elif self.model_to_use == 'knn':
                return KNeighborsClassifier()
            elif self.model_to_use == 'naive_bayes':
                return GaussianNB()
            elif self.model_to_use == 'decision_tree':
                return DecisionTreeClassifier(random_state=42)
            else:
                self.logger.logger.error(f"Invalid model_to_use: {self.model_to_use}")
        else:
            return RandomForestClassifier(random_state=42)
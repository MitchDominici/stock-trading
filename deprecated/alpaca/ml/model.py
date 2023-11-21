import os
import pickle

script_dir = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = 'data/ml_models/'


def save_model(model, filename):
    full_file_path = os.path.join(script_dir, '../..', MODEL_DIR, filename)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

    with open(full_file_path, 'wb') as model_file:
        pickle.dump(model, model_file)


def load_model(filename):
    full_file_path = os.path.join(script_dir, '../..', MODEL_DIR, filename)
    with open(full_file_path, 'rb') as model_file:
        loaded_model = pickle.load(model_file)
        return loaded_model

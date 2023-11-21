import argparse
import os

import yaml

from src.config.alpaca import AlpacaConfig
from src.config.postgres import PostgresConfig
from src.constants import global_chunk_size, global_days_to_get, global_paper_trading, global_live_trading


class ConfigService:
    alpaca_paper: AlpacaConfig
    alpaca_live: AlpacaConfig
    postgres: PostgresConfig
    args = None
    misc = None
    trading_configs = None

    def __init__(self):
        self.get_config()

    def __getitem__(self, config_name):
        return getattr(self, config_name)

    def get_config(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        config_file_path = os.path.join(script_dir, 'config.yml')
        try:
            with open(config_file_path, 'r') as yaml_file:
                yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
                self.alpaca_paper = self.get_alpaca_paper_from_yaml(yaml_data)
                self.alpaca_live = self.get_alpaca_live_from_yaml(yaml_data)
                self.postgres = self.get_postgres_from_yaml(yaml_data)
                self.misc = self.get_misc_data_from_yaml(yaml_data)
                self.trading_configs = self.get_trading_configs_from_yaml(yaml_data)
            self.get_args()
        except FileNotFoundError:
            print(
                f"FileNotFoundError: Could not find config file at {config_file_path}. Please make sure it exists and "
                f"try again."
            )
        except yaml.YAMLError as e:
            print(
                f"yaml.YAMLError: Could not parse config file at {config_file_path}. Please make sure it is valid YAML.")

    @staticmethod
    def get_alpaca_live_from_yaml(yaml_data):
        try:
            return AlpacaConfig(**yaml_data['alpaca']['live'])
        except Exception as e:
            if global_live_trading:
                raise e
            return None

    @staticmethod
    def get_alpaca_paper_from_yaml(yaml_data):
        try:
            return AlpacaConfig(**yaml_data['alpaca']['paper'])
        except Exception as e:
            if global_paper_trading:
                raise e
            return None

    @staticmethod
    def get_misc_data_from_yaml(yaml_data):
        try:
            return yaml_data['misc']
        except KeyError:
            return None

    @staticmethod
    def get_trading_configs_from_yaml(yaml_data):
        try:
            return yaml_data['trading_configs']
        except KeyError:
            return None

    @staticmethod
    def get_postgres_from_yaml(yaml_data):
        try:
            return PostgresConfig(**yaml_data['postgres'])
        except KeyError:
            return None

    def get_alpaca_config(self, live: bool = False) -> AlpacaConfig:
        if live:
            return self.alpaca_live
        else:
            return self.alpaca_paper

    def get_postgres_config(self) -> PostgresConfig:
        return self.postgres

    def get_args(self):
        if not self.args:
            parser = argparse.ArgumentParser(description="Configuration Manager for the application")

            parser.add_argument('--run_action', type=str,
                                help='The action to perform (e.g., download_stock_data, insert_tickers)',
                                required=False)
            parser.add_argument('--days_to_get', type=int,
                                help='The number of days of historical data to get', required=False)
            parser.add_argument('--chunk_size', type=int,
                                help='The number of tickers to process at a time', required=False)

            self.args = parser.parse_args()
        return self.args

    def get_run_action(self):
        return self.get_args().run_action or self.get('misc', 'default_run_action')

    def get_days_to_get(self):
        return self.get_args().days_to_get or int(self.get('misc', 'default_days_to_get') or global_days_to_get)

    def get_chunk_size(self):
        return self.get_args().chunk_size or int(self.get('misc', 'default_chunk_size') or global_chunk_size)

    def get_trading_configs(self):
        return self.trading_configs

    def get_indicators_to_use(self):
        return self.get('trading_configs', 'indicators_to_use')

    def get_days_of_stock_data_to_get(self):
        return self.get('trading_configs', 'days_of_stock_data_to_get')

    def get(self, config_name, key=None):
        try:
            if not key:
                return self[config_name]
            return self[config_name][key]
        except KeyError:
            return None

from src.config.alpaca import AlpacaConfig
from src.config.config_service import ConfigService
from src.config.postgres import PostgresConfig


class ConfigManager:
    _instance = None
    config_service: ConfigService = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.init_config_service()
        return cls._instance

    # def __getitem__(self, config_name):
    #     return getattr(self, config_name)

    def init_config_service(self):
        self.config_service = ConfigService()

    def get_alpaca_config(self, live: bool = False) -> AlpacaConfig:
        return self.config_service.get_alpaca_config(live)

    def get_postgres_config(self) -> PostgresConfig:
        return self.config_service.get_postgres_config()

    def get_args(self):
        return self.config_service.get_args()

    def get_run_action(self):
        return self.config_service.get_run_action()

    def get_days_to_get(self):
        return self.config_service.get_days_to_get()

    def get_chunk_size(self):
        return self.config_service.get_chunk_size()

    def get_trading_configs(self):
        return self.config_service.get_trading_configs()

    def get(self, config_name, key=None):
        try:
            return self.config_service.get(config_name, key)
        except KeyError:
            print(f"KeyError: Could not find key {key} in config {config_name}. Please make sure it exists and try again.")
            raise KeyError


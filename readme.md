
# Stock Trader

This project comprises a set of Python scripts designed to analyze, select, and trade high volatility stocks, particularly penny stocks, using machine learning models and automated trading strategies.



## Getting Started

### Prerequisites

- Python 3.x
- [Alpaca account](https://alpaca.markets/)

### Installation

1. Clone the repository:

```
git clone https://wild-kahuna@dev.azure.com/wild-kahuna/stock-trader/_git/stock-trader
cd stock-trader
```

2. Install required Python packages:

```
pip install -r requirements.txt
```

3. Add your Alpaca API keys:

Update the `config/config.yml` (or relevant file) with your Alpaca API key and secret.

Example config:
```yml
alpaca:
  paper:
    API_KEY: 
    API_SECRET: 
    API_URL: https://paper-api.alpaca.markets
  live:
    API_KEY:
    API_SECRET:
    API_URL: https://api.alpaca.markets
postgres:
  user: 
  password: 
  host: 
  port: 
  dbname: 
```

### Components

1. **backtest_ml.py**
   - **Purpose**: To backtest machine learning models using historical stock data.
   - **Command**: python main.py --run_action download_stock_data
   - **Features**:
     - Data cleaning and preparation for stock prices.
     - Feature engineering specific to stock data.
     - Label generation for ML models.
     - Training and backtesting of ML models.

2. **build_daily_watchlist.py**
   - **Purpose**: To build a daily watchlist of potential stocks for trading.
   - **Command**: python main.py --run_action build_daily_watchlist
   - **Features**:
     - Stock analysis to identify buy signals.
     - Compilation of a watchlist based on analysis results.

3. **download_stock_data.py**
   - **Purpose**: To download stock data for analysis and trading.
   - **Command**: python main.py --run_action download_stock_data
   - **Features**:
     - Fetching stock data for specified time frames.
     - Data storage for subsequent analysis.

4. **run_trader_bot.py**
   - **Purpose**: Main executable for the trading bot.
   - **Command**: python main.py --run_action run_trader_bot
   - **Features**:
     - Integrates ML models for trading decisions.
     - Processes trading signals.
     - Executes trades based on ML predictions and analysis.
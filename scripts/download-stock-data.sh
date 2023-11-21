#!/bin/bash
# Directory where your Python script is located
script_dir="C:/.important/projects/stock-trader"

cd "$script_dir" || exit

echo running download_stock_data

    # Run your Python script
./venv/Scripts/python.exe ./main.py --run_action download_stock_data

read -p "Press enter to continue"



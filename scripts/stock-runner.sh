#!/bin/bash
# Set the start time
start_time=$(date +%s)

# Calculate the end time (2 hours later)
end_time=$((start_time + 7200))

echo "start_time $(date -d @$start_time)"
echo "end_time $(date -d @$end_time)"

#echo "start_time $(date -d @$start_time)" >> stock-runner.log
#echo "end_time $(date -d @$end_time)" >> stock-runner.log

echo ""
echo "********************"
echo "starting stock-trader"
echo "********************"
echo ""

# Directory where your Python script is located
script_dir="C:/.important/projects/stock-trader"

#read -p "Press enter to continue"

# Loop until the current time is less than the end time
while [[ $(date +%s) -lt $end_time ]]; do
    # Change to the script directory
    cd "$script_dir" || exit
    echo running stock-trading
    # Run your Python script
    ./venv/Scripts/python.exe ./main.py --run_action run_trader_bot

    echo ""
    echo "--------------------"
    echo "Pausing for 1 minute"
    echo "--------------------"
    echo ""

    # Sleep for 1 minute before running again
    sleep 60
done

echo ""
echo "********************"
echo "stopping stock-trader"
echo "********************"
echo ""

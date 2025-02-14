#!/bin/bash

# Define the Python scripts
EXTRACT="extract.py"
TRANSFORM="transform.py"

echo "Starting the execution of $EXTRACT..."
# Run the first Python script
python3 "tasks/$EXTRACT"

# Check if the first script executed successfully
if [ $? -eq 0 ]; then
    echo "$EXTRACT executed successfully. Running $TRANSFORM..."
    # Run the second Python script
    python3 "tasks/$TRANSFORM"

    if [ $? -eq 0 ]; then
        echo "$TRANSFORM executed successfully."
    else
        echo "Error: $TRANSFORM failed to execute."
    fi
else
    echo "Error: $EXTRACT failed to execute. $TRANSFORM will not be run."
fi

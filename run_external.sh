#!/bin/bash

# Kill any existing Streamlit processes to free up ports
echo "Checking for existing Streamlit processes..."
pkill -f streamlit || true

# Run the app with external access
echo "Starting Streamlit app with external access..."
python run_external.py
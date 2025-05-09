#!/bin/bash

# Kill any existing Streamlit processes to free up ports
echo "Checking for existing Streamlit processes..."
pkill -f streamlit || true

# Run the app with public URL
echo "Starting Streamlit app with public URL..."
python run_public.py
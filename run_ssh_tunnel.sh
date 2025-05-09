#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if SSH is available
if ! command_exists ssh; then
    echo "Error: SSH is not installed. Please install SSH to use tunneling."
    exit 1
fi

# Kill any existing Streamlit processes to free up ports
echo "Checking for existing Streamlit processes..."
pkill -f streamlit || true

# Start Streamlit in the background with proper configuration
echo "Starting Streamlit app..."
streamlit run Home.py --server.port=8501 --server.enableCORS=true --server.enableXsrfProtection=false &
STREAMLIT_PID=$!

# Wait for Streamlit to start
echo "Waiting for Streamlit to start..."
sleep 5

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

# Display information
echo ""
echo "=============================================================="
echo "Streamlit app is running at:"
echo "  - Local URL:     http://localhost:8501"
echo "  - Network URL:   http://$LOCAL_IP:8501"
echo "=============================================================="
echo ""
echo "Creating SSH tunnel with serveo.net..."
echo "This will make your app available on the internet with a public URL."
echo ""

# Create SSH tunnel with serveo.net
echo "SSH tunnel command:"
echo "ssh -R 80:localhost:8501 serveo.net"
echo ""
echo "Starting tunnel now..."
echo ""

# Start the SSH tunnel
ssh -R 80:localhost:8501 serveo.net

# If SSH tunnel exits, kill the Streamlit process
kill $STREAMLIT_PID
echo "Streamlit app stopped."
#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Kill any existing Streamlit processes to free up ports
echo "Checking for existing Streamlit processes..."
pkill -f streamlit || true

# Start Streamlit in the background
echo "Starting Streamlit app..."
streamlit run Home.py --server.port=8501 --server.enableCORS=true --server.enableXsrfProtection=false &
STREAMLIT_PID=$!

# Wait for Streamlit to start
echo "Waiting for Streamlit to start..."
sleep 5

# Check if we can use ssh to create a tunnel
if command_exists ssh; then
    echo "You can create a secure tunnel using SSH with a command like:"
    echo "ssh -R 80:localhost:8501 serveo.net"
    echo ""
    echo "Or if you have a server with SSH access:"
    echo "ssh -R 8501:localhost:8501 your-server-username@your-server-ip"
    echo ""
fi

# Check if curl is available to use with localhost.run
if command_exists curl; then
    echo "You can create a public URL using localhost.run with this command:"
    echo "ssh -R 80:localhost:8501 localhost.run"
    echo ""
fi

echo "Your Streamlit app is running at:"
echo "Local URL:     http://localhost:8501"
echo "Network URL:   http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo "Press Ctrl+C to stop the server"

# Wait for user to press Ctrl+C
wait $STREAMLIT_PID
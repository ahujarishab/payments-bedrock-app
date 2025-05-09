import os
import sys
import streamlit.web.bootstrap as bootstrap
import socket
import subprocess
import time

def get_ip_address():
    """Get the local IP address of the machine"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def main():
    # Set Streamlit port
    port = 8501
    
    # Get the local IP address
    local_ip = get_ip_address()
    
    # Print access URLs
    print("\n" + "="*80)
    print("Your Streamlit app is running!")
    print("="*80)
    print("\nAccess URLs:")
    print(f"  - Local URL:     http://localhost:{port}")
    print(f"  - Network URL:   http://{local_ip}:{port}")
    print("\nTo create a public URL, you have several options:")
    print("  1. Use Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/")
    print("  2. Set up an ngrok account and get an auth token: https://dashboard.ngrok.com/signup")
    print("  3. Use localtunnel: npm install -g localtunnel")
    print("\nFor example, to use localtunnel after installing it:")
    print(f"  lt --port {port}")
    print("="*80 + "\n")
    
    # Run the Streamlit app
    os.environ["STREAMLIT_SERVER_PORT"] = str(port)
    bootstrap.run("Home.py", "", [], flag_options={})

if __name__ == "__main__":
    main()
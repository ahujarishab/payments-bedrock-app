import os
import sys
import streamlit.web.bootstrap as bootstrap
import socket

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
    
    # Set environment variables for Streamlit
    os.environ["STREAMLIT_SERVER_PORT"] = str(port)
    os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "true"
    os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
    
    # Print access URLs
    print("\n" + "="*80)
    print("Your Streamlit app is running with external access enabled!")
    print("="*80)
    print("\nAccess URLs:")
    print(f"  - Local URL:     http://localhost:{port}")
    print(f"  - Network URL:   http://{local_ip}:{port}")
    print(f"  - External URL:  http://<your-public-ip>:{port} (if port is exposed)")
    print("\nNOTE: To make your app accessible from the internet:")
    print("      1. Ensure your firewall allows incoming connections on port 8501")
    print("      2. If behind a router, set up port forwarding for port 8501")
    print("="*80 + "\n")
    
    # Run the Streamlit app
    bootstrap.run("Home.py", "", [], flag_options={})

if __name__ == "__main__":
    main()
# SSH Tunneling Guide for Streamlit Apps

SSH tunneling is a powerful method to expose your locally running Streamlit app to the internet without requiring additional tools or paid services. This guide explains how to set up SSH tunneling for your Streamlit application.

## What is SSH Tunneling?

SSH tunneling creates a secure connection between a local port on your machine and a remote server, allowing traffic to be forwarded through this encrypted connection. For our purposes, we'll use reverse tunneling (`-R` flag) to make our local Streamlit app accessible from the internet.

## Option 1: Using Serveo.net (Easiest)

[Serveo.net](https://serveo.net/) is a free service that provides SSH tunneling without requiring any registration.

1. First, start your Streamlit app with external access enabled:
   ```bash
   ./run_external.sh
   ```

2. In a new terminal, create an SSH tunnel using serveo.net:
   ```bash
   ssh -R 80:localhost:8501 serveo.net
   ```

3. Serveo will provide you with a public URL (e.g., https://randomname.serveo.net) that you can share with others.

## Option 2: Using localhost.run (Alternative Free Service)

[localhost.run](https://localhost.run/) is another free service similar to serveo.net.

1. Start your Streamlit app:
   ```bash
   ./run_external.sh
   ```

2. In a new terminal, create an SSH tunnel:
   ```bash
   ssh -R 80:localhost:8501 localhost.run
   ```

3. You'll receive a public URL that you can share.

## Option 3: Using Your Own Server

If you have access to a server with a public IP address, you can create a tunnel to it:

1. Start your Streamlit app:
   ```bash
   ./run_external.sh
   ```

2. Create an SSH tunnel to your server:
   ```bash
   ssh -R 8501:localhost:8501 username@your-server-ip
   ```

3. On your server, users can access your app at `http://your-server-ip:8501`

## SSH Tunneling Command Explained

The SSH command for tunneling has the following format:
```
ssh -R [remote_port]:localhost:[local_port] [username@]server
```

Where:
- `-R` specifies a reverse tunnel (from local to remote)
- `remote_port` is the port on the remote server (80 for HTTP)
- `local_port` is your Streamlit port (8501 by default)
- `server` is the remote server address

## Persistent Tunnels

To make your tunnel more persistent, you can add these options:

```bash
ssh -R 80:localhost:8501 -o ServerAliveInterval=60 -o ExitOnForwardFailure=yes serveo.net
```

This will:
- Send a keepalive packet every 60 seconds
- Exit if the forwarding fails, allowing you to restart the tunnel

## Security Considerations

1. **Authentication**: When using your own server, ensure it has proper authentication.
2. **Firewall**: Check that your server's firewall allows connections on the specified port.
3. **HTTPS**: Services like serveo.net provide HTTPS, which is important for secure connections.
4. **Temporary Access**: SSH tunnels are ideal for temporary access. For permanent solutions, consider proper hosting.

## Troubleshooting

1. **Connection refused**: Make sure your Streamlit app is running and accessible at localhost:8501
2. **Permission denied**: Check your SSH keys or credentials
3. **Tunnel closed**: Some networks block SSH tunneling; try a different network or port

## Alternative: Using autossh for Persistent Connections

For more reliable connections, you can use `autossh` which automatically restarts SSH if the connection drops:

1. Install autossh:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install autossh
   
   # On macOS with Homebrew
   brew install autossh
   ```

2. Create a persistent tunnel:
   ```bash
   autossh -M 0 -R 80:localhost:8501 serveo.net
   ```

The `-M 0` disables autossh's monitoring and relies on SSH's built-in mechanisms.
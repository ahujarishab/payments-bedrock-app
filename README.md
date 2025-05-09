# Payment Processing with AWS Bedrock

A multi-page Streamlit application that allows you to invoke and monitor multiple AWS Bedrock agents for payment processing.

## Features

- **Home Page**: Process payments using any of your configured AWS Bedrock agents
- **Execution History**: View the history of all agent executions with filtering options

## Supported Agents

The application supports the following agents:
- **Payment Orchestrator**: Handles the entire payment workflow
- **Payment Validator**: Validates payment details
- **Sanction Check**: Checks customer details against sanction lists

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Configure your AWS credentials and agent IDs:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use any text editor
```

3. Run the Streamlit app:

```bash
streamlit run Home.py
```

## Environment Variables

The application uses the following environment variables:

### AWS Credentials
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_SESSION_TOKEN`: (Optional) Your AWS session token for temporary credentials
- `AWS_DEFAULT_REGION`: AWS region (default: us-east-1)

### Agent Configuration
- `PAYMENT_ORCHESTRATOR_AGENT_ID`: Your Payment Orchestrator agent ID
- `PAYMENT_ORCHESTRATOR_AGENT_ALIAS_ID`: Your Payment Orchestrator agent alias ID
- `PAYMENT_VALIDATOR_AGENT_ID`: Your Payment Validator agent ID
- `PAYMENT_VALIDATOR_AGENT_ALIAS_ID`: Your Payment Validator agent alias ID
- `SANCTION_CHECK_AGENT_ID`: Your Sanction Check agent ID
- `SANCTION_CHECK_AGENT_ALIAS_ID`: Your Sanction Check agent alias ID

## Pages

### Home
- Select between Payment Orchestrator, Payment Validator, and Sanction Check agents
- Upload or edit payment JSON payloads
- Process payments through your selected agent
- View recent processing history

### Execution History
- View detailed history of all agent executions
- Filter by agent type and status
- See request and response payloads for each execution
- Manage execution history

## Required AWS Permissions

- `bedrock:InvokeAgent`
- `bedrock:GetAgent`
- `bedrock:GetAgentAlias`
- Related Bedrock permissions

## Security Note

- AWS credentials are stored in the .env file and loaded as environment variables
- The .env file is included in .gitignore to prevent accidental commits
- For production deployments, consider using IAM roles instead of access keys

## Running with External Access

To run the application with external access:

1. Use the provided script to run Streamlit with CORS enabled and XSRF protection disabled:
   ```bash
   ./run_external.sh
   ```

2. Access the application using:
   - Local URL: http://localhost:8501
   - Network URL: http://<your-local-ip>:8501 (for devices on your network)
   - External URL: http://<your-public-ip>:8501 (if port forwarding is set up)

## Creating a Public URL

To make your app accessible from anywhere on the internet, you have several options:

### Option 1: Using SSH Tunneling (No Installation Required)

1. Run the helper script that provides instructions:
   ```bash
   ./run_public_url.sh
   ```

2. Follow the instructions to create a tunnel using SSH:
   ```bash
   ssh -R 80:localhost:8501 serveo.net
   ```

3. Access the application using the URL provided by the service.

### Option 2: Using Ngrok (Requires Account)

1. Sign up for a free ngrok account: https://dashboard.ngrok.com/signup

2. Install ngrok and set up your auth token:
   ```bash
   # Install ngrok
   npm install -g ngrok
   # Set your auth token
   ngrok authtoken YOUR_AUTH_TOKEN
   ```

3. Run Streamlit with external access and ngrok in separate terminals:
   ```bash
   # Terminal 1: Run Streamlit with external access
   ./run_external.sh
   
   # Terminal 2: Run ngrok
   ngrok http 8501
   ```

### Option 3: Using Cloudflare Tunnel

For a more robust solution, consider using Cloudflare Tunnel:
https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/

### Notes on Public URL Configuration

- These public URLs are temporary and will change each time you run the script
- For a permanent URL, consider using a proper hosting solution like AWS App Runner, Heroku, or Streamlit Cloud
- Be aware of security implications when exposing your app to the internet
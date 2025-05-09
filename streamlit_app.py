import streamlit as st
import json
import boto3
import os
from botocore.exceptions import ClientError
from load_dotenv import load_env_file
from datetime import datetime

# Load environment variables from .env file if it exists
load_env_file()

# Set page configuration
st.set_page_config(
    page_title="AWS Bedrock Agent Invoker",
    page_icon="🤖",
    layout="wide"
)

# Add page navigation in sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Agent Invoker", "Agent Status Dashboard"])

# Initialize session state variables if they don't exist
if 'json_data' not in st.session_state:
    st.session_state.json_data = None
if 'response' not in st.session_state:
    st.session_state.response = None
if 'error' not in st.session_state:
    st.session_state.error = None
if 'aws_access_key_id' not in st.session_state:
    st.session_state.aws_access_key_id = ""
if 'aws_secret_access_key' not in st.session_state:
    st.session_state.aws_secret_access_key = ""
if 'aws_session_token' not in st.session_state:
    st.session_state.aws_session_token = ""

def invoke_bedrock_agent(agent_id, agent_alias_id, json_payload, region=None):
    """
    Invoke an AWS Bedrock agent with the provided JSON payload
    """
    try:
        # Initialize Bedrock Agent Runtime client with region
        bedrock_agent_runtime = boto3.client(
            'bedrock-agent-runtime',
            region_name=region if region else os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        )
        
        # Check if AWS credentials are configured
        if not os.environ.get('AWS_ACCESS_KEY_ID') and not boto3.Session().get_credentials():
            return {'error': "AWS credentials not configured. Please set your AWS credentials in the sidebar."}
        
        # Invoke the agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId='streamlit-session-' + str(hash(json.dumps(json_payload))),
            inputText=json.dumps(json_payload),
            enableTrace=True
        )
        
        # Process the response
        completion = ""
        for event in response.get("completion", []):
            if "chunk" in event:
                chunk = event["chunk"]
                completion += chunk["bytes"].decode()
            else:
            # Handle the missing key scenario
                completion += ""
        
        return {
            'response': completion,
            'trace': response.get('trace', {}),
            'sessionId': response.get('sessionId', '')
        }
    except ClientError as e:
        return {'error': f"Error invoking Bedrock agent: {str(e)}"}
    except Exception as e:
        return {'error': f"Unexpected error: {str(e)}"}

# App title and description
st.title("🤖 AWS Bedrock Agent Invoker")
st.markdown("""
Upload a JSON payload and invoke an AWS Bedrock agent with the click of a button.
Make sure you have the necessary AWS credentials configured.
""")

# Sidebar for AWS configuration
st.sidebar.header("AWS Configuration")

# AWS Region selection
aws_region = st.sidebar.text_input("AWS Region", value="us-east-1")
os.environ['AWS_DEFAULT_REGION'] = aws_region

# AWS Credentials
st.sidebar.subheader("AWS Credentials")
with st.sidebar.expander("Configure AWS Credentials", expanded=False):
    aws_access_key_id = st.text_input(
        "AWS Access Key ID", 
        value=st.session_state.aws_access_key_id,
        type="password",
        help="Your AWS Access Key ID"
    )
    aws_secret_access_key = st.text_input(
        "AWS Secret Access Key", 
        value=st.session_state.aws_secret_access_key,
        type="password",
        help="Your AWS Secret Access Key"
    )
    aws_session_token = st.text_input(
        "AWS Session Token (optional)", 
        value=st.session_state.aws_session_token,
        type="password",
        help="Only needed for temporary credentials"
    )
    
    if st.button("Save AWS Credentials"):
        st.session_state.aws_access_key_id = aws_access_key_id
        st.session_state.aws_secret_access_key = aws_secret_access_key
        st.session_state.aws_session_token = aws_session_token
        
        # Set environment variables
        os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key_id
        os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_access_key
        if aws_session_token:
            os.environ['AWS_SESSION_TOKEN'] = aws_session_token
        
        st.success("AWS credentials saved and environment variables set!")

# Agent configuration
agent_id = st.sidebar.text_input("Bedrock Agent ID", placeholder="Enter your agent ID")
agent_alias_id = st.sidebar.text_input("Bedrock Agent Alias ID", placeholder="Enter your agent alias ID")

# File uploader for JSON
st.subheader("Upload JSON Payload")
uploaded_file = st.file_uploader("Choose a JSON file", type=['json'])

# JSON editor
st.subheader("Or Edit JSON Directly")
if uploaded_file is not None:
    # If file is uploaded, load its content
    try:
        content = uploaded_file.getvalue().decode('utf-8')
        st.session_state.json_data = json.loads(content)
    except json.JSONDecodeError:
        st.error("Invalid JSON file. Please upload a valid JSON.")
        st.session_state.json_data = None
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        st.session_state.json_data = None

# JSON editor
json_input = st.text_area(
    "JSON Payload", 
    value=json.dumps(st.session_state.json_data, indent=2) if st.session_state.json_data else '{\n  "key": "value"\n}',
    height=300,
    help="Enter valid JSON with double-quoted keys. Example: {\"key\": \"value\"}"
)

# Parse JSON input
try:
    st.session_state.json_data = json.loads(json_input)
    st.success("Valid JSON format")
except json.JSONDecodeError as e:
    st.error(f"Invalid JSON format: {str(e)}")
    st.session_state.json_data = None

# Invoke button
col1, col2 = st.columns([1, 3])
with col1:
    # Check if AWS credentials are configured
    aws_creds_configured = bool(os.environ.get('AWS_ACCESS_KEY_ID') or boto3.Session().get_credentials())
    
    if st.button("Invoke Bedrock Agent", type="primary", disabled=not all([agent_id, agent_alias_id, st.session_state.json_data])):
        with st.spinner("Invoking Bedrock agent..."):
            if not aws_creds_configured:
                st.session_state.error = "AWS credentials not configured. Please set your AWS credentials in the sidebar."
                st.session_state.response = None
            else:
                result = invoke_bedrock_agent(agent_id, agent_alias_id, st.session_state.json_data, aws_region)
                
                if 'error' in result:
                    st.session_state.error = result['error']
                    st.session_state.response = None
                else:
                    st.session_state.response = result
                    st.session_state.error = None

# Display requirements for invocation
with col2:
    if not agent_id:
        st.info("⚠️ Please enter an Agent ID in the sidebar")
    if not agent_alias_id:
        st.info("⚠️ Please enter an Agent Alias ID in the sidebar")
    if not st.session_state.json_data:
        st.info("⚠️ Please provide a valid JSON payload")
    
    # Check if AWS credentials are configured
    aws_creds_configured = bool(os.environ.get('AWS_ACCESS_KEY_ID') or boto3.Session().get_credentials())
    if not aws_creds_configured:
        st.warning("⚠️ AWS credentials not configured. Please set your AWS credentials in the sidebar.")

# Display response
if st.session_state.error:
    st.error(st.session_state.error)

if st.session_state.response:
    st.subheader("Agent Response")
    
    # Display the completion
    st.markdown("### Completion")
    st.write(st.session_state.response.get('response', 'No response data'))
    
    # Display session ID
    st.markdown("### Session ID")
    st.code(st.session_state.response.get('sessionId', 'No session ID'))
    
    # Display trace information if available
    if 'trace' in st.session_state.response and st.session_state.response['trace']:
        st.markdown("### Trace Information")
        st.json(st.session_state.response['trace'])

# Add information about AWS credentials status
st.sidebar.markdown("---")
st.sidebar.subheader("AWS Credentials Status")

# Check if AWS credentials are configured
aws_creds_configured = bool(os.environ.get('AWS_ACCESS_KEY_ID') or boto3.Session().get_credentials())
if aws_creds_configured:
    st.sidebar.success("✅ AWS credentials are configured")
else:
    st.sidebar.error("❌ AWS credentials are not configured")

st.sidebar.info("""
Required AWS permissions:
- `bedrock:InvokeAgent`
- Related Bedrock permissions

Note: Your AWS credentials are stored only in this session and are not saved permanently.
""")
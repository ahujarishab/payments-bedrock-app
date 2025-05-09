import streamlit as st
import boto3
import os
from load_dotenv import get_aws_credentials, get_agent_credentials
from agent_utils import get_agent_options, check_agent_configuration
from aws_client import check_aws_credentials

def display_aws_config_sidebar():
    """
    Display AWS configuration status in the sidebar
    """
    st.sidebar.header("AWS Configuration")
    aws_creds = get_aws_credentials()
    aws_creds_configured = check_aws_credentials()

    if aws_creds_configured:
        st.sidebar.success("✅ AWS credentials are configured")
        st.sidebar.info(f"Region: {aws_creds['aws_region']}")
    else:
        st.sidebar.error("❌ AWS credentials are not configured")
        st.sidebar.warning("Please set AWS credentials in your .env file")
    
    return aws_creds_configured

def display_agent_config_sidebar():
    """
    Display agent configuration status in the sidebar
    """
    st.sidebar.header("Agent Configuration")
    agent_creds = get_agent_credentials()
    agent_options = get_agent_options()
    
    # Display status for all agents
    for agent_key, agent_name in agent_options.items():
        agent_id = agent_creds[f'{agent_key}_agent_id']
        agent_alias_id = agent_creds[f'{agent_key}_agent_alias_id']
        
        st.sidebar.subheader(f"{agent_name}")
        if agent_id and agent_alias_id:
            st.sidebar.success("✅ Configured")
            st.sidebar.info(f"Agent ID: {agent_id[:5]}...{agent_id[-5:] if len(agent_id) > 10 else ''}")
        else:
            st.sidebar.error("❌ Not configured")
            st.sidebar.warning(f"Please set {agent_key.upper()}_AGENT_ID and {agent_key.upper()}_AGENT_ALIAS_ID in your .env file")

def display_agent_selector(default_agent="payment_orchestrator"):
    """
    Display agent selection radio buttons
    """
    st.subheader("Select Agent")
    agent_options = get_agent_options()
    
    selected_agent = st.radio(
        "Choose which agent to use:",
        list(agent_options.keys()),
        format_func=lambda x: agent_options[x],
        horizontal=True,
        index=list(agent_options.keys()).index(st.session_state.selected_agent) 
              if 'selected_agent' in st.session_state and st.session_state.selected_agent in agent_options 
              else list(agent_options.keys()).index(default_agent)
    )
    
    # Update session state
    if 'selected_agent' not in st.session_state:
        st.session_state.selected_agent = selected_agent
    else:
        st.session_state.selected_agent = selected_agent
    
    return selected_agent

def display_json_editor(default_json):
    """
    Display JSON editor with file upload option
    """
    # File uploader for JSON
    st.subheader("Upload JSON Payload")
    uploaded_file = st.file_uploader("Choose a JSON file", type=['json'])

    # JSON editor
    st.subheader("Or Edit JSON Directly")
    if uploaded_file is not None:
        # If file is uploaded, load its content
        try:
            import json
            content = uploaded_file.getvalue().decode('utf-8')
            st.session_state.json_data = json.loads(content)
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please upload a valid JSON.")
            st.session_state.json_data = None
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.session_state.json_data = None

    # JSON editor
    import json
    json_input = st.text_area(
        "JSON Payload", 
        value=json.dumps(st.session_state.json_data, indent=2) if 'json_data' in st.session_state and st.session_state.json_data else default_json,
        height=400,
        help="Enter valid JSON with double-quoted keys. Example: {\"key\": \"value\"}"
    )

    # Parse JSON input
    try:
        json_data = json.loads(json_input)
        st.success("Valid JSON format")
        st.session_state.json_data = json_data
        return json_data
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON format: {str(e)}")
        st.session_state.json_data = None
        return None

def display_configuration_info():
    """
    Display configuration information in the sidebar
    """
    st.sidebar.markdown("---")
    st.sidebar.info("""
    ## Configuration Instructions

    To configure AWS credentials and agent IDs:

    1. Copy `.env.example` to `.env`
    2. Edit the `.env` file with your credentials
    3. Restart the application

    Required AWS permissions:
    - `bedrock:InvokeAgent`
    - `bedrock:GetAgent`
    - `bedrock:GetAgentAlias`
    - Related Bedrock permissions
    """)
import streamlit as st
import json
import os
from load_dotenv import load_env_file
from aws_client import setup_aws_environment, check_aws_credentials
from agent_utils import invoke_agent, get_agent_options, check_agent_configuration
from ui_components import (
    display_agent_selector,
    display_json_editor,
    display_configuration_info
)
from session_state import initialize_session_state, get_default_json_template

# Load environment variables from .env file if it exists
load_env_file()

# Set up AWS environment
aws_creds = setup_aws_environment()

# Set page configuration
st.set_page_config(
    page_title="Payment Orchestrator",
    page_icon="💳",
    layout="wide"
)

# Hide the default sidebar
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Hide the navigation arrow */
    .e10vaf9m1, .st-emotion-cache-1f3w014, .ex0cdmw0, svg[class*="st-emotion-cache"] {
        display: none !important;
    }
    
    .back-button {
        margin-bottom: 20px;
    }
    
    .back-button button {
        background-color: #f0f0f0 !important;
        color: #333 !important;
        border: none !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
initialize_session_state()

# Add a back button above the title
st.markdown('<div class="back-button">', unsafe_allow_html=True)
if st.button("← Back to Dashboard"):
    st.switch_page("Home.py")
st.markdown('</div>', unsafe_allow_html=True)

# App title and description
st.title("💳 Payment Processing")
st.markdown("""
Upload a payment JSON payload and process it using AWS Bedrock agents.
Choose which agent to use for processing your payment.
""")

# Agent selection
selected_agent = display_agent_selector()

# JSON editor with file upload option
json_data = display_json_editor(get_default_json_template())

# Invoke button
col1, col2 = st.columns([1, 3])
with col1:
    # Check if AWS credentials and agent are configured
    agent_configured = check_agent_configuration(selected_agent)
    agent_options = get_agent_options()
    aws_creds_configured = check_aws_credentials()
    
    button_label = f"Process with {agent_options[selected_agent]}"
    
    if st.button(button_label, type="primary", disabled=not all([agent_configured, aws_creds_configured, json_data])):
        with st.spinner(f"Processing with {agent_options[selected_agent]}..."):
            result = invoke_agent(selected_agent, json_data, aws_creds['aws_region'])
            
            if 'error' in result:
                st.session_state.error = result['error']
                st.session_state.response = None
            else:
                st.session_state.response = result
                st.session_state.error = None

# Display requirements for invocation
with col2:
    if not agent_configured:
        st.info(f"⚠️ {agent_options[selected_agent]} agent not configured. Please set the agent ID and alias ID in your .env file.")
    if not json_data:
        st.info("⚠️ Please provide a valid JSON payload")
    
    # Check if AWS credentials are configured
    if not aws_creds_configured:
        st.warning("⚠️ AWS credentials not configured. Please set your AWS credentials in the .env file.")

# Display response
if st.session_state.error:
    st.error(st.session_state.error)

if st.session_state.response:
    st.subheader("Processing Response")
    
    # Display the completion
    st.markdown("### Result")
    st.write(st.session_state.response.get('response', 'No response data'))
    
    # Display session ID
    st.markdown("### Session ID")
    st.code(st.session_state.response.get('sessionId', 'No session ID'))
    
    # Display trace information if available
    if 'trace' in st.session_state.response and st.session_state.response['trace']:
        with st.expander("Trace Information"):
            st.json(st.session_state.response['trace'])

# Recent payment history
if st.session_state.payment_history:
    st.subheader("Recent Processing History")
    
    for i, history_item in enumerate(reversed(st.session_state.payment_history[:3])):
        agent_type = history_item.get('agent_type', 'unknown')
        agent_display_name = agent_options.get(agent_type, agent_type.replace('_', ' ').title())
        
        with st.expander(f"Request {i+1} - {history_item['timestamp']} - {agent_display_name} - {history_item['status']}"):
            st.write("**Request:**")
            st.json(history_item['payload'])
            st.write("**Response:**")
            st.write(history_item['response'])

# Add information about configuration
display_configuration_info()
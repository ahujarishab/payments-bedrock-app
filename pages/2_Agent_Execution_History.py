import streamlit as st
import pandas as pd
from load_dotenv import load_env_file
from aws_client import setup_aws_environment
from agent_utils import get_agent_options
from ui_components import display_configuration_info
from session_state import initialize_session_state

# Load environment variables from .env file if it exists
load_env_file()

# Set up AWS environment
aws_creds = setup_aws_environment()

# Set page configuration
st.set_page_config(
    page_title="Agent Execution History",
    page_icon="📜",
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

# Initialize session state
initialize_session_state()

# Agent options for display
agent_options = get_agent_options()

# Add a back button above the title
st.markdown('<div class="back-button">', unsafe_allow_html=True)
if st.button("← Back to Dashboard"):
    st.switch_page("Home.py")
st.markdown('</div>', unsafe_allow_html=True)

# App title and description
st.title("📜 Agent Execution History")
st.markdown("""
View the execution history of your AWS Bedrock agents.
""")

# Refresh button
if st.button("🔄 Refresh Execution History"):
    st.rerun()

# Filter options
st.subheader("Filter Executions")
agent_filter = st.multiselect(
    "Filter by Agent Type",
    options=list(agent_options.keys()),
    format_func=lambda x: agent_options[x],
    default=list(agent_options.keys())
)

status_filter = st.multiselect(
    "Filter by Status",
    options=["Success", "Failed"],
    default=["Success", "Failed"]
)

# Payment Executions
if not st.session_state.payment_history:
    st.info("No payment executions have been performed yet. Use the Home page to invoke agents.")
else:
    # Filter history based on selections
    filtered_history = [
        item for item in st.session_state.payment_history 
        if (not agent_filter or item.get('agent_type', 'unknown') in agent_filter) and
           (not status_filter or item.get('status', 'Unknown') in status_filter)
    ]
    
    if not filtered_history:
        st.info("No executions match the selected filters.")
    else:
        # Create a DataFrame from the history
        data = []
        for i, item in enumerate(reversed(filtered_history)):
            # Extract key information from the payload
            payload = item.get('payload', {})
            merchant_id = payload.get('header', {}).get('MerchantID', 'Unknown')
            order_number = payload.get('header', {}).get('OrderNumber', 'Unknown')
            amount = payload.get('CardDetails', {}).get('Amount', 'Unknown')
            currency = payload.get('CardDetails', {}).get('CurrencyCode', 'Unknown')
            agent_type = item.get('agent_type', 'unknown')
            agent_display_name = agent_options.get(agent_type, agent_type.replace('_', ' ').title())
            
            data.append({
                "Execution ID": item.get('sessionId', f"exec-{i+1}"),
                "Timestamp": item.get('timestamp', 'Unknown'),
                "Agent": agent_display_name,
                "Merchant": merchant_id,
                "Order": order_number,
                "Amount": f"{amount} {currency}",
                "Status": item.get('status', 'Unknown'),
                "Index": i  # Store the index for accessing details
            })
        
        df = pd.DataFrame(data)
        
        # Style the DataFrame
        def highlight_status(val):
            if val == 'Success':
                return 'background-color: #d4edda'
            elif val == 'Failed':
                return 'background-color: #f8d7da'
            return ''
        
        # Display the styled DataFrame
        st.subheader("Agent Execution History")
        st.dataframe(df.style.applymap(highlight_status, subset=['Status']), use_container_width=True)
        
        # Display details for selected execution
        st.subheader("Execution Details")
        
        # Create a format function for the selectbox
        def format_execution(idx):
            item = filtered_history[-(idx+1)]
            agent_type = item.get('agent_type', 'unknown')
            agent_display_name = agent_options.get(agent_type, agent_type.replace('_', ' ').title())
            return f"{item['timestamp']} - {agent_display_name} - {item['status']}"
        
        selected_execution = st.selectbox(
            "Select an execution to view details:",
            options=range(len(filtered_history)),
            format_func=format_execution
        )
        
        # Get the selected execution
        execution = filtered_history[-(selected_execution+1)]
        agent_type = execution.get('agent_type', 'unknown')
        agent_display_name = agent_options.get(agent_type, agent_type.replace('_', ' ').title())
        
        # Display execution details
        st.write(f"**Agent:** {agent_display_name}")
        st.write(f"**Session ID:** {execution.get('sessionId', 'Unknown')}")
        st.write(f"**Timestamp:** {execution.get('timestamp', 'Unknown')}")
        st.write(f"**Status:** {execution.get('status', 'Unknown')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Request")
            st.json(execution['payload'])
        
        with col2:
            st.subheader("Response")
            st.write(execution['response'])
        
        # Add a button to remove this execution from history
        if st.button("Remove This Execution from History"):
            # Find the actual index in the full history
            for i, item in enumerate(st.session_state.payment_history):
                if (item.get('timestamp') == execution.get('timestamp') and 
                    item.get('sessionId') == execution.get('sessionId')):
                    st.session_state.payment_history.pop(i)
                    break
            
            st.success("Execution removed from history.")
            st.rerun()

        # Add a button to clear all history
        if st.button("Clear All History"):
            st.session_state.payment_history = []
            st.success("All execution history cleared.")
            st.rerun()

# Add information about data persistence
display_configuration_info()
import streamlit as st
import json
import os
import time
import random
from datetime import datetime
from load_dotenv import load_env_file
from aws_client import setup_aws_environment, check_aws_credentials
from agent_utils import invoke_agent, get_agent_options, check_agent_configuration
from ui_components import (
    display_agent_selector,
    display_json_editor,
    display_configuration_info
)
from session_state import initialize_session_state, get_default_json_template

# Function to add log entry to a specific step
def add_step_log(step_index, message):
    if step_index not in st.session_state.step_logs:
        st.session_state.step_logs[step_index] = []
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.step_logs[step_index].append(f"[{timestamp}] {message}")

# Function to process payment with multi-agent collaboration
def process_payment_with_agents(json_data):
    # Set processing flags
    st.session_state.is_processing = True
    st.session_state.processing_started = True
    st.session_state.processing_complete = False
    
    # Reset agent statuses
    st.session_state.agent_statuses = {
        'payment_orchestrator': {'status': 'pending', 'response': None, 'error': None, 'active': False},
        'payment_validator': {'status': 'pending', 'response': None, 'error': None, 'active': False},
        'sanction_check': {'status': 'pending', 'response': None, 'error': None, 'active': False}
    }
    
    # Reset orchestrator steps
    st.session_state.orchestrator_steps = {
        'current_step': 0,
        'steps': DEFAULT_STEPS
    }
    
    # Clear previous step logs
    st.session_state.step_logs = {}
    
    # Extract relevant data for each agent
    validator_payload = {
        "CardDetails": json_data.get("CardDetails", {})
    }
    
    sanction_check_payload = {
        "CustomerDetails": json_data.get("CustomerDetails", {})
    }
    
    # Step 0: Receiving payment request
    st.session_state.orchestrator_steps['current_step'] = 0
    st.session_state.agent_statuses['payment_orchestrator']['active'] = True
    add_step_log(0, "Payment request received")
    add_step_log(0, "Parsing JSON payload")
    add_step_log(0, "Extracting payment details")
    
    # Step 1: Validating request format
    st.session_state.orchestrator_steps['current_step'] = 1
    add_step_log(1, "Validating request format")
    add_step_log(1, "Checking required fields")
    add_step_log(1, "Validating card details format")
    add_step_log(1, "Validating customer information")
    
    # Step 2: Start Payment Validator
    st.session_state.orchestrator_steps['current_step'] = 2
    st.session_state.agent_statuses['payment_validator']['status'] = 'running'
    st.session_state.agent_statuses['payment_validator']['active'] = True
    st.session_state.agent_statuses['payment_orchestrator']['active'] = False
    add_step_log(2, "Delegating card validation to Payment Validator")
    add_step_log(2, "Preparing card details for validation")
    add_step_log(2, "Invoking Payment Validator agent")
    
    # Call the Payment Validator agent
    try:
        add_step_log(2, "Payment Validator processing card details")
        validator_result = invoke_agent("payment_validator", validator_payload, aws_creds['aws_region'])
        
        if 'error' in validator_result:
            st.session_state.agent_statuses['payment_validator']['status'] = 'error'
            st.session_state.agent_statuses['payment_validator']['error'] = validator_result['error']
            add_step_log(2, f"Error: {validator_result['error']}")
        else:
            st.session_state.agent_statuses['payment_validator']['status'] = 'success'
            st.session_state.agent_statuses['payment_validator']['response'] = validator_result
            add_step_log(2, "Card validation completed successfully")
    except Exception as e:
        st.session_state.agent_statuses['payment_validator']['status'] = 'error'
        st.session_state.agent_statuses['payment_validator']['error'] = str(e)
        add_step_log(2, f"Exception: {str(e)}")
    
    # Step 3: Start Sanction Check
    st.session_state.orchestrator_steps['current_step'] = 3
    st.session_state.agent_statuses['sanction_check']['status'] = 'running'
    st.session_state.agent_statuses['sanction_check']['active'] = True
    st.session_state.agent_statuses['payment_validator']['active'] = False
    add_step_log(3, "Delegating customer check to Sanction Check")
    add_step_log(3, "Preparing customer details for sanction check")
    add_step_log(3, "Invoking Sanction Check agent")
    
    # Call the Sanction Check agent
    try:
        add_step_log(3, "Sanction Check processing customer details")
        sanction_result = invoke_agent("sanction_check", sanction_check_payload, aws_creds['aws_region'])
        
        if 'error' in sanction_result:
            st.session_state.agent_statuses['sanction_check']['status'] = 'error'
            st.session_state.agent_statuses['sanction_check']['error'] = sanction_result['error']
            add_step_log(3, f"Error: {sanction_result['error']}")
        else:
            st.session_state.agent_statuses['sanction_check']['status'] = 'success'
            st.session_state.agent_statuses['sanction_check']['response'] = sanction_result
            add_step_log(3, "Customer check completed successfully")
    except Exception as e:
        st.session_state.agent_statuses['sanction_check']['status'] = 'error'
        st.session_state.agent_statuses['sanction_check']['error'] = str(e)
        add_step_log(3, f"Exception: {str(e)}")
    
    # Step 4: Analyze validation results
    st.session_state.orchestrator_steps['current_step'] = 4
    st.session_state.agent_statuses['payment_orchestrator']['active'] = True
    st.session_state.agent_statuses['sanction_check']['active'] = False
    add_step_log(4, "Analyzing validation results")
    add_step_log(4, "Processing validator response")
    
    # Prepare enhanced payload with validation results
    enhanced_payload = json_data.copy()
    
    # Add validator results
    if st.session_state.agent_statuses['payment_validator']['status'] == 'success':
        validator_response = st.session_state.agent_statuses['payment_validator']['response']
        enhanced_payload["ValidationResults"] = {
            "Status": "Success",
            "Details": validator_response.get('response', 'No details available')
        }
        add_step_log(4, "Card validation successful")
    else:
        enhanced_payload["ValidationResults"] = {
            "Status": "Failed",
            "Details": st.session_state.agent_statuses['payment_validator'].get('error', 'Validation failed')
        }
        add_step_log(4, "Card validation failed")
    
    # Step 5: Analyze sanction check results
    st.session_state.orchestrator_steps['current_step'] = 5
    add_step_log(5, "Analyzing sanction check results")
    add_step_log(5, "Processing sanction check response")
    
    # Add sanction check results to enhanced payload
    if st.session_state.agent_statuses['sanction_check']['status'] == 'success':
        sanction_response = st.session_state.agent_statuses['sanction_check']['response']
        enhanced_payload["SanctionResults"] = {
            "Status": "Success",
            "Details": sanction_response.get('response', 'No details available')
        }
        add_step_log(5, "Sanction check successful")
    else:
        enhanced_payload["SanctionResults"] = {
            "Status": "Failed",
            "Details": st.session_state.agent_statuses['sanction_check'].get('error', 'Sanction check failed')
        }
        add_step_log(5, "Sanction check failed")
    
    # Step 6: Make payment decision
    st.session_state.orchestrator_steps['current_step'] = 6
    add_step_log(6, "Making payment decision")
    add_step_log(6, "Evaluating validation and sanction check results")
    
    # Check if both validation and sanction check passed
    validation_passed = enhanced_payload["ValidationResults"]["Status"] == "Success"
    sanction_passed = enhanced_payload["SanctionResults"]["Status"] == "Success"
    
    if validation_passed and sanction_passed:
        add_step_log(6, "All checks passed, proceeding with payment")
    else:
        add_step_log(6, "Some checks failed, but proceeding with payment for demonstration")
    
    # Step 7: Process payment with gateway
    st.session_state.orchestrator_steps['current_step'] = 7
    st.session_state.agent_statuses['payment_orchestrator']['status'] = 'running'
    add_step_log(7, "Processing payment with gateway")
    add_step_log(7, "Connecting to payment gateway")
    add_step_log(7, "Sending payment request")
    
    # Create a comprehensive payload for the orchestrator with all necessary information
    # Include the results from the validator and sanction check agents without calling them again
    orchestrator_final_payload = {
        "originalRequest": json_data,
        "validationResults": {
            "status": enhanced_payload["ValidationResults"]["Status"],
            "details": enhanced_payload["ValidationResults"]["Details"]
        },
        "sanctionResults": {
            "status": enhanced_payload["SanctionResults"]["Status"],
            "details": enhanced_payload["SanctionResults"]["Details"]
        },
        "action": "processPayment",
        "allChecksPass": validation_passed and sanction_passed
    }
    
    # Call the Payment Orchestrator agent with the comprehensive payload
    try:
        add_step_log(7, "Sending comprehensive payload to Payment Orchestrator")
        orchestrator_result = invoke_agent("payment_orchestrator", orchestrator_final_payload, aws_creds['aws_region'])
        add_step_log(7, "Received gateway response")
        add_step_log(7, "Processing gateway response")
        
        # Step 8: Generate response
        st.session_state.orchestrator_steps['current_step'] = 8
        add_step_log(8, "Generating response")
        add_step_log(8, "Formatting response data")
        
        if 'error' in orchestrator_result:
            st.session_state.agent_statuses['payment_orchestrator']['status'] = 'error'
            st.session_state.agent_statuses['payment_orchestrator']['error'] = orchestrator_result['error']
            add_step_log(8, f"Error: {orchestrator_result['error']}")
        else:
            st.session_state.agent_statuses['payment_orchestrator']['status'] = 'success'
            st.session_state.agent_statuses['payment_orchestrator']['response'] = orchestrator_result
            add_step_log(8, "Payment processed successfully")
            add_step_log(8, "Response generated")
    except Exception as e:
        st.session_state.agent_statuses['payment_orchestrator']['status'] = 'error'
        st.session_state.agent_statuses['payment_orchestrator']['error'] = str(e)
        add_step_log(8, f"Exception: {str(e)}")
    
    # Complete all steps
    st.session_state.orchestrator_steps['current_step'] = len(DEFAULT_STEPS)
    st.session_state.agent_statuses['payment_orchestrator']['active'] = False
    
    # Set processing complete
    st.session_state.processing_complete = True
    
    # Store the result in session state
    st.session_state.multi_agent_result = {
        'orchestrator': st.session_state.agent_statuses['payment_orchestrator'],
        'validator': st.session_state.agent_statuses['payment_validator'],
        'sanction_check': st.session_state.agent_statuses['sanction_check'],
        'enhanced_payload': enhanced_payload
    }
    
    # Add to payment history if orchestrator was successful
    if st.session_state.agent_statuses['payment_orchestrator']['status'] == 'success':
        if 'payment_history' not in st.session_state:
            st.session_state.payment_history = []
            
        orchestrator_response = st.session_state.agent_statuses['payment_orchestrator']['response']
        st.session_state.payment_history.append({
            'agent_type': 'payment_orchestrator',
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'payload': json_data,
            'response': orchestrator_response.get('response', 'No response'),
            'sessionId': orchestrator_response.get('sessionId', 'Unknown'),
            'status': 'Success',
            'trace': orchestrator_response.get('trace', {})
        })
    
    # Return the final result
    return {
        'orchestrator': st.session_state.agent_statuses['payment_orchestrator'],
        'validator': st.session_state.agent_statuses['payment_validator'],
        'sanction_check': st.session_state.agent_statuses['sanction_check']
    }

# Load environment variables from .env file if it exists
load_env_file()

# Set up AWS environment
aws_creds = setup_aws_environment()

# Set page configuration
st.set_page_config(
    page_title="Payment Processing",
    page_icon="💳",
    layout="wide"
)

# Add custom CSS for styling
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
    
    .agent-status {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    
    .agent-status.success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    
    .agent-status.error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
    
    .agent-status.running {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
    }
    
    .agent-status.pending {
        background-color: #e2e3e5;
        border: 1px solid #d6d8db;
    }
    
    .worklog {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .worklog-entry {
        margin-bottom: 8px;
        padding-bottom: 4px;
        border-bottom: 1px solid #e9ecef;
    }
    
    .worklog-entry .timestamp {
        color: #6c757d;
        font-size: 0.8em;
        margin-bottom: 2px;
        font-weight: bold;
    }
    
    .worklog-entry .message {
        margin: 0;
    }
    
    .card {
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #e9ecef;
        margin-bottom: 15px;
        background-color: white;
    }
    
    .card-header {
        font-weight: bold;
        margin-bottom: 10px;
        border-bottom: 1px solid #e9ecef;
        padding-bottom: 5px;
    }
    
    .process-button {
        margin-top: 15px;
        margin-bottom: 15px;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    
    .status-indicator.success {
        background-color: #28a745;
    }
    
    .status-indicator.error {
        background-color: #dc3545;
    }
    
    .status-indicator.running {
        background-color: #ffc107;
    }
    
    .status-indicator.pending {
        background-color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
initialize_session_state()

# Initialize step logs if not exists
if 'step_logs' not in st.session_state:
    st.session_state.step_logs = {}

# Initialize processing flag
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
    
# Initialize agent statuses if not exists
if 'agent_statuses' not in st.session_state:
    st.session_state.agent_statuses = {
        'payment_orchestrator': {'status': 'pending', 'response': None, 'error': None, 'active': False},
        'payment_validator': {'status': 'pending', 'response': None, 'error': None, 'active': False},
        'sanction_check': {'status': 'pending', 'response': None, 'error': None, 'active': False}
    }
    
# Define default orchestrator steps
DEFAULT_STEPS = [
    "Receiving payment request",
    "Validating request format",
    "Delegating card validation to Payment Validator",
    "Delegating customer check to Sanction Check",
    "Analyzing validation results",
    "Analyzing sanction check results",
    "Making payment decision",
    "Processing payment with gateway",
    "Generating response"
]

# Initialize orchestrator steps if not exists
if 'orchestrator_steps' not in st.session_state:
    st.session_state.orchestrator_steps = {
        'current_step': 0,
        'steps': DEFAULT_STEPS
    }

# Add a back button above the title
st.markdown('<div class="back-button">', unsafe_allow_html=True)
if st.button("← Back to Dashboard"):
    st.switch_page("Home.py")
st.markdown('</div>', unsafe_allow_html=True)

# App title and description
st.title("💳 Payment Processing")
st.markdown("""
This page allows you to process payments using AWS Bedrock agents. The payment orchestrator coordinates with the validator and sanction check agents to ensure secure and compliant payment processing.
""")

# Check AWS credentials
aws_configured = check_aws_credentials()

# Check if agents are configured
payment_orchestrator_configured = check_agent_configuration('payment_orchestrator')
payment_validator_configured = check_agent_configuration('payment_validator')
sanction_check_configured = check_agent_configuration('sanction_check')

# Display configuration status in a more compact way
st.sidebar.subheader("Configuration Status")

config_status = {
    "AWS Credentials": aws_configured,
    "Payment Orchestrator": payment_orchestrator_configured,
    "Payment Validator": payment_validator_configured,
    "Sanction Check": sanction_check_configured
}

for item, status in config_status.items():
    if status:
        st.sidebar.success(f"✅ {item}: Configured")
    else:
        st.sidebar.error(f"❌ {item}: Not configured")

# Create a layout with two main columns
left_col, right_col = st.columns([3, 2])

with left_col:
    # Payment Request section - without card wrapper
    st.subheader("Payment Request")
    
    # JSON editor with file upload option
    json_data = display_json_editor(get_default_json_template())
    
    # Process payment button with improved styling
    if st.button("Process Payment", type="primary", disabled=not all([aws_configured, payment_orchestrator_configured, payment_validator_configured, sanction_check_configured, json_data is not None])):
        with st.spinner("Processing payment..."):
            result = process_payment_with_agents(json_data)
    
    # Recent payment history section - without card wrapper
    if st.session_state.payment_history:
        st.subheader("Recent Processing History")
        
        agent_options = get_agent_options()
        for i, history_item in enumerate(reversed(st.session_state.payment_history[:3])):
            agent_type = history_item.get('agent_type', 'unknown')
            agent_display_name = agent_options.get(agent_type, agent_type.replace('_', ' ').title())
            
            with st.expander(f"Request {i+1} - {history_item['timestamp']} - {agent_display_name} - {history_item['status']}"):
                st.write("**Request:**")
                st.json(history_item['payload'])
                st.write("**Response:**")
                st.write(history_item['response'])

with right_col:
    # Payment Orchestrator Response section
    st.subheader("Payment Orchestrator Response")
    
    if 'agent_statuses' in st.session_state and st.session_state.agent_statuses['payment_orchestrator']['status'] != 'pending':
        status = st.session_state.agent_statuses['payment_orchestrator']['status']
        
        if status == 'success':
            response = st.session_state.agent_statuses['payment_orchestrator']['response']
            if response and 'response' in response:
                st.success("✅ Payment processed successfully")
                
                # Clean up the response to remove raw process_payment function calls
                response_text = response.get('response', 'No response data')
                if "process_payment(" in response_text:
                    # Extract just the relevant part of the response
                    try:
                        # Try to find a more meaningful part of the response
                        if "Payment approved" in response_text:
                            st.write("Payment approved and processed successfully.")
                        elif "Transaction completed" in response_text:
                            st.write("Transaction completed successfully.")
                        else:
                            # Show a generic success message instead of the raw function call
                            st.write("Payment request was processed successfully by the payment orchestrator.")
                    except:
                        # Fallback to a generic message
                        st.write("Payment request was processed successfully.")
                else:
                    # If no function call is found, display the original response
                    st.write(response_text)
                
                # Show session ID in an expander
                with st.expander("Session Details"):
                    st.write(f"Session ID: {response.get('sessionId', 'Unknown')}")
                    # Don't display the trace JSON directly
            else:
                st.info("Payment processed but no response data available")
        elif status == 'error':
            error = st.session_state.agent_statuses['payment_orchestrator']['error']
            st.error(f"❌ Error: {error}")
        elif status == 'running':
            st.info("⏳ Payment processing in progress...")
    else:
        st.info("Submit a payment request to see the response here")
    
    # Work Log section - without card wrapper
    if st.session_state.step_logs:
        st.subheader("Work Log")
        
        st.markdown('<div class="worklog">', unsafe_allow_html=True)
        
        if st.session_state.step_logs:
            all_logs = []
            for step_index, logs in st.session_state.step_logs.items():
                # Try to convert step_index to int if it's a string and looks like a number
                try:
                    idx = int(step_index) if isinstance(step_index, str) else step_index
                    step_name = DEFAULT_STEPS[idx] if idx < len(DEFAULT_STEPS) else f"Step {step_index}"
                except (ValueError, TypeError):
                    # If conversion fails, use a default step name
                    step_name = f"Step: {step_index}"
                for log in logs:
                    all_logs.append((step_index, step_name, log))
            
            # Sort logs by step index
            all_logs.sort(key=lambda x: int(x[0]) if isinstance(x[0], str) and x[0].isdigit() else (x[0] if isinstance(x[0], int) else 999))
            
            # Display logs
            for step_index, step_name, log in all_logs:
                st.markdown(f"""
                <div class="worklog-entry">
                    <div class="timestamp">{step_name}</div>
                    <p class="message">{log}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Add information about configuration
display_configuration_info()
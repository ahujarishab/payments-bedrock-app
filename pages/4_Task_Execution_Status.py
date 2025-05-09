import streamlit as st
import pandas as pd
import json
import random
from datetime import datetime, timedelta
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
    page_title="Task Execution Status",
    page_icon="🔄",
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

# Initialize task execution session state if not exists
if 'current_task' not in st.session_state:
    st.session_state.current_task = None
if 'task_steps' not in st.session_state:
    st.session_state.task_steps = []
if 'current_step_index' not in st.session_state:
    st.session_state.current_step_index = 0
if 'step_logs' not in st.session_state:
    st.session_state.step_logs = {}
if 'task_started' not in st.session_state:
    st.session_state.task_started = False
if 'task_completed' not in st.session_state:
    st.session_state.task_completed = False
if 'execution_id' not in st.session_state:
    st.session_state.execution_id = None

# Agent options for display
agent_options = get_agent_options()

# Add a back button above the title
st.markdown('<div class="back-button">', unsafe_allow_html=True)
if st.button("← Back to Dashboard"):
    st.switch_page("Home.py")
st.markdown('</div>', unsafe_allow_html=True)

# App title and description
st.title("🔄 Task Execution Status")
st.markdown("""
Monitor the step-by-step execution progress of your AWS Bedrock agent tasks.
""")

# Define sample task steps for different agent types
def get_task_steps(agent_type):
    if agent_type == "payment_orchestrator":
        return [
            "Validating payment request format",
            "Checking merchant credentials",
            "Validating payment card details",
            "Performing fraud check",
            "Checking customer sanctions",
            "Processing payment with gateway",
            "Recording transaction details",
            "Generating payment receipt",
            "Sending confirmation notification"
        ]
    elif agent_type == "payment_validator":
        return [
            "Parsing card details",
            "Validating card number format",
            "Checking card expiration",
            "Validating CVV format",
            "Checking BIN database",
            "Validating currency code",
            "Generating validation report"
        ]
    else:  # sanction_check
        return [
            "Parsing customer information",
            "Checking name against watchlists",
            "Validating address information",
            "Checking country sanctions",
            "Performing PEP screening",
            "Calculating risk score",
            "Generating compliance report"
        ]

# Function to generate sample logs for a step
def generate_step_logs(step_name, agent_type):
    current_time = datetime.now()
    logs = []
    
    # Common log entries
    logs.append(f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] Starting {step_name}")
    
    # Step-specific logs
    if "validating" in step_name.lower() or "checking" in step_name.lower():
        logs.append(f"[{(current_time + timedelta(milliseconds=120)).strftime('%H:%M:%S.%f')[:-3]}] Retrieving validation rules")
        logs.append(f"[{(current_time + timedelta(milliseconds=350)).strftime('%H:%M:%S.%f')[:-3]}] Applying validation checks")
        
        if random.random() > 0.8:  # Occasionally show warnings
            logs.append(f"[{(current_time + timedelta(milliseconds=500)).strftime('%H:%M:%S.%f')[:-3]}] WARNING: Validation taking longer than expected")
            
        logs.append(f"[{(current_time + timedelta(milliseconds=780)).strftime('%H:%M:%S.%f')[:-3]}] Validation completed successfully")
    
    elif "processing" in step_name.lower():
        logs.append(f"[{(current_time + timedelta(milliseconds=100)).strftime('%H:%M:%S.%f')[:-3]}] Connecting to payment gateway")
        logs.append(f"[{(current_time + timedelta(milliseconds=350)).strftime('%H:%M:%S.%f')[:-3]}] Sending payment request")
        logs.append(f"[{(current_time + timedelta(milliseconds=1200)).strftime('%H:%M:%S.%f')[:-3]}] Received gateway response")
        logs.append(f"[{(current_time + timedelta(milliseconds=1300)).strftime('%H:%M:%S.%f')[:-3]}] Processing response")
    
    elif "generating" in step_name.lower():
        logs.append(f"[{(current_time + timedelta(milliseconds=100)).strftime('%H:%M:%S.%f')[:-3]}] Collecting report data")
        logs.append(f"[{(current_time + timedelta(milliseconds=300)).strftime('%H:%M:%S.%f')[:-3]}] Formatting report")
        logs.append(f"[{(current_time + timedelta(milliseconds=450)).strftime('%H:%M:%S.%f')[:-3]}] Report generated successfully")
    
    elif "sending" in step_name.lower():
        logs.append(f"[{(current_time + timedelta(milliseconds=100)).strftime('%H:%M:%S.%f')[:-3]}] Preparing notification")
        logs.append(f"[{(current_time + timedelta(milliseconds=250)).strftime('%H:%M:%S.%f')[:-3]}] Sending to notification service")
        logs.append(f"[{(current_time + timedelta(milliseconds=500)).strftime('%H:%M:%S.%f')[:-3]}] Notification delivered")
    
    # Add agent-specific logs
    if agent_type == "payment_orchestrator" and "processing payment" in step_name.lower():
        logs.append(f"[{(current_time + timedelta(milliseconds=400)).strftime('%H:%M:%S.%f')[:-3]}] Applying payment routing rules")
        logs.append(f"[{(current_time + timedelta(milliseconds=600)).strftime('%H:%M:%S.%f')[:-3]}] Selected optimal payment processor")
    
    elif agent_type == "payment_validator" and "validating card" in step_name.lower():
        logs.append(f"[{(current_time + timedelta(milliseconds=200)).strftime('%H:%M:%S.%f')[:-3]}] Applying Luhn algorithm check")
        logs.append(f"[{(current_time + timedelta(milliseconds=300)).strftime('%H:%M:%S.%f')[:-3]}] Validating card issuer")
    
    elif agent_type == "sanction_check" and "watchlists" in step_name.lower():
        logs.append(f"[{(current_time + timedelta(milliseconds=200)).strftime('%H:%M:%S.%f')[:-3]}] Checking OFAC database")
        logs.append(f"[{(current_time + timedelta(milliseconds=400)).strftime('%H:%M:%S.%f')[:-3]}] Checking EU sanctions list")
        logs.append(f"[{(current_time + timedelta(milliseconds=600)).strftime('%H:%M:%S.%f')[:-3]}] Checking UN sanctions list")
    
    # Common completion log
    logs.append(f"[{(current_time + timedelta(milliseconds=random.randint(800, 1500))).strftime('%H:%M:%S.%f')[:-3]}] Completed {step_name}")
    
    return logs

# Function to simulate task execution
def simulate_task_execution():
    if not st.session_state.task_started:
        return
    
    if st.session_state.current_step_index < len(st.session_state.task_steps):
        current_step = st.session_state.task_steps[st.session_state.current_step_index]
        
        # Generate logs for the current step if not already generated
        if current_step not in st.session_state.step_logs:
            st.session_state.step_logs[current_step] = generate_step_logs(current_step, st.session_state.current_task)
        
        # Simulate step completion after a delay
        if random.random() > 0.7:  # 30% chance to advance to next step on each refresh
            st.session_state.current_step_index += 1
            
            # Check if task is completed
            if st.session_state.current_step_index >= len(st.session_state.task_steps):
                st.session_state.task_completed = True

# Main content area with two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Execution Progress")
    
    # Task selection
    agent_type = st.selectbox(
        "Select Agent Type",
        options=list(agent_options.keys()),
        format_func=lambda x: agent_options[x]
    )
    
    # Start/Reset task button
    col_start, col_reset = st.columns(2)
    
    with col_start:
        if st.button("Start New Execution", disabled=st.session_state.task_started and not st.session_state.task_completed):
            st.session_state.current_task = agent_type
            st.session_state.task_steps = get_task_steps(agent_type)
            st.session_state.current_step_index = 0
            st.session_state.step_logs = {}
            st.session_state.task_started = True
            st.session_state.task_completed = False
            st.session_state.execution_id = f"exec-{agent_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            st.rerun()
    
    with col_reset:
        if st.button("Reset", disabled=not st.session_state.task_started):
            st.session_state.current_task = None
            st.session_state.task_steps = []
            st.session_state.current_step_index = 0
            st.session_state.step_logs = {}
            st.session_state.task_started = False
            st.session_state.task_completed = False
            st.session_state.execution_id = None
            st.rerun()
    
    # Display task information
    if st.session_state.task_started:
        st.write(f"**Execution ID:** {st.session_state.execution_id}")
        st.write(f"**Agent:** {agent_options.get(st.session_state.current_task, st.session_state.current_task)}")
        st.write(f"**Status:** {'Completed' if st.session_state.task_completed else 'In Progress'}")
        
        # Progress bar
        progress = st.session_state.current_step_index / len(st.session_state.task_steps) if st.session_state.task_steps else 0
        st.progress(progress)
        
        # Step list with highlighting
        st.write("**Execution Steps:**")
        for i, step in enumerate(st.session_state.task_steps):
            if i < st.session_state.current_step_index:
                st.success(f"{i+1}. {step} ✓")
            elif i == st.session_state.current_step_index and not st.session_state.task_completed:
                st.info(f"{i+1}. {step} ⟳")
            else:
                st.write(f"{i+1}. {step}")
    else:
        st.info("Select an agent type and click 'Start New Execution' to begin monitoring.")

with col2:
    st.subheader("Step Execution Logs")
    
    if st.session_state.task_started:
        # Simulate task execution
        simulate_task_execution()
        
        if st.session_state.task_completed:
            st.success("Task execution completed successfully!")
        
        # Get current or last step
        current_index = min(st.session_state.current_step_index, len(st.session_state.task_steps) - 1)
        if st.session_state.task_steps:
            current_step = st.session_state.task_steps[current_index]
            
            # Display step information
            st.write(f"**Current Step:** {current_step}")
            
            # Display logs for the current step
            if current_step in st.session_state.step_logs:
                log_container = st.container()
                with log_container:
                    for log in st.session_state.step_logs[current_step]:
                        st.text(log)
            else:
                st.write("Waiting for logs...")
                
            # Auto-refresh for in-progress tasks
            if not st.session_state.task_completed:
                st.empty()
                st.rerun()
    else:
        st.info("Start a task execution to view logs.")

# Add refresh button
if st.button("🔄 Refresh Status"):
    st.rerun()

# Add information about the page
st.markdown("---")
st.info("""
## About This Page

This page simulates the real-time monitoring of agent task execution.
In a production environment, this would connect to:

- CloudWatch Logs for real-time log streaming
- Step Functions for execution tracking
- EventBridge for real-time status updates
""")

# Add configuration information
display_configuration_info()
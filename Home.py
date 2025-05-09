import streamlit as st
from load_dotenv import load_env_file
from aws_client import setup_aws_environment

# Load environment variables from .env file if it exists
load_env_file()

# Set up AWS environment
setup_aws_environment()

# Set page configuration
st.set_page_config(
    page_title="Main Dashboard",
    page_icon="🧭",
    layout="wide"
)

# Hide the default sidebar and style the buttons
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Hide the navigation arrow */
    .e10vaf9m1, .st-emotion-cache-1f3w014, .ex0cdmw0, svg[class*="st-emotion-cache"] {
        display: none !important;
    }
    
    h1, h3 {
        font-family: 'Roboto', sans-serif;
    }
    
    .centered-content {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .description {
        text-align: center;
        margin-top: 10px;
        margin-bottom: 30px;
        color: #555;
        font-size: 16px;
        font-family: 'Roboto', sans-serif;
    }
    
    div.stButton > button {
        height: 100px;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* Button colors */
    .payment-btn button {
        background-color: #1E88E5 !important;
        border-color: #1E88E5 !important;
    }
    
    .history-btn button {
        background-color: #43A047 !important;
        border-color: #43A047 !important;
    }
    
    .status-btn button {
        background-color: #FB8C00 !important;
        border-color: #FB8C00 !important;
    }
    
    .task-btn button {
        background-color: #8E24AA !important;
        border-color: #8E24AA !important;
    }
    
    /* Hover effects */
    .payment-btn button:hover {
        background-color: #1565C0 !important;
        border-color: #1565C0 !important;
    }
    
    .history-btn button:hover {
        background-color: #2E7D32 !important;
        border-color: #2E7D32 !important;
    }
    
    .status-btn button:hover {
        background-color: #EF6C00 !important;
        border-color: #EF6C00 !important;
    }
    
    .task-btn button:hover {
        background-color: #6A1B9A !important;
        border-color: #6A1B9A !important;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("🧭 Main Dashboard")
st.markdown("""
Use this dashboard to navigate to different sections of the application.
""")

# Create a centered container for the buttons
st.markdown('<div class="centered-content">', unsafe_allow_html=True)

# First row
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="payment-btn">', unsafe_allow_html=True)
    payment_btn = st.button("💳  Payment Processing", use_container_width=True, key="payment_btn")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="description">Process payments using AWS Bedrock agents. Upload JSON payloads and invoke different agent types.</div>', unsafe_allow_html=True)
    if payment_btn:
        st.switch_page("pages/1_Payment_Processing.py")

with col2:
    st.markdown('<div class="history-btn">', unsafe_allow_html=True)
    history_btn = st.button("📜  Agent Execution History", use_container_width=True, key="history_btn")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="description">View the history of agent executions. Filter by agent type and status.</div>', unsafe_allow_html=True)
    if history_btn:
        st.switch_page("pages/2_Agent_Execution_History.py")

# Second row
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="status-btn">', unsafe_allow_html=True)
    status_btn = st.button("📊  Agent Status Dashboard", use_container_width=True, key="status_btn")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="description">Monitor the status and health of your AWS Bedrock agents. View metrics and test agents.</div>', unsafe_allow_html=True)
    if status_btn:
        st.switch_page("pages/3_Agent_Status.py")

with col4:
    st.markdown('<div class="task-btn">', unsafe_allow_html=True)
    task_btn = st.button("🔄  Task Execution Status", use_container_width=True, key="task_btn")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="description">Monitor the step-by-step execution progress of your AWS Bedrock agent tasks.</div>', unsafe_allow_html=True)
    if task_btn:
        st.switch_page("pages/4_Task_Execution_Status.py")

# Close the centered container
st.markdown('</div>', unsafe_allow_html=True)

# Add information about the application
st.markdown("### About This Application")
st.markdown("""
This application demonstrates the use of AWS Bedrock agents for payment processing and validation.
It provides a user interface for invoking agents, monitoring their status, and viewing execution history.

**Key Features:**
- Process payments using different agent types
- Monitor agent status and health
- View execution history and logs
- Track task execution progress in real-time
""")
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

# Hide the sidebar and adjust spacing
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Hide the navigation arrow */
    .e10vaf9m1, .st-emotion-cache-1f3w014, .ex0cdmw0, svg[class*="st-emotion-cache"] {
        display: none !important;
    }
    
    /* Reduce top padding */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Reduce space around title */
    h1 {
        margin-top: 0 !important;
        padding-top: 0 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Target button text specifically */
    div.stButton button p {
        color: black !important;
    }
    
    /* Reduce space between elements */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown("<h1>🧭 Main Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='margin-bottom:0.5rem;'>Use this dashboard to navigate to different sections of the application.</p>", unsafe_allow_html=True)

# Create a centered container for the buttons
col1, col2 = st.columns(2)

with col1:
    # Light blue button - direct styling
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background-color: #90CAF9;
        border-color: #90CAF9;
        height: 100px;
        font-size: 24px;
        font-weight: bold;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)
    payment_btn = st.button("💳  Payment Processing", use_container_width=True, key="payment_btn")
    st.markdown('<div style="text-align:center; margin-bottom:15px;">Process payments using AWS Bedrock agents. Upload JSON payloads and invoke different agent types.</div>', unsafe_allow_html=True)
    if payment_btn:
        st.switch_page("pages/1_Payment_Processing.py")

with col2:
    # Light green button - direct styling
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background-color: #A5D6A7;
        border-color: #A5D6A7;
        height: 100px;
        font-size: 24px;
        font-weight: bold;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)
    history_btn = st.button("📜  Agent Execution History", use_container_width=True, key="history_btn")
    st.markdown('<div style="text-align:center; margin-bottom:15px;">View the history of agent executions. Filter by agent type and status.</div>', unsafe_allow_html=True)
    if history_btn:
        st.switch_page("pages/2_Agent_Execution_History.py")

# Second row
col3, col4 = st.columns(2)

with col3:
    # Light orange button - direct styling
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(1) button {
        background-color: #FFCC80;
        border-color: #FFCC80;
        height: 100px;
        font-size: 24px;
        font-weight: bold;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)
    status_btn = st.button("📊  Agent Status Dashboard", use_container_width=True, key="status_btn")
    st.markdown('<div style="text-align:center; margin-bottom:15px;">Monitor the status and health of your AWS Bedrock agents. View metrics and test agents.</div>', unsafe_allow_html=True)
    if status_btn:
        st.switch_page("pages/3_Agent_Status.py")

with col4:
    # Light purple button - direct styling
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(2) button {
        background-color: #CE93D8;
        border-color: #CE93D8;
        height: 100px;
        font-size: 24px;
        font-weight: bold;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)
    task_btn = st.button("🔄  Task Execution Status", use_container_width=True, key="task_btn")
    st.markdown('<div style="text-align:center; margin-bottom:15px;">Monitor the step-by-step execution progress of your AWS Bedrock agent tasks.</div>', unsafe_allow_html=True)
    if task_btn:
        st.switch_page("pages/4_Task_Execution_Status.py")

# Third row
col5, col6 = st.columns(2)

with col5:
    # Light teal button - direct styling
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"]:nth-of-type(3) > div:nth-child(1) button {
        background-color: #80CBC4;
        border-color: #80CBC4;
        height: 100px;
        font-size: 24px;
        font-weight: bold;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)
    spa_btn = st.button("📄  SPA Processing", use_container_width=True, key="spa_btn")
    st.markdown('<div style="text-align:center; margin-bottom:15px;">Process structured product agreements (SPA) stored in S3 buckets using AWS Bedrock agents.</div>', unsafe_allow_html=True)
    if spa_btn:
        st.switch_page("pages/5_SPA_Processing.py")

# Add information about the application in a compact format
st.markdown("<h3 style='margin-top:0.5rem; margin-bottom:0.5rem;'>About This Application</h3>", unsafe_allow_html=True)
st.markdown("""
<p style='margin-bottom:0.5rem;'>This application demonstrates the use of AWS Bedrock agents for payment processing, document processing, and validation.</p>
<ul style='margin-top:0; padding-left:20px;'>
<li>Process payments using different agent types</li>
<li>Process structured product agreements (SPA) from S3 buckets</li>
<li>Monitor agent status and health</li>
<li>View execution history and logs</li>
<li>Track task execution progress in real-time</li>
</ul>
""", unsafe_allow_html=True)
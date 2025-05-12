import streamlit as st
import json
import time
from load_dotenv import load_env_file
from aws_client import setup_aws_environment, check_aws_credentials
from spa_processing import orchestrate_structured_product_agreement
from ui_components import display_configuration_info
from session_state import initialize_session_state

# Load environment variables from .env file if it exists
load_env_file()

# Set up AWS environment
aws_creds = setup_aws_environment()

# Set page configuration
st.set_page_config(
    page_title="SPA Processing",
    page_icon="📄",
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
    
    .agent-status {
        margin-top: 10px;
        padding: 10px;
        border-radius: 5px;
    }
    
    .agent-status.pending {
        background-color: #f8f9fa;
        border-left: 5px solid #6c757d;
    }
    
    .agent-status.running {
        background-color: #e8f4fd;
        border-left: 5px solid #0d6efd;
    }
    
    .agent-status.success {
        background-color: #d1e7dd;
        border-left: 5px solid #198754;
    }
    
    .agent-status.error {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
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
st.title("📄 Structured Product Agreement Processing")
st.markdown("""
Process structured product agreements (SPA) stored in S3 buckets using AWS Bedrock agents.
""")

# Create two columns for the main layout
left_col, right_col = st.columns([1, 1])

# Left column: Form for SPA processing
with left_col:
    st.subheader("SPA Document Details")
    
    # Form for SPA processing
    with st.form("spa_processing_form"):
        s3_bucket_path = st.text_input(
            "S3 Bucket Path", 
            value="s3://spa-client-docs/SPA-docs/SPI-001/GUARANTEED-RETURN-STRUCTURED-PRODUCT-AGREEMENT-2-en.pdf",
            help="The S3 bucket path where the document is stored"
        )
        
        investor_id = st.text_input(
            "Investor ID", 
            value="I70897",
            help="The investor ID associated with the document"
        )
        
        document_type = st.selectbox(
            "Document Type",
            options=["spa", "term_sheet", "prospectus", "other"],
            index=0,
            help="The type of document to process"
        )
        
        collaborator_agent = st.text_input(
            "Collaborator Agent",
            value="spap-collaborator-agent",
            help="The collaborator agent to work with"
        )
        
        # Check if AWS credentials and agents are configured
        aws_creds_configured = check_aws_credentials()
        
        # Submit button
        submit_button = st.form_submit_button("Process Document", type="primary")
    
    # Display requirements for invocation
    if not aws_creds_configured:
        st.warning("⚠️ AWS credentials not configured. Please set your AWS credentials in the .env file.")

# Right column: Processing status and results
with right_col:
    st.subheader("Processing Status")
    
    # Initialize status placeholder
    status_placeholder = st.empty()
    
    # Display initial status
    status_placeholder.markdown('<div class="agent-status pending">Waiting for document submission...</div>', unsafe_allow_html=True)
    
    # Results placeholder
    results_placeholder = st.empty()

# Process the document when the form is submitted
if submit_button:
    # Update status
    status_placeholder.markdown('<div class="agent-status running">Processing document...</div>', unsafe_allow_html=True)
    
    # Process the document
    with st.spinner("Processing structured product agreement..."):
        try:
            result = orchestrate_structured_product_agreement(
                s3_bucket_path=s3_bucket_path,
                investor_id=investor_id,
                document_type=document_type,
                collaborator_agent=collaborator_agent
            )
            
            # Store the result in session state
            st.session_state.spa_result = result
            
            # Update status based on result
            if 'error' in result:
                status_placeholder.markdown('<div class="agent-status error">Error processing document</div>', unsafe_allow_html=True)
                results_placeholder.error(result['error'])
            else:
                status_placeholder.markdown('<div class="agent-status success">Document processed successfully</div>', unsafe_allow_html=True)
                
                # Display results
                results_placeholder.subheader("Processing Results")
                results_placeholder.write("**Response:**")
                results_placeholder.write(result.get('response', 'No response'))
                
                with results_placeholder.expander("Session Details"):
                    results_placeholder.write(f"Session ID: {result.get('sessionId', 'Unknown')}")
                    if 'trace' in result:
                        results_placeholder.json(result['trace'])
        except Exception as e:
            status_placeholder.markdown('<div class="agent-status error">Error processing document</div>', unsafe_allow_html=True)
            results_placeholder.error(f"An error occurred: {str(e)}")

# Add information about configuration
display_configuration_info()
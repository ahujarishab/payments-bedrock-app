import streamlit as st
import pandas as pd
import json
from datetime import datetime
from botocore.exceptions import ClientError
from load_dotenv import load_env_file
from aws_client import setup_aws_environment, get_bedrock_agent_client
from agent_utils import get_agent_options, get_agent_credentials_for_type, invoke_agent
from ui_components import display_configuration_info
from session_state import initialize_session_state

# Load environment variables from .env file if it exists
load_env_file()

# Set up AWS environment
aws_creds = setup_aws_environment()

# Set page configuration
st.set_page_config(
    page_title="Agent Status Dashboard",
    page_icon="📊",
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

# Function to get agent details
def get_agent_details(agent_id, region=None):
    """
    Get details about a Bedrock agent
    """
    try:
        # Initialize Bedrock agent client
        bedrock_client = get_bedrock_agent_client(region)
        
        # Get agent details
        response = bedrock_client.get_agent(
            agentId=agent_id
        )
        
        return response
    except ClientError as e:
        st.error(f"Error getting agent details: {str(e)}")
        return {'error': f"Error getting agent details: {str(e)}"}
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return {'error': f"Unexpected error: {str(e)}"}

# Function to get agent alias details
def get_agent_alias(agent_id, agent_alias_id, region=None):
    """
    Get details about a Bedrock agent alias
    """
    try:
        # Initialize Bedrock agent client
        bedrock_client = get_bedrock_agent_client(region)
        
        # Get agent alias details
        response = bedrock_client.get_agent_alias(
            agentId=agent_id,
            agentAliasId=agent_alias_id
        )
        
        return response
    except ClientError as e:
        st.error(f"Error getting agent alias details: {str(e)}")
        return {'error': f"Error getting agent alias details: {str(e)}"}
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return {'error': f"Unexpected error: {str(e)}"}

# Function to get agent status
def get_agent_status(agent_id, agent_alias_id, region=None):
    """
    Get the status of a Bedrock agent
    """
    try:
        # Get agent details
        agent_details = get_agent_details(agent_id, region)
        
        if 'error' in agent_details:
            return {'status': 'Unknown', 'message': agent_details['error']}
        
        # Get agent alias details
        alias_details = get_agent_alias(agent_id, agent_alias_id, region)
        
        if 'error' in alias_details:
            return {'status': 'Unknown', 'message': alias_details['error']}
        
        # Determine status based on agent and alias details
        status = 'Active'
        if agent_details.get('agentStatus') != 'READY':
            status = 'Not Ready'
        
        # Format the last updated time
        last_updated = alias_details.get('lastUpdatedAt', 'Unknown')
        if isinstance(last_updated, datetime):
            last_updated = last_updated.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            'status': status,
            'agentName': agent_details.get('agentName', 'Unknown'),
            'aliasName': alias_details.get('agentAliasName', 'Unknown'),
            'lastModified': last_updated,
            'model': agent_details.get('foundationModel', 'Unknown'),
            'description': agent_details.get('description', 'No description available')
        }
    except Exception as e:
        st.error(f"Error getting agent status: {str(e)}")
        return {'status': 'Error', 'message': str(e)}

# Function to simulate agent workload
def get_agent_workload(agent_type):
    """
    Simulate workload metrics for an agent
    """
    # In a real implementation, you would get this data from CloudWatch metrics
    # or another monitoring system
    
    # Generate some random workload data for demonstration
    import random
    
    current_time = datetime.now()
    
    # Generate data points for the last 24 hours (hourly)
    timestamps = [(current_time - pd.Timedelta(hours=i)).strftime("%Y-%m-%d %H:00") for i in range(24, 0, -1)]
    
    if agent_type == "payment_orchestrator":
        # Payment orchestrator tends to have higher workload
        requests = [random.randint(15, 60) for _ in range(24)]
        latency = [random.randint(300, 1000) for _ in range(24)]
        errors = [random.randint(0, 4) for _ in range(24)]
    elif agent_type == "payment_validator":
        # Payment validator tends to have moderate workload
        requests = [random.randint(10, 50) for _ in range(24)]
        latency = [random.randint(200, 800) for _ in range(24)]
        errors = [random.randint(0, 3) for _ in range(24)]
    else:  # sanction_check
        # Sanction check tends to have lower workload
        requests = [random.randint(5, 30) for _ in range(24)]
        latency = [random.randint(300, 1000) for _ in range(24)]
        errors = [random.randint(0, 2) for _ in range(24)]
    
    return {
        'timestamps': timestamps,
        'requests': requests,
        'latency': latency,
        'errors': errors,
        'total_requests': sum(requests),
        'avg_latency': sum(latency) / len(latency),
        'total_errors': sum(errors),
        'success_rate': 100 - (sum(errors) / sum(requests) * 100) if sum(requests) > 0 else 100
    }

# Add a back button above the title
st.markdown('<div class="back-button">', unsafe_allow_html=True)
if st.button("← Back to Dashboard"):
    st.switch_page("Home.py")
st.markdown('</div>', unsafe_allow_html=True)

# App title and description
st.title("📊 Agent Status Dashboard")
st.markdown("""
Monitor the status and workload of your AWS Bedrock agents.
""")

# Refresh button
if st.button("🔄 Refresh Agent Status"):
    st.rerun()

# Create tabs for each agent
tabs = st.tabs([agent_options[agent_type] for agent_type in agent_options])

# Process each agent in its own tab
for i, agent_type in enumerate(agent_options):
    with tabs[i]:
        agent_name = agent_options[agent_type]
        agent_creds = get_agent_credentials_for_type(agent_type)
        agent_id = agent_creds['agent_id']
        agent_alias_id = agent_creds['agent_alias_id']
        
        if not agent_id or not agent_alias_id:
            st.info(f"{agent_name} agent not configured. Please set the agent ID and alias ID in your .env file.")
        else:
            # Show loading spinner while fetching agent status
            with st.spinner(f"Fetching {agent_name} status..."):
                # Get agent status
                status = get_agent_status(agent_id, agent_alias_id, aws_creds['aws_region'])
            
            # Create two columns for status and workload
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Agent Status")
                
                # Display status
                if status.get('status') == 'Active':
                    st.success(f"Status: {status.get('status')}")
                elif status.get('status') == 'Not Ready':
                    st.warning(f"Status: {status.get('status')}")
                else:
                    st.error(f"Status: {status.get('status')}")
                
                # Display agent details
                st.write(f"Agent Name: {status.get('agentName', 'Unknown')}")
                st.write(f"Alias Name: {status.get('aliasName', 'Unknown')}")
                st.write(f"Foundation Model: {status.get('model', 'Unknown')}")
                st.write(f"Last Modified: {status.get('lastModified', 'Unknown')}")
                
                if status.get('description'):
                    with st.expander("Description"):
                        st.write(status.get('description'))
            
            with col2:
                st.subheader("Agent Health")
                
                # Get workload metrics
                workload = get_agent_workload(agent_type)
                
                # Create three columns for metrics
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    st.metric("Total Requests (24h)", f"{workload['total_requests']}")
                
                with metric_col2:
                    st.metric("Avg. Latency (ms)", f"{int(workload['avg_latency'])}")
                
                with metric_col3:
                    st.metric("Success Rate", f"{workload['success_rate']:.1f}%")
            
            # Display workload chart
            st.subheader("Request Volume (24h)")
            
            # Create a DataFrame for the chart
            chart_data = pd.DataFrame({
                'Time': workload['timestamps'],
                'Requests': workload['requests'],
                'Errors': workload['errors']
            })
            
            # Display the chart
            st.line_chart(chart_data.set_index('Time')[['Requests', 'Errors']])
            
            # Add a test button to invoke the agent
            st.subheader("Test Agent")
            
            # Default test payload based on agent type
            if agent_type == "payment_orchestrator":
                test_payload = {
                    "header": {
                        "MerchantID": "Mrt1234567890",   
                        "OrderNumber": "TEST" + datetime.now().strftime("%H%M%S"),
                        "LocalDateTime": datetime.now().strftime("%y%m%d%H%M%S"),
                        "TransactionID": "TEST" + datetime.now().strftime("%H%M%S"),
                        "TerminalID": "20",
                        "SettleIndicator": "true",
                        "UniqueRequestNumber": "TEST" + datetime.now().strftime("%H%M%S")
                    },
                    "request": {
                        "RequestType": "Sale",
                        "InputType": "Keyed",
                        "DeviceType": "I" 
                    },                
                    "PaymentDetails": {
                        "PaymentType": "Credit",           
                        "Media": "MC"     
                    },
                    "CardDetails": {
                        "AccountType": "PAN",
                        "AccountNumber": "6006199750003330026",
                        "CardVerificationValue": "356",
                        "Expiration": "04/29",
                        "Amount": "12.00",
                        "CurrencyCode": "678" 
                    },
                    "CustomerDetails": {
                        "CustomerName": "John Doe",
                        "CustomerID": "12345678901",
                        "EmailID": "john.doe@example.com",
                        "AddressVerification": {
                            "Address1": "4011, Stary Cir Dr",
                            "Address2": "Travis",
                            "City": "Austin",
                            "CountryCode": "US",
                            "State": "Texas",
                            "Postalcode": "1234-78730"
                        }
                    }
                }
            elif agent_type == "payment_validator":
                test_payload = {
                    "CardDetails": {
                        "AccountType": "PAN",
                        "AccountNumber": "6006199750003330026",
                        "CardVerificationValue": "356",
                        "Expiration": "04/29",
                        "Amount": "12.00",
                        "CurrencyCode": "678" 
                    }
                }
            else:  # sanction_check
                test_payload = {
                    "CustomerDetails": {
                        "CustomerName": "John Doe",
                        "CustomerID": "12345678901",
                        "EmailID": "john.doe@example.com",
                        "AddressVerification": {
                            "Address1": "4011, Stary Cir Dr",
                            "Address2": "Travis",
                            "City": "Austin",
                            "CountryCode": "US",
                            "State": "Texas",
                            "Postalcode": "1234-78730"
                        }
                    }
                }
            
            # Allow editing the test payload
            with st.expander("Edit Test Payload"):
                test_json = st.text_area(
                    "JSON Payload", 
                    value=json.dumps(test_payload, indent=2),
                    height=300,
                    key=f"test_json_{agent_type}"
                )
                
                try:
                    test_payload = json.loads(test_json)
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON format: {str(e)}")
                    test_payload = None
            
            if st.button(f"Test {agent_name}", key=f"test_button_{agent_type}"):
                if test_payload:
                    with st.spinner(f"Testing {agent_name}..."):
                        result = invoke_agent(agent_type, test_payload, aws_creds['aws_region'])
                        
                        if 'error' in result:
                            st.error(result['error'])
                        else:
                            st.success("Test completed successfully!")
                            st.subheader("Response")
                            st.write(result['response'])
                            
                            with st.expander("Session Details"):
                                st.write(f"Session ID: {result.get('sessionId', 'Unknown')}")
                                if 'trace' in result:
                                    st.json(result['trace'])
                else:
                    st.error("Invalid test payload. Please fix the JSON format.")

# Add information about permissions
display_configuration_info()
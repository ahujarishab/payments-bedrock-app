import json
import streamlit as st
from datetime import datetime
from botocore.exceptions import ClientError
from load_dotenv import get_agent_credentials
from aws_client import get_bedrock_agent_runtime_client

def get_agent_options():
    """
    Get the standard agent options dictionary
    """
    return {
        "payment_orchestrator": "Payment Orchestrator",
        "payment_validator": "Payment Validator",
        "sanction_check": "Sanction Check"
    }

def check_agent_configuration(agent_type):
    """
    Check if an agent is properly configured
    """
    agent_creds = get_agent_credentials()
    agent_id = agent_creds[f'{agent_type}_agent_id']
    agent_alias_id = agent_creds[f'{agent_type}_agent_alias_id']
    
    return bool(agent_id and agent_alias_id)

def get_agent_credentials_for_type(agent_type):
    """
    Get agent ID and alias ID for a specific agent type
    """
    agent_creds = get_agent_credentials()
    return {
        'agent_id': agent_creds[f'{agent_type}_agent_id'],
        'agent_alias_id': agent_creds[f'{agent_type}_agent_alias_id']
    }

def invoke_agent(agent_type, json_payload, region=None):
    """
    Invoke a Bedrock agent with the provided JSON payload
    """
    try:
        # Initialize Bedrock Agent Runtime client
        bedrock_agent_runtime = get_bedrock_agent_runtime_client(region)
        
        # Get agent credentials
        agent_creds = get_agent_credentials_for_type(agent_type)
        agent_id = agent_creds['agent_id']
        agent_alias_id = agent_creds['agent_alias_id']
        
        # Check if agent credentials are configured
        if not agent_id or not agent_alias_id:
            return {'error': f"{agent_type.replace('_', ' ').title()} agent not configured. Please set the agent ID and alias ID in your .env file."}
        
        # Create a session ID
        session_id = f"{agent_type}-{str(hash(json.dumps(json_payload)))}"
        
        # Invoke the agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
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
        
        # Store in history
        add_to_payment_history(agent_type, json_payload, completion, 'Success', session_id)
        
        return {
            'response': completion,
            'trace': response.get('trace', {}),
            'sessionId': session_id
        }
    except ClientError as e:
        error_msg = f"Error invoking {agent_type.replace('_', ' ').title()} agent: {str(e)}"
        
        # Store error in history
        add_to_payment_history(agent_type, json_payload, error_msg, 'Failed', 
                              f"{agent_type}-error-{datetime.now().strftime('%H%M%S')}")
        
        return {'error': error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        return {'error': error_msg}

def add_to_payment_history(agent_type, payload, response, status, session_id):
    """
    Add an entry to the payment history in session state
    """
    # Initialize payment history if it doesn't exist
    if 'payment_history' not in st.session_state:
        st.session_state.payment_history = []
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_item = {
        'timestamp': timestamp,
        'agent_type': agent_type,
        'payload': payload,
        'response': response,
        'status': status,
        'sessionId': session_id
    }
    
    st.session_state.payment_history.append(history_item)
    
    # Keep only the last 10 entries
    if len(st.session_state.payment_history) > 10:
        st.session_state.payment_history = st.session_state.payment_history[-10:]
import json
import streamlit as st
from datetime import datetime
from botocore.exceptions import ClientError
from load_dotenv import get_agent_credentials
from aws_client import get_bedrock_agent_runtime_client
from agent_utils import add_to_payment_history

def orchestrate_structured_product_agreement(s3_bucket_path, investor_id, document_type="spa", collaborator_agent="spap-collaborator-agent"):
    """
    Orchestrate the processing of a structured product agreement document.
    
    Args:
        s3_bucket_path (str): The S3 bucket path where the document is stored
        investor_id (str): The investor ID associated with the document
        document_type (str, optional): The type of document. Defaults to "spa".
        collaborator_agent (str, optional): The collaborator agent to work with. Defaults to "spap-collaborator-agent".
    
    Returns:
        dict: The processing result
    """
    try:
        # Initialize Bedrock Agent Runtime client
        bedrock_agent_runtime = get_bedrock_agent_runtime_client()
        
        # Create payload for processing
        payload = {
            "documentDetails": {
                "s3BucketPath": s3_bucket_path,
                "investorId": investor_id,
                "documentType": document_type
            },
            "processingDetails": {
                "collaboratorAgent": collaborator_agent,
                "requestTimestamp": datetime.now().isoformat()
            }
        }
        
        # Get agent credentials for payment orchestrator (we'll use this as the main agent)
        agent_creds = get_agent_credentials()
        agent_id = agent_creds['payment_orchestrator_agent_id']
        agent_alias_id = agent_creds['payment_orchestrator_agent_alias_id']
        
        # Check if agent credentials are configured
        if not agent_id or not agent_alias_id:
            return {'error': "Payment orchestrator agent not configured. Please set the agent ID and alias ID in your .env file."}
        
        # Create a session ID
        session_id = f"spa-processing-{investor_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Invoke the agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=json.dumps(payload),
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
        add_to_payment_history("spa_processing", payload, completion, 'Success', session_id)
        
        return {
            'response': completion,
            'trace': response.get('trace', {}),
            'sessionId': session_id
        }
    except ClientError as e:
        error_msg = f"Error invoking SPA processing agent: {str(e)}"
        
        # Store error in history
        add_to_payment_history("spa_processing", payload, error_msg, 'Failed', 
                              f"spa-processing-error-{datetime.now().strftime('%H%M%S')}")
        
        return {'error': error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        return {'error': error_msg}
import os
import boto3
from botocore.exceptions import ClientError

def setup_aws_environment():
    """
    Set up AWS environment variables and return AWS credentials
    """
    # Get AWS credentials from environment variables
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_session_token = os.environ.get('AWS_SESSION_TOKEN')
    aws_region = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Return AWS credentials
    return {
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key,
        'aws_session_token': aws_session_token,
        'aws_region': aws_region
    }

def check_aws_credentials():
    """
    Check if AWS credentials are configured
    """
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    return aws_access_key_id is not None and aws_secret_access_key is not None

def get_bedrock_client(region=None):
    """
    Get a boto3 client for Amazon Bedrock
    """
    if region is None:
        region = os.environ.get('AWS_REGION', 'us-east-1')
    
    try:
        # Create a boto3 session
        session = boto3.Session(
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.environ.get('AWS_SESSION_TOKEN'),
            region_name=region
        )
        
        # Create a bedrock-agent-runtime client
        bedrock_client = session.client(service_name='bedrock-agent-runtime')
        
        return bedrock_client
    except Exception as e:
        print(f"Error creating Bedrock client: {str(e)}")
        raise e

def get_bedrock_agent_client(region=None):
    """
    Get a boto3 client for Amazon Bedrock Agent
    """
    if region is None:
        region = os.environ.get('AWS_REGION', 'us-east-1')
    
    try:
        # Create a boto3 session
        session = boto3.Session(
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.environ.get('AWS_SESSION_TOKEN'),
            region_name=region
        )
        
        # Create a bedrock-agent client
        bedrock_client = session.client(service_name='bedrock-agent')
        
        return bedrock_client
    except Exception as e:
        print(f"Error creating Bedrock Agent client: {str(e)}")
        raise e

def get_bedrock_agent_runtime_client(region=None):
    """
    Get a boto3 client for Amazon Bedrock Agent Runtime
    """
    if region is None:
        region = os.environ.get('AWS_REGION', 'us-east-1')
    
    try:
        # Create a boto3 session
        session = boto3.Session(
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.environ.get('AWS_SESSION_TOKEN'),
            region_name=region
        )
        
        # Create a bedrock-agent-runtime client
        bedrock_client = session.client(service_name='bedrock-agent-runtime')
        
        return bedrock_client
    except Exception as e:
        print(f"Error creating Bedrock Agent Runtime client: {str(e)}")
        raise e
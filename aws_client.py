import boto3
import os
from botocore.exceptions import ClientError
from load_dotenv import get_aws_credentials

def get_bedrock_agent_runtime_client(region=None):
    """
    Get a configured Bedrock Agent Runtime client
    """
    aws_creds = get_aws_credentials()
    region_name = region if region else aws_creds.get('aws_region', 'us-east-1')
    
    return boto3.client(
        'bedrock-agent-runtime',
        region_name=region_name
    )

def get_bedrock_client(region=None):
    """
    Get a configured Bedrock client
    """
    aws_creds = get_aws_credentials()
    region_name = region if region else aws_creds.get('aws_region', 'us-east-1')
    
    return boto3.client(
        'bedrock',
        region_name=region_name
    )

def check_aws_credentials():
    """
    Check if AWS credentials are properly configured
    """
    return bool(os.environ.get('AWS_ACCESS_KEY_ID') or boto3.Session().get_credentials())

def setup_aws_environment():
    """
    Set up AWS environment variables from credentials
    """
    aws_creds = get_aws_credentials()
    
    os.environ['AWS_ACCESS_KEY_ID'] = aws_creds['aws_access_key_id']
    os.environ['AWS_SECRET_ACCESS_KEY'] = aws_creds['aws_secret_access_key']
    if aws_creds['aws_session_token']:
        os.environ['AWS_SESSION_TOKEN'] = aws_creds['aws_session_token']
    os.environ['AWS_DEFAULT_REGION'] = aws_creds['aws_region']
    
    return aws_creds
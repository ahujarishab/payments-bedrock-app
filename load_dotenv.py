import os
from pathlib import Path

def load_env_file(env_file='.env'):
    """
    Load environment variables from a .env file
    """
    try:
        env_path = Path(env_file)
        if env_path.exists():
            print(f"Loading environment variables from {env_file}")
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key-value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        
                        # Set environment variable if not already set
                        if key and value:
                            os.environ[key] = value
            return True
        else:
            print(f"Environment file {env_file} not found")
            return False
    except Exception as e:
        print(f"Error loading environment file: {str(e)}")
        return False

def get_env_var(var_name, default=None):
    """
    Get an environment variable, with a default value if not found
    """
    return os.environ.get(var_name, default)

def get_aws_credentials():
    """
    Get AWS credentials from environment variables
    """
    return {
        'aws_access_key_id': get_env_var('AWS_ACCESS_KEY_ID', ''),
        'aws_secret_access_key': get_env_var('AWS_SECRET_ACCESS_KEY', ''),
        'aws_session_token': get_env_var('AWS_SESSION_TOKEN', ''),
        'aws_region': get_env_var('AWS_DEFAULT_REGION', 'us-east-1')
    }

def get_agent_credentials():
    """
    Get agent credentials from environment variables for all agents
    """
    return {
        'payment_orchestrator_agent_id': get_env_var('PAYMENT_ORCHESTRATOR_AGENT_ID', ''),
        'payment_orchestrator_agent_alias_id': get_env_var('PAYMENT_ORCHESTRATOR_AGENT_ALIAS_ID', ''),
        'payment_validator_agent_id': get_env_var('PAYMENT_VALIDATOR_AGENT_ID', ''),
        'payment_validator_agent_alias_id': get_env_var('PAYMENT_VALIDATOR_AGENT_ALIAS_ID', ''),
        'sanction_check_agent_id': get_env_var('SANCTION_CHECK_AGENT_ID', ''),
        'sanction_check_agent_alias_id': get_env_var('SANCTION_CHECK_AGENT_ALIAS_ID', '')
    }

if __name__ == "__main__":
    load_env_file()
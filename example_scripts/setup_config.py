import os
from dotenv import load_dotenv
from utils import _set_paths
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager

# Load environment variables from .env file
load_dotenv()

# Set up paths (if needed)
_set_paths()

# Fetch environment variables
arbitrum_rpc = os.getenv('ARBITRUM_RPC')
avalanche_rpc = os.getenv('AVAX_RPC')
private_key = os.getenv('PRIVATE_KEY')
user_wallet_address = os.getenv('USER_WALLET_ADDRESS')

# Create config dictionary
config = {
    'rpcs': {
        'arbitrum': arbitrum_rpc,
        'avalanche': avalanche_rpc
    },
    'chain_ids': {
        'arbitrum': 42161,
        'avalanche': 43114
    },
    'private_key': private_key,
    'user_wallet_address': user_wallet_address
}

# Save config to a file (optional)
config_file = 'config.yaml'
with open(config_file, 'w') as file:
    import yaml
    yaml.dump(config, file, default_flow_style=False)

# Initialize the ConfigManager for Arbitrum
arbitrum_config_object = ConfigManager(chain='arbitrum')

# Set the config object attributes from the config file
arbitrum_config_object.set_config(filepath=config_file)

# Optionally, overwrite object attributes
arbitrum_config_object.set_rpc(arbitrum_rpc)
print(arbitrum_config_object.rpc)
print(arbitrum_config_object.private_key)
print(arbitrum_config_object.user_wallet_address)

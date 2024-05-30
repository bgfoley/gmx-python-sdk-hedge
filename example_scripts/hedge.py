# create_increase_order.py
from utils import _set_paths
_set_paths()

from gmx_python_sdk.scripts.v2.order.order_argument_parser import OrderArgumentParser
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager
from price_utils import fetch_eth_price, calculate_size_delta

# Initialize configuration
chain = 'arbitrum'
arbitrum_config_object = ConfigManager(chain=chain)
arbitrum_config_object.set_config()

# Define initial collateral delta in ETH
initial_collateral_delta_eth = 1.0  # Replace this with your actual value

# Fetch ETH price
eth_price_usd = fetch_eth_price(chain)
print(f"ETH Price (USD): {eth_price_usd}")

# Calculate size delta in USD from the initial collateral delta
size_delta_usd = calculate_size_delta(initial_collateral_delta_eth, eth_price_usd)
print(f"Size Delta (USD): {size_delta_usd}")

# Define order parameters
parameters = {
    "chain": chain,
    "index_token_symbol": "ETH",
    "collateral_token_symbol": "ETH",
    "start_token_symbol": "ETH",
    "is_long": False,
    "size_delta_usd": size_delta_usd,
    "initial_collateral_delta": initial_collateral_delta_eth,
    "slippage_percent": 0.003
}

# Process parameters
order_parameters = OrderArgumentParser(
    config=arbitrum_config_object,
    is_increase=True
).process_parameters_dictionary(parameters)

print("Order Parameters:", order_parameters)

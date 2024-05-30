from utils import _set_paths
_set_paths()

from gmx_python_sdk.scripts.v2.order.order_argument_parser import (
    OrderArgumentParser
)
from gmx_python_sdk.scripts.v2.order.create_increase_order import IncreaseOrder
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager
from price_utils2 import get_eth_price_and_size_delta

arbitrum_config_object = ConfigManager(chain='arbitrum')
arbitrum_config_object.set_config()

# Define initial collateral delta in ETH
initial_collateral_delta_eth = 1  # Replace this with your actual value

# Fetching data (mock example, replace it with actual fetch logic)
data = {
    "0x1FF7F3EFBb9481Cbd7db4F932cBCD4467144237C": {
        "id": "2848670368",
        "minBlockNumber": 216079827,
        "tokenSymbol": "NEAR",
        "tokenAddress": "0x1FF7F3EFBb9481Cbd7db4F932cBCD4467144237C",
        "maxPriceFull": "7677087",
        "minPriceFull": "7675855",
    },
    "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1": {
        "id": "2848670366",
        "minBlockNumber": 216079828,
        "tokenSymbol": "ETH",
        "tokenAddress": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        "maxPriceFull": "3841914100000000",
        "minPriceFull": "3841778641080000",
    }
}

# Get price of ETH and calculate size delta
eth_price_usd, size_delta_usd = get_eth_price_and_size_delta(data, initial_collateral_delta_eth)

parameters = {
    "chain": 'arbitrum',
    "index_token_symbol": "ETH",
    "collateral_token_symbol": "ETH",
    "start_token_symbol": "ETH",
    "is_long": False,
    "size_delta_usd": size_delta_usd,
    "leverage": 1,
    "slippage_percent": 0.003
}

order_parameters = OrderArgumentParser(
    arbitrum_config_object,
    is_increase=True
).process_parameters_dictionary(
    parameters
)

order = IncreaseOrder(
    config=arbitrum_config_object,
    market_key=order_parameters['market_key'],
    collateral_address=order_parameters['start_token_address'],
    index_token_address=order_parameters['index_token_address'],
    is_long=order_parameters['is_long'],
    size_delta=order_parameters['size_delta'],
    initial_collateral_delta_amount=initial_collateral_delta_eth,  # Set this to the initial collateral delta in ETH
    slippage_percent=order_parameters['slippage_percent'],
    swap_path=order_parameters['swap_path'],
    debug_mode=True
)

print(f"ETH Price (USD): {eth_price_usd}")
print(f"Size Delta (USD): {size_delta_usd}")
print(f"Initial Collateral Delta (ETH): {initial_collateral_delta_eth}")

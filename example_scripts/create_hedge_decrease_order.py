import numpy as np
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager, get_tokens_address_dict
from gmx_python_sdk.scripts.v2.order.order_argument_parser import OrderArgumentParser as OrderArgumentParserCustom
from gmx_python_sdk.scripts.v2.get.get_oracle_prices import OraclePrices as OraclePricesCustom
from gmx_python_sdk.scripts.v2.order.create_decrease_order import DecreaseOrder

# Step 1: Setup Config and Initialize Classes
chain = 'arbitrum'
config = ConfigManager(chain)
config.set_config()

# Step 2: Fetch ETH price
oracle_prices = OraclePricesCustom(chain)
prices = oracle_prices.get_recent_prices()

# Assuming ETH address for Arbitrum
eth_address = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
eth_max_price = float(prices[eth_address]['maxPriceFull'])
eth_min_price = float(prices[eth_address]['minPriceFull'])

# Correct the price by scaling down
eth_price = np.median([eth_max_price, eth_min_price])
eth_price_usd = eth_price / 1e30

# Step 3: Define initial collateral delta in ETH
initial_collateral_delta_eth = 0.5  # Example input, replace with actual value

# Calculate size delta in USD
size_delta_usd = initial_collateral_delta_eth * eth_price_usd

# Step 4: Prepare Order Parameters
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

order_parser = OrderArgumentParserCustom(config, is_decrease=True)
order_parameters = order_parser.process_parameters_dictionary(parameters)

# Step 5: Create and Execute Decrease Order
order = DecreaseOrder(
    config=config,
    market_key=order_parameters['market_key'],
    collateral_address=order_parameters['start_token_address'],
    index_token_address=order_parameters['index_token_address'],
    is_long=order_parameters['is_long'],
    size_delta=order_parameters['size_delta'],
    initial_collateral_delta_amount=int(initial_collateral_delta_eth * 10**18),  # Convert to uint256 format
    slippage_percent=order_parameters['slippage_percent'],
    swap_path=order_parameters['swap_path'],
    debug_mode=True
)

print(f"ETH Price (USD): {eth_price_usd}")
print(f"Size Delta (USD): {size_delta_usd}")
print(f"Initial Collateral Delta (ETH): {initial_collateral_delta_eth}")
print("Order Parameters:", order_parameters)

# Execute the order (commented out to avoid actual execution)
# order.execute_order()

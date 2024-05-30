import numpy as np
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager, get_execution_price_and_price_impact, get_tokens_address_dict
from gmx_python_sdk.scripts.v2.order.order_argument_parser import OrderArgumentParser as OrderArgumentParserCustom
from gmx_python_sdk.scripts.v2.get.get_oracle_prices import OraclePrices as OraclePricesCustom
from gmx_python_sdk.scripts.v2.order.create_increase_order import IncreaseOrder

# Step 1: Setup Config and Initialize Classes
chain = 'arbitrum'
config = ConfigManager(chain)
config.set_config()

# Step 2: Fetch ETH price
oracle_prices = OraclePricesCustom(chain)
prices = oracle_prices.get_recent_prices()

# Assuming ETH address for Arbitrum
eth_address = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
eth_price = np.median([float(prices[eth_address]['maxPriceFull']), float(prices[eth_address]['minPriceFull'])])
eth_price_usd = eth_price / 1e30

# Step 3: Define initial collateral delta in ETH
initial_collateral_delta_eth = 1.0  # Example input, replace with actual value

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

order_parser = OrderArgumentParserCustom(config, is_increase=True)
order_parameters = order_parser.process_parameters_dictionary(parameters)

# Step 5: Fetch Execution Price and Validate
execution_params = {
    "data_store_address": config.data_store_address,
    "market_key": order_parameters['market_key'],
    "index_token_price": int(eth_price_usd * 1e30),
    "position_size_in_usd": int(size_delta_usd * 1e30),
    "position_size_in_tokens": int(initial_collateral_delta_eth * 1e18),
    "size_delta": order_parameters['size_delta'],
    "is_long": order_parameters['is_long'],
}

execution_price_info = get_execution_price_and_price_impact(config, execution_params, 18)

execution_price = execution_price_info['execution_price']
print(f"Execution Price: {execution_price}")

# Step 6: Create and Execute Increase Order
order = IncreaseOrder(
    config=config,
    market_key=order_parameters['market_key'],
    collateral_address=order_parameters['start_token_address'],
    index_token_address=order_parameters['index_token_address'],
    is_long=order_parameters['is_long'],
    size_delta=order_parameters['size_delta'],
    initial_collateral_delta_amount=initial_collateral_delta_eth,
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
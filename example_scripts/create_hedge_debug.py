import numpy as np
import logging
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager, contract_map
from gmx_python_sdk.scripts.v2.order.order_argument_parser import OrderArgumentParser as OrderArgumentParserCustom
from gmx_python_sdk.scripts.v2.get.get_oracle_prices import OraclePrices as OraclePricesCustom
from gmx_python_sdk.scripts.v2.order.create_increase_order import IncreaseOrder

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Step 1: Setup Config and Initialize Classes
chain = 'arbitrum'
config = ConfigManager(chain)
config.set_config()

# Fetch the data_store_address using the same approach from the provided script
data_store_address = contract_map[config.chain]['datastore']['contract_address']
logger.info(f"Data Store Address: {data_store_address}")

# Step 2: Fetch ETH price
oracle_prices = OraclePricesCustom(chain)
prices = oracle_prices.get_recent_prices()

# Assuming ETH address for Arbitrum
eth_address = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
eth_price = np.median([float(prices[eth_address]['maxPriceFull']), float(prices[eth_address]['minPriceFull'])])
eth_price_usd = eth_price / 1e30

logger.info(f"Fetched ETH Price (USD): {eth_price_usd}")

# Step 3: Define initial collateral delta in ETH
initial_collateral_delta_eth = 1.0  # Example input, replace with actual value

# Calculate size delta in USD
size_delta_usd = initial_collateral_delta_eth * eth_price_usd
logger.info(f"Calculated Size Delta (USD): {size_delta_usd}")

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
logger.info(f"Order Parameters: {order_parameters}")

# Step 5: Create and Execute Increase Order
try:
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
    logger.info(f"Order Created: {order}")
except Exception as e:
    logger.error(f"Error creating order: {e}")
    raise

# Assuming additional logging within the IncreaseOrder class itself
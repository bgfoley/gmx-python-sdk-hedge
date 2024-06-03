import logging
import numpy as np
import sys
from hexbytes import HexBytes
from web3 import Web3
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager, get_tokens_address_dict, create_connection
from gmx_python_sdk.scripts.v2.order.order_argument_parser import OrderArgumentParser as OrderArgumentParserCustom
from gmx_python_sdk.scripts.v2.get.get_oracle_prices import OraclePrices as OraclePricesCustom
from gmx_python_sdk.scripts.v2.order.create_increase_order import IncreaseOrder
from gmx_python_sdk.scripts.v2.gas_utils import get_execution_fee

# Manually defining order_type dictionary
order_types = {
    'market_increase': 0,
    'limit_increase': 1,
    'market_decrease': 2,
    'limit_decrease': 3,
    'stop_loss_decrease': 4,
    'liquidation': 5,
    'update': 6,
    'cancel': 7,
}

decrease_position_swap_types = {
    'no_swap': 0,
    'swap': 1,
}

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Step 1: Setup Config and Initialize Classes
chain = 'arbitrum'
config = ConfigManager(chain)
config.set_config()

# Verify configuration
logger.info(f"Using chain: {chain}")
logger.info(f"RPC URL: {config.rpc}")

# Initialize the connection
connection = create_connection(config)
if connection is None:
    logger.error("Failed to establish a connection.")
    sys.exit(1)

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

# Step 3: Query the deposit amount in ETH from the user
try:
    deposit_eth = float(input("Enter the amount of ETH to deposit: "))
except ValueError:
    logger.error("Invalid input. Please enter a numeric value.")
    sys.exit(1)

# Step 4: Estimate the execution fee (in ETH)
gas_price = connection.eth.gas_price
gas_limits = {
    'createOrder': 300000  # Example gas limit for creating an order
}

# Modify get_execution_fee function to calculate fee directly
def get_execution_fee(gas_limit, gas_price):
    return gas_limit * gas_price

execution_fee = get_execution_fee(gas_limits['createOrder'], gas_price)
execution_fee_eth = execution_fee / 1e18

# Step 5: Calculate the actual collateral delta (ETH)
collateral_delta_eth = deposit_eth - execution_fee_eth
if collateral_delta_eth <= 0:
    logger.error("Deposit amount is too low to cover the execution fee.")
    sys.exit(1)

# Step 6: Calculate the position size in USD based on the collateral delta
size_delta_usd = collateral_delta_eth * eth_price_usd

# Step 7: Prepare Order Parameters
parameters = {
    "chain": chain,
    "index_token_symbol": "ETH",
    "collateral_token_symbol": "ETH",
    "start_token_symbol": "ETH",
    "is_long": False,
    "size_delta_usd": size_delta_usd,
    "initial_collateral_delta": collateral_delta_eth,
    "slippage_percent": 0.003
}

order_parser = OrderArgumentParserCustom(config, is_increase=True)
order_parameters = order_parser.process_parameters_dictionary(parameters)

# Step 8: Create and Prepare to Print Increase Order Parameters
order = IncreaseOrder(
    config=config,
    market_key=order_parameters['market_key'],
    collateral_address=order_parameters['start_token_address'],
    index_token_address=order_parameters['index_token_address'],
    is_long=order_parameters['is_long'],
    size_delta=order_parameters['size_delta'],
    initial_collateral_delta_amount=int(collateral_delta_eth * 10**18),  # Convert to uint256 format
    slippage_percent=order_parameters['slippage_percent'],
    swap_path=order_parameters['swap_path'],
    debug_mode=True
)

# Set the order type explicitly
order_type = order_types['market_increase']

# Extract and format the order arguments for Solidity
def print_create_order_params(order, order_type):
    user_wallet_address = order.config.user_wallet_address
    eth_zero_address = "0x0000000000000000000000000000000000000000"
    ui_ref_address = "0x0000000000000000000000000000000000000000"
    should_unwrap_native_token = True
    referral_code = HexBytes("0x0000000000000000000000000000000000000000000000000000000000000000")

    arguments = (
        (
            user_wallet_address,
            eth_zero_address,
            ui_ref_address,
            order.market_key,
            order.collateral_address,
            order.swap_path
        ),
        (
            order.size_delta,
            order.initial_collateral_delta_amount,
            0,  # mark_price (not used in this context)
            0,  # acceptable_price (not used in this context)
            0,  # execution_fee (not used in this context)
            0,  # callback_gas_limit (not used in this context)
            0   # min_output_amount (not used in this context)
        ),
        order_type,
        decrease_position_swap_types['no_swap'],
        order.is_long,
        should_unwrap_native_token,
        referral_code
    )

    formatted_args = f"""
    CreateOrderParams(
        {arguments[0][0]},
        {arguments[0][1]},
        {arguments[0][2]},
        {arguments[0][3]},
        {arguments[0][4]},
        [{', '.join(arguments[0][5])}],
        {arguments[1][0]},
        {arguments[1][1]},
        {arguments[1][2]},
        {arguments[1][3]},
        {arguments[1][4]},
        {arguments[1][5]},
        {arguments[1][6]},
        {arguments[2]},
        {arguments[3]},
        {arguments[4]},
        {arguments[5]},
        {arguments[6]}
    )
    """
    print(formatted_args)

# Print the parameters
logger.info(f"ETH Price (USD): {eth_price_usd}")
logger.info(f"Execution Fee (ETH): {execution_fee_eth}")
logger.info(f"Collateral Delta (ETH): {collateral_delta_eth}")
logger.info(f"Size Delta (USD): {size_delta_usd}")
logger.info(f"Order Parameters: {order_parameters}")

# Print CreateOrderParams
print_create_order_params(order, order_type)

# Execute the order (commented out to avoid actual execution)
# order.execute_order()
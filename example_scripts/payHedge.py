from utils import _set_paths

_set_paths()

import logging
import json
import numpy as np
from datetime import datetime
from web3 import Web3
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager, create_connection
from gmx_python_sdk.scripts.v2.get.get_oracle_prices import OraclePrices as OraclePricesCustom
from gmx_python_sdk.scripts.v2.gas_utils import get_execution_fee
from gmx_python_sdk.scripts.v2.order.order_argument_parser import OrderArgumentParser
from gmx_python_sdk.scripts.v2.order.create_increase_order import IncreaseOrder
from gmx_python_sdk.scripts.v2 import keys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded parameters
chain = 'arbitrum'
GMX_MARKET = '0x450bb6774dd8a756274e0ab4107953259d2ac541'
WETH = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
HEDGE_VAULT = '0xYourHedgeVaultAddressHere'
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
DATASTORE_ADDRESS = '0xFD70de6b91282D8017aA4E741e9Ae325CAb992d8'
referral_code = "0x0000000000000000000000000000000000000000000000000000000000000000"
order_type = 0  # market_increase
decrease_position_swap_type = 0  # no_swap
callbackGasLimit = 3000000  # 3,000,000 wei in gas limit

# Load DataStore ABI from JSON file
with open('gmx_python_sdk/data_store/DataStoreABI.json', 'r') as f:
    DATASTORE_ABI = json.load(f)

# Setup Config and Initialize Classes
config = ConfigManager(chain)
config.set_config()

# Verify configuration
logger.info(f"Using chain: {chain}")
logger.info(f"RPC URL: {config.rpc}")

# Initialize the connection
logger.info(f"Start creating connection: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
connection = create_connection(config)
if connection is None:
    logger.error("Failed to establish a connection.")
    exit(1)
logger.info(f"Connection created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Step 2: Query the deposit amount in ETH from the user
try:
    deposit_eth = float(input("Enter the amount of ETH to spend: "))
except ValueError:
    logger.error("Invalid input. Please enter a numeric value.")
    exit(1)

# Fetch gas price
gas_price = connection.eth.gas_price

# Retrieve gas limits from DataStore
dataStore = connection.eth.contract(address=DATASTORE_ADDRESS, abi=DATASTORE_ABI)
baseGasLimit = dataStore.functions.getUint(keys.execution_gas_fee_base_amount_key()).call()
multiplierFactor = dataStore.functions.getUint(keys.execution_gas_fee_multiplier_key()).call()
estimatedGasLimit = dataStore.functions.getUint(keys.increase_order_gas_limit_key()).call()

# Calculate the adjusted gas limit and execution fee
adjustedGasLimit = baseGasLimit + (estimatedGasLimit * multiplierFactor // 10**8) + callbackGasLimit
execution_fee_wei = adjustedGasLimit * gas_price
execution_fee_eth = execution_fee_wei / 1e18
logger.info(f"Execution fee estimated: {execution_fee_eth} ETH")

# Calculate the actual collateral delta (ETH)
collateral_delta_eth = deposit_eth - execution_fee_eth - (callbackGasLimit * gas_price / 1e18)
if collateral_delta_eth <= 0:
    logger.error("Deposit amount is too low to cover the execution fee and callback gas limit.")
    exit(1)

# Fetch ETH price
oracle_prices = OraclePricesCustom(chain)
prices = oracle_prices.get_recent_prices()
eth_max_price = float(prices[WETH]['maxPriceFull'])
eth_min_price = float(prices[WETH]['minPriceFull'])
eth_price = np.median([eth_max_price, eth_min_price])
eth_price_usd = eth_price / 1e30

# Calculate the position size in USD based on the collateral delta
size_delta_usd = collateral_delta_eth * eth_price_usd

# Query slippage tolerance
slippage_tolerance = float(input("Enter your slippage tolerance (e.g., 0.01 for 1%): "))
slippage_multiplier = 1 - slippage_tolerance
acceptable_price = eth_price_usd * slippage_multiplier

parameters = {
    "chain": chain,
    "index_token_symbol": "ETH",
    "collateral_token_symbol": "ETH",
    "start_token_symbol": "ETH",
    "is_long": False,
    "size_delta_usd": size_delta_usd,
    "leverage": 1,
    "slippage_percent": slippage_tolerance
}

order_parameters = OrderArgumentParser(config, is_increase=True).process_parameters_dictionary(parameters)

order = IncreaseOrder(
    config=config,
    market_key=order_parameters['market_key'],
    collateral_address=order_parameters['start_token_address'],
    index_token_address=order_parameters['index_token_address'],
    is_long=order_parameters['is_long'],
    size_delta=order_parameters['size_delta'],
    initial_collateral_delta_amount=order_parameters['initial_collateral_delta'],
    slippage_percent=order_parameters['slippage_percent'],
    swap_path=order_parameters['swap_path'],
    debug_mode=True
)

# Print order parameters
def print_order_params(order_params):
    formatted_args = f"""
    [
        [
            "{order_params['addresses']['receiver']}",
            "{order_params['addresses']['callbackContract']}",
            "{order_params['addresses']['uiFeeReceiver']}",
            "{order_params['addresses']['market']}",
            "{order_params['addresses']['initialCollateralToken']}",
            {order_params['addresses']['swapPath']}
        ],
        [
            "{order_params['numbers']['sizeDeltaUsd']}",
            "{order_params['numbers']['initialCollateralDeltaAmount']}",
            "{order_params['numbers']['triggerPrice']}",
            "{order_params['numbers']['acceptablePrice']}",
            "{order_params['numbers']['executionFee']}",
            "{order_params['numbers']['callbackGasLimit']}",
            "{order_params['numbers']['minOutputAmount']}"
        ],
        {order_params['orderType']},
        {order_params['decreasePositionSwapType']},
        {order_params['isLong']},
        {order_params['shouldUnwrapNativeToken']},
        "{order_params['referralCode']}"
    ]
    """
    print(formatted_args)

print_order_params(order_parameters)
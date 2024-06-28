import logging
import numpy as np
from datetime import datetime
from hexbytes import HexBytes
from web3 import Web3
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager, create_connection
from gmx_python_sdk.scripts.v2.get.get_oracle_prices import OraclePrices as OraclePricesCustom
from gmx_python_sdk.scripts.v2.gas_utils import get_execution_fee

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded parameters
chain = 'arbitrum'
GMX_MARKET = '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336'
WETH = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
HEDGE_VAULT = '0x3cCa753479EEdEb4392A62B93568505F7B40D644'
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
user_wallet_address = '0xYourUserWalletAddressHere'
eth_zero_address = ZERO_ADDRESS
ui_ref_address = ZERO_ADDRESS
should_unwrap_native_token = True
referral_code = HexBytes("0x0000000000000000000000000000000000000000000000000000000000000000")
order_type = 0  # market_increase
decrease_position_swap_type = 0  # no_swap

# Step 1: Setup Config and Initialize Classes
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
    deposit_eth = float(input("Enter the amount of ETH to deposit: "))
except ValueError:
    logger.error("Invalid input. Please enter a numeric value.")
    exit(1)

# Step 3: Estimate the execution fee (in ETH)
logger.info(f"Start estimating execution fee: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
gas_price = connection.eth.gas_price
gas_limits = {
    'createOrder': 300000  # Example gas limit for creating an order
}

# Ensure correct calculation of the execution fee
execution_fee_wei = gas_limits['createOrder'] * gas_price
execution_fee_eth = execution_fee_wei / 1e18
logger.info(f"Execution fee estimated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Step 4: Calculate the actual collateral delta (ETH)
collateral_delta_eth = deposit_eth - execution_fee_eth
if collateral_delta_eth <= 0:
    logger.error("Deposit amount is too low to cover the execution fee.")
    exit(1)

# Step 5: Fetch ETH price
logger.info(f"Start fetching ETH price: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
oracle_prices = OraclePricesCustom(chain)
prices = oracle_prices.get_recent_prices()
logger.info(f"ETH price fetched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Assuming ETH address for Arbitrum
eth_max_price = float(prices[WETH]['maxPriceFull'])
eth_min_price = float(prices[WETH]['minPriceFull'])
eth_price = np.median([eth_max_price, eth_min_price])
eth_price_usd = eth_price / 1e30

# Step 6: Calculate the position size in USD based on the collateral delta
size_delta_usd = collateral_delta_eth * eth_price_usd

# Step 7: Create the order parameters
order_params = {
    "addresses": {
        "receiver": HEDGE_VAULT,
        "callbackContract": HEDGE_VAULT,
        "uiFeeReceiver": ZERO_ADDRESS,
        "market": GMX_MARKET,
        "initialCollateralToken": WETH,
        "swapPath": []
    },
    "numbers": {
        "sizeDeltaUsd": int(size_delta_usd * 1e30),
        "initialCollateralDeltaAmount": int(collateral_delta_eth * 1e18),
        "triggerPrice": 0,
        "acceptablePrice": int(eth_price_usd * 1e30 * (1 - 0.01)),  # 1% slippage tolerance
        "executionFee": int(execution_fee_wei),
        "callbackGasLimit": 0,
        "minOutputAmount": 0
    },
    "orderType": order_type,
    "decreasePositionSwapType": decrease_position_swap_type,
    "isLong": False,
    "shouldUnwrapNativeToken": should_unwrap_native_token,
    "referralCode": referral_code
}

# Log the order parameters
logger.info(f"ETH Price (USD): {eth_price_usd}")
logger.info(f"Execution Fee (ETH): {execution_fee_eth}")
logger.info(f"Collateral Delta (ETH): {collateral_delta_eth}")
logger.info(f"Size Delta (USD): {size_delta_usd}")
logger.info(f"Order Parameters: {order_params}")

# Print CreateOrderParams
def print_create_order_params(order_params):
    formatted_args = f"""
    CreateOrderParams(
        {order_params['addresses']['receiver']},
        {order_params['addresses']['callbackContract']},
        {order_params['addresses']['uiFeeReceiver']},
        {order_params['addresses']['market']},
        {order_params['addresses']['initialCollateralToken']},
        [{', '.join(order_params['addresses']['swapPath'])}],
        {order_params['numbers']['sizeDeltaUsd']},
        {order_params['numbers']['initialCollateralDeltaAmount']},
        {order_params['numbers']['triggerPrice']},
        {order_params['numbers']['acceptablePrice']},
        {order_params['numbers']['executionFee']},
        {order_params['numbers']['callbackGasLimit']},
        {order_params['numbers']['minOutputAmount']},
        {order_params['orderType']},
        {order_params['decreasePositionSwapType']},
        {order_params['isLong']},
        {order_params['shouldUnwrapNativeToken']},
        {order_params['referralCode']}
    )
    """
    print(formatted_args)

# Print CreateOrderParams
print_create_order_params(order_params)

# Uncomment this line to execute the order if you are ready
# order.execute_order()

import logging
import numpy as np
import sys
from hexbytes import HexBytes
from web3 import Web3
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager, create_connection
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

# Step 2: Query the deposit amount in ETH from the user
try:
    deposit_eth = float(input("Enter the amount of ETH to deposit: "))
except ValueError:
    logger.error("Invalid input. Please enter a numeric value.")
    sys.exit(1)

# Step 3: Estimate the execution fee (in ETH)
gas_price = connection.eth.gas_price
gas_limits = {
    'createOrder': 300000  # Example gas limit for creating an order
}

# Modify get_execution_fee function to calculate fee directly
def get_execution_fee(gas_limit, gas_price):
    return gas_limit * gas_price

execution_fee = get_execution_fee(gas_limits['createOrder'], gas_price)
execution_fee_eth = execution_fee / 1e18

# Step 4: Calculate the actual collateral delta (ETH)
collateral_delta_eth = deposit_eth - execution_fee_eth
if collateral_delta_eth <= 0:
    logger.error("Deposit amount is too low to cover the execution fee.")
    sys.exit(1)

# Step 5: Fetch ETH price
oracle_prices = OraclePricesCustom(chain)
prices = oracle_prices.get_recent_prices()

# Assuming ETH address for Arbitrum
eth_address = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
eth_max_price = float(prices[eth_address]['maxPriceFull'])
eth_min_price = float(prices[eth_address]['minPriceFull'])

# Correct the price by scaling down
eth_price = np.median([eth_max_price, eth_min_price])
eth_price_usd = eth_price / 1e30

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
    "slippage_percent": 0.01  # Increase slippage tolerance to 1%
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

# Define hedge contract address
hedge_contract_address = '0xYourHedgeContractAddress'  # Replace with your Hedge contract address
gmx_market = '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336'  # GMX market address
weth_address = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'  # WETH address
zero_address = '0x0000000000000000000000000000000000000000'  # Zero address

# Assemble the CreateOrderParams structure
order_params = {
    "addresses": {
        "receiver": hedge_contract_address,
        "callbackContract": hedge_contract_address,
        "uiFeeReceiver": zero_address,
        "market": gmx_market,
        "initialCollateralToken": weth_address,
        "swapPath": order_parameters['swap_path']
    },
    "numbers": {
        "sizeDeltaUsd": order_parameters['size_delta'],
        "initialCollateralDeltaAmount": order_parameters['initial_collateral_delta'],
        "triggerPrice": 0,  # triggerPrice not used
        "acceptablePrice": 0,  # acceptablePrice not used
        "executionFee": int(execution_fee),
        "callbackGasLimit": 0,  # callbackGasLimit not used
        "minOutputAmount": 0  # minOutputAmount not used
    },
    "orderType": order_type,
    "decreasePositionSwapType": decrease_position_swap_types['no_swap'],
    "isLong": False,
    "shouldUnwrapNativeToken": True,
    "referralCode": HexBytes("0x0000000000000000000000000000000000000000000000000000000000000000")
}

# Log the assembled order parameters
logger.info(f"Assembled Order Params: {order_params}")

# Interact with the Hedge contract
hedge_abi = [...]  # Replace with your Hedge contract ABI

hedge_contract = connection.eth.contract(address=hedge_contract_address, abi=hedge_abi)

# Prepare the transaction
txn = hedge_contract.functions.hedge(
    int(deposit_eth * 1e18),
    Web3.toChecksumAddress(order.config.user_wallet_address),
    order_params
).build_transaction({
    'chainId': config.chain_id,
    'gas': 300000,  # Example gas limit
    'gasPrice': connection.eth.gas_price,
    'nonce': connection.eth.get_transaction_count(Web3.toChecksumAddress(order.config.user_wallet_address)),
    'value': 0  # Adjust if you need to send ETH with the transaction
})

# Log the transaction details
logger.info(f"Prepared Transaction: {txn}")

# Comment out the actual execution for testing purposes
# Sign and send the transaction
# private_key = config.private_key
# signed_txn = connection.eth.account.sign_transaction(txn, private_key)
# tx_hash = connection.eth.send_raw_transaction(signed_txn.rawTransaction)

# logger.info(f"Transaction hash: {tx_hash.hex()}")
# logger.info(f"Check status: https://arbiscan.io/tx/{tx_hash.hex()}")

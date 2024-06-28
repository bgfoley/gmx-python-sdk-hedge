import logging
import numpy as np
from datetime import datetime
from web3 import Web3
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager, create_connection, get_datastore_contract
from gmx_python_sdk.scripts.v2.get.get_oracle_prices import OraclePrices as OraclePricesCustom
from gmx_python_sdk.scripts.v2.gas_utils import get_execution_fee
from gmx_python_sdk.scripts.v2.keys import (
    decrease_order_gas_limit_key, increase_order_gas_limit_key,
    execution_gas_fee_base_amount_key, execution_gas_fee_multiplier_key,
    single_swap_gas_limit_key, swap_order_gas_limit_key, deposit_gas_limit_key,
    withdraw_gas_limit_key
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded parameters
chain = 'arbitrum'
GMX_MARKET = '0x450bb6774dd8a756274e0ab4107953259d2ac541'
WETH = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
HEDGE_VAULT = '0x3cCa753479EEdEb4392A62B93568505F7B40D644'
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
user_wallet_address = '0xYourUserWalletAddressHere'
should_unwrap_native_token = True
referral_code = "0x0000000000000000000000000000000000000000000000000000000000000000"
order_type = 0  # market_increase
decrease_position_swap_type = 0  # no_swap
callback_gas_limit = 3000000  # 3,000,000 units

def get_input(prompt):
    return input(prompt)

def get_gas_limits(datastore_object):
    """
    Given a Web3 contract object of the datstore, return a dictionary with the uncalled gas limits
    that correspond to various operations that will require the execution fee to calculated for.

    Parameters
    ----------
    datastore_object : web3 object
        contract connection.

    """
    gas_limits = {
        "deposit": datastore_object.functions.getUint(deposit_gas_limit_key()),
        "withdraw": datastore_object.functions.getUint(withdraw_gas_limit_key()),
        "single_swap": datastore_object.functions.getUint(single_swap_gas_limit_key()),
        "swap_order": datastore_object.functions.getUint(swap_order_gas_limit_key()),
        "increase_order": datastore_object.functions.getUint(increase_order_gas_limit_key()),
        "decrease_order": datastore_object.functions.getUint(decrease_order_gas_limit_key()),
        "estimated_fee_base_gas_limit": datastore_object.functions.getUint(
            execution_gas_fee_base_amount_key()),
        "estimated_fee_multiplier_factor": datastore_object.functions.getUint(
            execution_gas_fee_multiplier_key())
    }

    return gas_limits

def main():
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
        deposit_eth = float(get_input("Enter the amount of ETH to deposit: "))
    except ValueError:
        logger.error("Invalid input. Please enter a numeric value.")
        exit(1)
    deposit_wei = int(deposit_eth * 1e18)

    # Step 3: Estimate the execution fee (in ETH) using the get_execution_fee function
    logger.info(f"Start estimating execution fee: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    datastore_object = get_datastore_contract(config)
    gas_limits = get_gas_limits(datastore_object)
    gas_price = connection.eth.gas_price
    execution_fee_wei = get_execution_fee(gas_limits, gas_limits['increase_order'], gas_price)
    
    # Add the callback gas limit fee
    callback_gas_fee_wei = callback_gas_limit * gas_price
    total_execution_fee_wei = execution_fee_wei + callback_gas_fee_wei
    
    execution_fee_eth = total_execution_fee_wei / 1e18
    logger.info(f"Execution fee estimated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 4: Calculate the actual collateral delta (ETH)
    collateral_delta_eth = deposit_eth - execution_fee_eth
    if collateral_delta_eth <= 0:
        logger.error("Deposit amount is too low to cover the execution fee and callback gas limit.")
        exit(1)
    collateral_delta_wei = int(collateral_delta_eth * 1e18)

    # Step 5: Fetch ETH price
    logger.info(f"Start fetching ETH price: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    oracle_prices = OraclePricesCustom(chain)
    prices = oracle_prices.get_recent_prices()
    logger.info(f"ETH price fetched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    eth_max_price = float(prices[WETH]['maxPriceFull'])
    eth_min_price = float(prices[WETH]['minPriceFull'])
    eth_price = np.median([eth_max_price, eth_min_price])
    eth_price_usd = eth_price / 1e30

    # Step 6: Calculate the position size in USD based on the collateral delta
    size_delta_usd = int(collateral_delta_eth * eth_price_usd * 1e30)  # Adjust to GMX format

    # Step 7: Create the order parameters
    order_params = [
        [
            HEDGE_VAULT,
            HEDGE_VAULT,
            ZERO_ADDRESS,
            GMX_MARKET,
            WETH,
            []
        ],
        [
            str(size_delta_usd),
            str(collateral_delta_wei),
            '0',
            str(int(eth_price_usd * 1e30 * (1 - 0.01))),  # 1% slippage tolerance
            str(total_execution_fee_wei),  # Ensure execution fee is formatted correctly
            str(callback_gas_limit),
            '0'
        ],
        order_type,
        decrease_position_swap_type,
        False,
        should_unwrap_native_token,
        referral_code
    ]

    # Log the order parameters
    logger.info(f"ETH Price (USD): {eth_price_usd}")
    logger.info(f"Execution Fee (ETH): {execution_fee_eth}")
    logger.info(f"Collateral Delta (ETH): {collateral_delta_eth}")
    logger.info(f"Size Delta (USD): {size_delta_usd}")


    # Print CreateOrderParams
    def print_create_order_params(order_params, deposit_wei, user_wallet_address):
        formatted_args = f"""
amount: {deposit_wei}
user: {user_wallet_address}
orderParams: [
  [
    "{order_params[0][0]}",
    "{order_params[0][1]}",
    "{order_params[0][2]}",
    "{order_params[0][3]}",
    "{order_params[0][4]}",
    {order_params[0][5]}
  ],
  [
    "{order_params[1][0]}",
    "{order_params[1][1]}",
    "{order_params[1][2]}",
    "{order_params[1][3]}",
    "{order_params[1][4]}",
    "{order_params[1][5]}",
    "{order_params[1][6]}"
  ],
  {order_params[2]},
  {order_params[3]},
  {str(order_params[4]).lower()},
  {str(order_params[5]).lower()},
  "{order_params[6]}"
]
"""
        print(formatted_args)

    # Print CreateOrderParams
    print_create_order_params(order_params, deposit_wei, user_wallet_address)

if __name__ == "__main__":
    main()

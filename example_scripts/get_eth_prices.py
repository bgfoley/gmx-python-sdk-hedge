import logging
import pandas as pd
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager
from gmx_python_sdk.scripts.v2.get.get_oracle_prices import OraclePrices

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Step 1: Setup Config and Initialize Classes
chain = 'arbitrum'
config = ConfigManager(chain)
config.set_config()

# Function to get the latest GMX oracle prices for ETH perps with ETH collateral
def get_eth_perp_prices():
    oracle_prices = OraclePrices(chain)
    prices = oracle_prices.get_recent_prices()
    
    # Assuming ETH address for Arbitrum
    eth_address = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
    
    if eth_address in prices:
        eth_prices = prices[eth_address]
        eth_max_price = float(eth_prices['maxPriceFull'])
        eth_min_price = float(eth_prices['minPriceFull'])
        eth_price = (eth_max_price + eth_min_price) / 2

        print(f"ETH Oracle Prices:")
        print(f"Max Price: {eth_max_price / 1e30} USD")
        print(f"Min Price: {eth_min_price / 1e30} USD")
        print(f"Median Price: {eth_price / 1e30} USD")
    else:
        print("ETH address not found in the oracle prices.")

# Run the function to get and print ETH perp prices
if __name__ == "__main__":
    get_eth_perp_prices()

# price_utils.py
import numpy as np
from ..get.get_oracle_prices import OraclePrices

def fetch_eth_price(chain):
    prices = OraclePrices(chain=chain).get_recent_prices()
    eth_price_data = prices.get("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1")  # ETH address
    if not eth_price_data:
        raise Exception("ETH price data not found")
    
    max_price = float(eth_price_data['maxPriceFull'])
    min_price = float(eth_price_data['minPriceFull'])
    eth_price = (max_price + min_price) / 2
    return eth_price / 1e18  # Convert from wei to ether

def calculate_size_delta(order_size_eth, eth_price_usd):
    return order_size_eth * eth_price_usd

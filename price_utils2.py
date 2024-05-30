import json

# Assuming data is already fetched and stored in a variable called `data`
data = {
    "0x1FF7F3EFBb9481Cbd7db4F932cBCD4467144237C": {
        "id": "2848670368",
        "minBlockNumber": 216079827,
        "tokenSymbol": "NEAR",
        "tokenAddress": "0x1FF7F3EFBb9481Cbd7db4F932cBCD4467144237C",
        "maxPriceFull": "7677087",
        "minPriceFull": "7675855",
    },
    "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1": {
        "id": "2848670366",
        "minBlockNumber": 216079828,
        "tokenSymbol": "ETH",
        "tokenAddress": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        "maxPriceFull": "3841914100000000",
        "minPriceFull": "3841778641080000",
    }
}

# Function to extract the ETH price
def extract_eth_price(data):
    for key, value in data.items():
        if value["tokenSymbol"] == "ETH":
            max_price = int(value["maxPriceFull"])
            min_price = int(value["minPriceFull"])
            eth_price = (max_price + min_price) / 2
            return eth_price / 1e18  # Convert from wei to ether
    return None

# Function to calculate the size delta in USD
def calculate_size_delta(order_size_eth, eth_price_usd):
    return order_size_eth * eth_price_usd

# Extract ETH price
eth_price_usd = extract_eth_price(data)
print(f"ETH Price (USD): {eth_price_usd}")

# Example order size in ETH
order_size_eth = 1.5  # Example size of the order in ETH

# Calculate size delta in USD
size_delta_usd = calculate_size_delta(order_size_eth, eth_price_usd)
print(f"Size Delta (USD): {size_delta_usd}")

# Returning values for main script usage
def get_eth_price_and_size_delta(data, order_size_eth):
    eth_price_usd = extract_eth_price(data)
    size_delta_usd = calculate_size_delta(order_size_eth, eth_price_usd)
    return eth_price_usd, size_delta_usd

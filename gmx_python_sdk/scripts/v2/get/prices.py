import requests

class OraclePrices:
    def __init__(self, chain: str):
        self.chain = chain
        self.oracle_url = {
            "arbitrum": (
                "https://arbitrum-api.gmxinfra.io/signed_prices/latest"
            ),
            "avalanche": (
                "https://avalanche-api.gmxinfra.io/signed_prices/latest"
            )
        }

    def get_recent_prices(self):
        """
        Get raw output of the GMX rest v2 api for signed prices

        Returns
        -------
        dict
            dictionary containing raw output for each token as its keys.

        """
        raw_output = self._make_query().json()
        return self._process_output(raw_output)

    def _make_query(self):
        """
        Make request using oracle url

        Returns
        -------
        requests.models.Response
            raw request response.

        """
        url = self.oracle_url[self.chain]
        return requests.get(url)

    def _process_output(self, output: dict):
        """
        Take the API response and create a new dictionary where the index token
        addresses are the keys

        Parameters
        ----------
        output : dict
            Dictionary of rest API repsonse.

        Returns
        -------
        processed : dict
            Processed dictionary with token addresses as keys.

        """
        processed = {}
        for i in output['signedPrices']:
            processed[i['tokenAddress']] = i
        return processed

def fetch_eth_price(chain: str):
    oracle_prices = OraclePrices(chain)
    prices = oracle_prices.get_recent_prices()
    eth_address = "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"  # ETH address on Arbitrum
    eth_price_data = prices.get(eth_address)
    if eth_price_data:
        eth_price = (int(eth_price_data['maxPriceFull']) + int(eth_price_data['minPriceFull'])) / 2 / 1e30  # Convert to USD
        return eth_price
    else:
        raise Exception("ETH price not found in the oracle data")

# Example usage
eth_price = fetch_eth_price("arbitrum")
print(f"ETH Price (USD): {eth_price}")

import numpy as np

class OrderArgumentParser:

    def __init__(self, config, is_increase: bool = False, is_decrease: bool = False, is_swap: bool = False):
        self.config = config
        self.parameters_dict = None
        self.is_increase = is_increase
        self.is_decrease = is_decrease
        self.is_swap = is_swap

        if is_increase:
            self.required_keys = [
                "chain",
                "index_token_address",
                "market_key",
                "start_token_address",
                "collateral_address",
                "swap_path",
                "is_long",
                "size_delta_usd",
                "initial_collateral_delta",
                "slippage_percent"
            ]

        if is_decrease:
            self.required_keys = [
                "chain",
                "index_token_address",
                "market_key",
                "start_token_address",
                "collateral_address",
                "is_long",
                "size_delta_usd",
                "initial_collateral_delta",
                "slippage_percent"
            ]

        if is_swap:
            self.required_keys = [
                "chain",
                "start_token_address",
                "out_token_address",
                "initial_collateral_delta",
                "swap_path",
                "slippage_percent"
            ]

        self.missing_base_key_methods = {
            "chain": self._handle_missing_chain,
            "index_token_address": self._handle_missing_index_token_address,
            "market_key": self._handle_missing_market_key,
            "start_token_address": self._handle_missing_start_token_address,
            "out_token_address": self._handle_missing_out_token_address,
            "collateral_address": self._handle_missing_collateral_address,
            "swap_path": self._handle_missing_swap_path,
            "is_long": self._handle_missing_is_long,
            "slippage_percent": self._handle_missing_slippage_percent
        }

    def process_parameters_dictionary(self, parameters_dict):
        missing_keys = self._determine_missing_keys(parameters_dict)
        self.parameters_dict = parameters_dict

        for missing_key in missing_keys:
            if missing_key in self.missing_base_key_methods:
                self.missing_base_key_methods[missing_key]()

        if not self.is_swap:
            self.calculate_missing_position_size_info_keys()
            self._check_if_max_leverage_exceeded()

        if self.is_increase:
            if self._calculate_initial_collateral_usd() < 2:
                raise Exception("Position size must be backed by >$2 of collateral!")

        self._format_size_info()

        return self.parameters_dict

    def _determine_missing_keys(self, parameters_dict):
        return [key for key in self.required_keys if key not in parameters_dict]

    def _handle_missing_chain(self):
        raise Exception("Please pass chain name in parameters dictionary!")

    def _handle_missing_index_token_address(self):
        try:
            token_symbol = self.parameters_dict['index_token_symbol']
        except KeyError:
            raise Exception("Index Token Address and Symbol not provided!")

        self.parameters_dict['index_token_address'] = self.find_key_by_symbol(
            get_tokens_address_dict(self.parameters_dict['chain']),
            token_symbol
        )

    def _handle_missing_market_key(self):
        index_token_address = self.parameters_dict['index_token_address']
        self.parameters_dict['market_key'] = self.find_market_key_by_index_address(
            Markets(self.config).get_available_markets(),
            index_token_address
        )

    def _handle_missing_start_token_address(self):
        try:
            start_token_symbol = self.parameters_dict['start_token_symbol']
        except KeyError:
            raise Exception("Start Token Address and Symbol not provided!")

        self.parameters_dict['start_token_address'] = self.find_key_by_symbol(
            get_tokens_address_dict(self.parameters_dict['chain']),
            start_token_symbol
        )

    def _handle_missing_out_token_address(self):
        try:
            out_token_symbol = self.parameters_dict['out_token_symbol']
        except KeyError:
            raise Exception("Out Token Address and Symbol not provided!")

        self.parameters_dict['out_token_address'] = self.find_key_by_symbol(
            get_tokens_address_dict(self.parameters_dict['chain']),
            out_token_symbol
        )

    def _handle_missing_collateral_address(self):
        try:
            collateral_token_symbol = self.parameters_dict['collateral_token_symbol']
        except KeyError:
            raise Exception("Collateral Token Address and Symbol not provided!")

        collateral_address = self.find_key_by_symbol(
            get_tokens_address_dict(self.parameters_dict['chain']),
            collateral_token_symbol
        )

        if self._check_if_valid_collateral_for_market(collateral_address) and not self.is_swap:
            self.parameters_dict['collateral_address'] = collateral_address

    def _handle_missing_swap_path(self):
        if self.is_swap:
            markets = Markets(chain=self.parameters_dict['chain']).get_available_markets()
            self.parameters_dict['swap_path'] = determine_swap_route(
                markets,
                self.parameters_dict['start_token_address'],
                self.parameters_dict['out_token_address']
            )[0]

        elif self.parameters_dict['start_token_address'] == self.parameters_dict['collateral_address']:
            self.parameters_dict['swap_path'] = []

        else:
            markets = Markets(chain=self.parameters_dict['chain']).get_available_markets()
            self.parameters_dict['swap_path'] = determine_swap_route(
                markets,
                self.parameters_dict['start_token_address'],
                self.parameters_dict['collateral_address']
            )[0]

    def _handle_missing_is_long(self):
        raise Exception("Please indicate if position is_long!")

    def _handle_missing_slippage_percent(self):
        raise Exception("Please indicate slippage!")

    def _check_if_valid_collateral_for_market(self, collateral_address: str):
        market_key = self.parameters_dict['market_key']
        market = Markets(self.config).get_available_markets()[market_key]
        if collateral_address == market['long_token_address'] or collateral_address == market['short_token_address']:
            return True
        else:
            raise Exception("Not a valid collateral for selected market!")

    @staticmethod
    def find_key_by_symbol(input_dict: dict, search_symbol: str):
        for key, value in input_dict.items():
            if value.get('symbol') == search_symbol:
                return key
        raise Exception(f'"{search_symbol}" not a known token for GMX v2!')

    @staticmethod
    def find_market_key_by_index_address(input_dict: dict, index_token_address: str):
        for key, value in input_dict.items():
            if value.get('index_token_address') == index_token_address:
                return key
        return None

    def calculate_missing_position_size_info_keys(self):
        if "size_delta_usd" in self.parameters_dict and "initial_collateral_delta" in self.parameters_dict:
            return self.parameters_dict

        elif "leverage" in self.parameters_dict and "initial_collateral_delta" in self.parameters_dict and "size_delta_usd" not in self.parameters_dict:
            initial_collateral_delta_usd = self._calculate_initial_collateral_usd()
            self.parameters_dict["size_delta_usd"] = self.parameters_dict["leverage"] * initial_collateral_delta_usd
            return self.parameters_dict

        elif "size_delta_usd" in self.parameters_dict and "leverage" in self.parameters_dict and "initial_collateral_delta" not in self.parameters_dict:
            collateral_usd = self.parameters_dict["size_delta_usd"] / self.parameters_dict["leverage"]
            self.parameters_dict["initial_collateral_delta"] = self._calculate_initial_collateral_tokens(collateral_usd)
            return self.parameters_dict

        else:
            raise Exception('Required keys are missing or provided incorrectly, please check: "size_delta_usd", "initial_collateral_delta", or "leverage"!')

    def _calculate_initial_collateral_usd(self):
        initial_collateral_delta_amount = self.parameters_dict['initial_collateral_delta']
        eth_price = fetch_eth_price(self.parameters_dict['chain'])
        return eth_price * initial_collateral_delta_amount

    def _calculate_initial_collateral_tokens(self, collateral_usd: float):
        eth_price = fetch_eth_price(self.parameters_dict['chain'])
        return collateral_usd / eth_price

    def _format_size_info(self):
        if not self.is_swap:
            self.parameters_dict["size_delta"] = int(self.parameters_dict["size_delta_usd"] * 10**30)
        decimal = get_tokens_address_dict(self.parameters_dict['chain'])[self.parameters_dict["start_token_address"]]['decimals']
        self.parameters_dict["initial_collateral_delta"] = int(self.parameters_dict["initial_collateral_delta"] * 10**decimal)

    def _check_if_max_leverage_exceeded(self):
        collateral_usd_value = self._calculate_initial_collateral_usd()
        leverage_requested = self.parameters_dict["size_delta_usd"] / collateral_usd_value
        max_leverage = 100
        if leverage_requested > max_leverage:
            raise Exception(f'Leverage requested "x{leverage_requested:.2f}" can not exceed x100!')

if __name__ == "__main__":
     chain = 'arbitrum'
    
    initial_collateral_delta_eth = 1.1
    eth_price_usd = fetch_eth_price("arbitrum")
    
    parameters = {
        "chain": 'arbitrum',
        "index_token_symbol": "ETH",
        "start_token_symbol": "ETH",
        "collateral_token_symbol": "ETH",
        "is_long": False,
        "initial_collateral_delta": initial_collateral_delta_eth,
        "slippage_percent": 0.003
    }

    parser = OrderArgumentParser(arbitrum_config_object, is_increase=True)
    processed_parameters = parser.process_parameters_dictionary(parameters)
    
    print(processed_parameters)

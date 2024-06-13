class OrderArgumentParser2:

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

        # Hardcoding some values
        parameters_dict['index_token_address'] = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
        parameters_dict['market_key'] = '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336'
        parameters_dict['start_token_address'] = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
        parameters_dict['collateral_address'] = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
        parameters_dict['swap_path'] = []
        parameters_dict['is_long'] = False

        self.parameters_dict = parameters_dict

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

    def calculate_missing_position_size_info_keys(self):
        if "size_delta_usd" in self.parameters_dict and \
                "initial_collateral_delta" in self.parameters_dict:
            return self.parameters_dict
        elif "leverage" in self.parameters_dict and \
                "initial_collateral_delta" in self.parameters_dict and \
                "size_delta_usd" not in self.parameters_dict:
            initial_collateral_delta_usd = self._calculate_initial_collateral_usd()
            self.parameters_dict["size_delta_usd"] = (
                self.parameters_dict["leverage"] * initial_collateral_delta_usd
            )
            return self.parameters_dict
        elif "size_delta_usd" in self.parameters_dict and "leverage" in self.parameters_dict and \
                "initial_collateral_delta" not in self.parameters_dict:
            collateral_usd = self.parameters_dict["size_delta_usd"] / \
                self.parameters_dict["leverage"]
            self.parameters_dict[
                "initial_collateral_delta"
            ] = self._calculate_initial_collateral_tokens(collateral_usd)
            return self.parameters_dict
        else:
            potential_missing_keys = '"size_delta_usd", "initial_collateral_delta", or "leverage"!'
            raise Exception(
                "Required keys are missing or provided incorrectly, please check: {}".format(
                    potential_missing_keys
                )
            )

    def _calculate_initial_collateral_usd(self):
        initial_collateral_delta_amount = self.parameters_dict['initial_collateral_delta']
        prices = OraclePrices(chain=self.parameters_dict['chain']).get_recent_prices()
        price = np.median(
            [float(prices[self.parameters_dict["start_token_address"]]['maxPriceFull']),
             float(prices[self.parameters_dict["start_token_address"]]['minPriceFull'])]
        )
        oracle_factor = 18 - 30  # Adjusted based on the token's decimals
        price = price * 10 ** oracle_factor
        return price * initial_collateral_delta_amount

    def _calculate_initial_collateral_tokens(self, collateral_usd: float):
        prices = OraclePrices(chain=self.parameters_dict['chain']).get_recent_prices()
        price = np.median(
            [float(prices[self.parameters_dict["start_token_address"]]['maxPriceFull']),
             float(prices[self.parameters_dict["start_token_address"]]['minPriceFull'])]
        )
        oracle_factor = 18 - 30  # Adjusted based on the token's decimals
        price = price * 10 ** oracle_factor
        return collateral_usd / price

    def _format_size_info(self):
        if not self.is_swap:
            self.parameters_dict["size_delta"] = int(
                self.parameters_dict["size_delta_usd"] * 10**30)
        decimal = 18  # Adjusted based on the token's decimals
        self.parameters_dict["initial_collateral_delta"] = int(
            self.parameters_dict["initial_collateral_delta"] * 10**decimal
        )

    def _check_if_max_leverage_exceeded(self):
        collateral_usd_value = self._calculate_initial_collateral_usd()
        leverage_requested = self.parameters_dict["size_delta_usd"] / \
            collateral_usd_value
        max_leverage = 100
        if leverage_requested > max_leverage:
            raise Exception('Leverage requested "x{:.2f}" can not exceed x100!'.format(
                leverage_requested
            )
            )

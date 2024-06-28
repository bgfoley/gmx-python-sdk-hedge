from utils import _set_paths
from decimal import Decimal
from gmx_python_sdk.scripts.v2.get.get_markets import Markets
from gmx_python_sdk.scripts.v2.get.get_open_positions import GetOpenPositions
from gmx_python_sdk.scripts.v2.gmx_utils import (
    ConfigManager, find_dictionary_by_key_value, get_tokens_address_dict,
    determine_swap_route
)

_set_paths()

def get_positions(config, address: str = None):
    """
    Get open positions for an address on a given network.
    If address is not passed it will take the address from the users config file.

    Parameters
    ----------
    config : object
        ConfigManager object with chain settings.
    address : str, optional
        Address to fetch open positions for. The default is None.

    Returns
    -------
    positions : dict
        Dictionary containing all open positions.
    """
    if address is None:
        address = config.user_wallet_address
        if address is None:
            raise Exception("No address passed in function or config!")

    positions = GetOpenPositions(config=config, address=address).get_data()

    if len(positions) > 0:
        print(f"Open Positions for {address}:")
        for key in positions.keys():
            print(key)
    else:
        print(f"No open positions found for {address}.")

    return positions

def transform_open_position_to_order_parameters(
    config,
    positions: dict,
    market_symbol: str,
    is_long: bool,
    slippage_percent: float,
    out_token,
    amount_of_position_to_close,
    amount_of_collateral_to_remove
):
    """
    Find the user-defined trade from market_symbol and is_long in a dictionary positions
    and return a dictionary formatted correctly to close 100% of that trade.

    Parameters
    ----------
    config : object
        ConfigManager object with chain settings.
    positions : dict
        Dictionary containing all open positions.
    market_symbol : str
        Symbol of market trader.
    is_long : bool
        True for long, False for short.
    slippage_percent : float
        Slippage tolerance to close trade as a percentage.
    out_token : str
        The token to receive after closing the position.
    amount_of_position_to_close : float
        Fraction of the position to close.
    amount_of_collateral_to_remove : float
        Fraction of the collateral to remove.

    Returns
    -------
    dict
        Order parameters formatted to close the position.
    """
    direction = "short" if not is_long else "long"
    position_dictionary_key = f"{market_symbol.upper()}_{direction}"

    # Find the key that matches the market_symbol and direction
    matching_key = None
    for key in positions.keys():
        if market_symbol.upper() in key and direction in key:
            matching_key = key
            break

    if not matching_key:
        raise Exception(f"Couldn't find a {market_symbol} {direction} for given user!")

    print(f"Using position key: {matching_key}")

    try:
        raw_position_data = positions[matching_key]
        gmx_tokens = get_tokens_address_dict(config.chain)

        # Try finding the token by both WETH and ETH symbols
        weth_token = find_dictionary_by_key_value(gmx_tokens, "symbol", "WETH")
        if weth_token is None:
            weth_token = find_dictionary_by_key_value(gmx_tokens, "symbol", "ETH")
        if weth_token is None:
            raise Exception(f"Couldn't find WETH or ETH in the token dictionary.")
        
        weth_address = weth_token["address"]

        out_token_address = find_dictionary_by_key_value(
            gmx_tokens, "symbol", out_token
        )
        if out_token_address is None:
            raise Exception(f"Couldn't find {out_token} in the token dictionary.")
        out_token_address = out_token_address['address']

        markets = Markets(config=config).get_available_markets()

        swap_path = []
        if weth_address != out_token_address:
            swap_path = determine_swap_route(
                markets, weth_address, out_token_address
            )[0]

        size_delta = int(
            (Decimal(raw_position_data['position_size']) * (Decimal(10)**30)) * Decimal(amount_of_position_to_close)
        )

        return {
            "chain": config.chain,
            "market_key": raw_position_data['market'],
            "collateral_address": weth_address,
            "index_token_address": weth_address,
            "is_long": raw_position_data['is_long'],
            "size_delta": size_delta,
            "initial_collateral_delta": int(
                Decimal(raw_position_data['inital_collateral_amount']) * Decimal(amount_of_collateral_to_remove)
            ),
            "slippage_percent": slippage_percent,
            "swap_path": swap_path
        }
    except KeyError:
        raise Exception(f"Couldn't find a {market_symbol} {direction} for given user!")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

if __name__ == "__main__":
    config = ConfigManager(chain='arbitrum')
    config.set_config()

    user_address = input("Enter the address to fetch open positions for: ")
    positions = get_positions(config=config, address=user_address)

    market_symbol = "ETH"
    is_long = False

    try:
        order_params = transform_open_position_to_order_parameters(
            config,
            positions,
            market_symbol,
            is_long,
            0.003,
            "USDC",  # Example out_token, you can change as needed
            1.0,  # Example: close 100% of the position
            1.0   # Example: remove 100% of the collateral
        )
        print(order_params)
    except Exception as e:
        print(e)

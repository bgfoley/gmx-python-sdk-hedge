Notes:
CLI - python get_positions.py <your_address>




# GMX Python SDK

A python based SDK developed for interacting with GMX v2

- [Requirements](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#requirements)
- [Config File Setup](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#config-file-setup)
- [Example Scripts](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#example-scripts)
- [General Usage](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#general-usage)
    - [Increase Position](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#increase-position)
    - [Decrease Position](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#decrease-position)
    - [Swap Order](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#swap-order)
    - [Deposit Order](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#deposit-order)
    - [Withdraw Order](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#withdraw-order)
    - [Estimate Swap Output](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#estimate-swap-output)
    - [Helper Scripts](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#helper-scripts)
        - [Order Argument Parser](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#order-argument-parser)
        - [Liquidity Argument Parser](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#liquidity-argument-parser)
        - [Closing Positions](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#closing-positions)
    - [GMX Stats](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#gmx-stats)
    - [Debug Mode](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#debug-mode)
- [Known Limitations](https://github.com/snipermonke01/gmx_python_sdk/tree/main?tab=readme-ov-file#known-limitations)


## Requirements

Developed using:
```python
  python=3.10.4
```

If not using the pip method to install package you may also try creating a new conda environment step by step with the following instructions:
```
conda create --name gmx_sdk python=3.10
conda activate gmx_sdk
pip install numpy
pip install hexbytes
pip install web3==6.10.0
pip install pyaml
pip install pandas==1.4.2
pip install numerize
```

The codebase is designed around the usage of web3py [6.10.0](https://web3py.readthedocs.io/en/stable/releases.html#web3-py-v6-10-0-2023-09-21), and will not work with older versions and has not been tested with the latest version.
## Config File Setup

[Config file](https://github.com/snipermonke01/gmx_python_sdk/blob/main/config.yaml) must set up before usage. For stats based operations, you will need only an RPC but for execution you need to save both a wallet address and the private key of that wallet. 

```yaml
arbitrum:
  rpc: rpc_url
  chain_id: chain_id
avalanche:
  rpc: rpc_url
  chain_id: chain_id
private_key: private_key
user_wallet_address: wallet_address
```

The example script [setting_config.py](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/setting_config.py) can be viewed for demonstration on how to import config and update with new details from script.

There is an example in [create_increase_.py](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/setting_config.py) of how it is possible to [set config parameters](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/create_increase_order.py#L8-L19) within the py script, and then [reset these](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/create_increase_order.py#L71-L77) once the script has finished running.

## Example Scripts

There are several example scripts which can be run and can be found in [example scripts.](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/) These are mostly for demonstration purposes on how to utilise the SDK, and can should be incoporated into your own scripts and strategies.


## General Usage

### [Increase Position](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/create_increase_order.py)

The following block demonstrates how to open (or increase) a position:

```python
from scripts.v2.create_increase_order import IncreaseOrder

order = IncreaseOrder(
    chain,
    market_key,
    collateral_address,
    index_token_address,
    is_long,
    size_delta_usd,
    initial_collateral_delta_amount,
    slippage_percent,
    swap_path
)
```
**chain** - *type str*: either 'arbitrum' or 'avalanche' (avalanche currently in testing still)

**market_key** - *type str*: the contract address of the GMX market you want to increase a position on

**collateral_address** - *type str*: the contract address of the token you want to use as collateral

**index_token_address** - *type str*: the contract address of the token you want to trade

**is_long** - *type bool*: True for long or False for short

**size_delta_usd** - *type int*: the size of position you want to open 10^30

**initial_collateral_delta_amount** - *type int*: the amount of token you want to use as collateral, 10^decimal of that token

**slippage_percent** - *type float*: the percentage you want to allow slippage

**swap_path** - *type list(str)*: a list of the GMX markets you will need to swap through if the starting token is different to the token you want to use as collateral

### [Decrease Position](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/create_decrease_order.py)

The following block demonstrates how to close (or decrease) a position:

```python
from scripts.v2.create_decrease_order import DecreaseOrder

order = DecreaseOrder(
    chain,
    market_key,
    collateral_address,
    index_token_address,
    is_long,
    size_delta_usd,
    initial_collateral_delta_amount,
    slippage_percent,
    swap_path
)
```
**chain** - *type str*: either 'arbitrum' or 'avalanche' (currently in testing still)

**market_key** - *type str*: the contract address of the GMX market you want to decrease a position for

**collateral_address** - *type str*: the contract address of the token you are using as collateral

**index_token_address** - *type str*: the contract address of the token are trading

**is_long** - *type bool*: True for long or False for short

**size_delta_usd** - *type int*: the size of the decrease to apply to your position, 10^30

**initial_collateral_delta_amount** - *type int*: the amount of collateral token you want to remove, 10^decimal of that token

**slippage_percent** - *type float*: the percentage you want to allow slippage

**swap_path** - *type list(str)*: a list of the GMX markets you will need to swap through to get your desired out token

### [Swap Order](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/create_swap_order.py)

The following block demonstrates how to make a swap:

```python
from scripts.v2.create_swap_order import SwapOrder

order = SwapOrder(
    chain,
    market_key,
    start_token,
    out_token,
    collateral_address,
    index_token_address,
    is_long,
    size_delta,
    initial_collateral_delta_amount,
    slippage_percent,
    swap_path
)
```
**chain** - *type str*: either 'arbitrum' or 'avalanche' (currently in testing still)

**market_key** - *type str*: the contract address of the GMX market you want to (first) market you want to swap through

**start_token** - *type str*: the contract address of the token you start the swap with

**out_token** - *type str*: the contract address of the token you want out

**collateral_address** - *type str*: the contract address of the token you start the swap with

**index_token** - *type str*: the contract address of the token you want out

**is_long** - *type bool*: set to False

**size_delta_usd** - *type int*: set to 0

**initial_collateral_delta_amount** - *type int*: the amount of start token you are swapping

**slippage_percent** - *type float*: the percentage you want to allow slippage

**swap_path** - *type list()*: list of gmx market address your swap will go through

### [Deposit Order](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/create_deposit_order.py)

The following block demonstrates how to make a deposit to a gm pool:

```python
from scripts.v2.create_deposit_order import DepositOrder

order = DepositOrder(
    chain,
    market_key,
    initial_long_token,
    initial_short_token,
    long_token_amount,
    short_token_amount
)
```
**chain** - *type str*: either 'arbitrum' or 'avalanche' (currently in testing still)

**market_key** - *type str*: the contract address of the GMX market you want to deposit into

**initial_long_token** - *type str*: the contract address of the token you want to use to deposit into long side, can be None

**initial_short_token** - *type str*: the contract address of the token you want to use to deposit into short side, can be None

**long_token_amount** - *type str*: the amount of token to add to long side, can be 0

**short_token_amount** - *type str*: the amount of token to add to short side, can be 0

### [Withdraw Order](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/create_withdraw_order.py)

The following block demonstrates how to make a withdrawal from a gm pool:

```python
from scripts.v2.create_withdrawal_order import WithdrawOrder

order = WithdrawOrder(
    chain,
    market_key,
    out_token,
    gm_amount
)
```
**chain** - *type str*: either 'arbitrum' or 'avalanche' (currently in testing still)

**market_key** - *type str*: the contract address of the GMX market you want to withdraw from

**out_token** - *type str*: the contract address of the token you want to use to receive

**gm_amount** - *type str*: amount of gm tokens to burn

### Get Execution Price & Price Impact On Position Change


```python
from scripts.v2.gmx_utils import get_execution_price_and_price_impact

chain = "arbitrum"
estimated_swap_output_parameters = {
    'data_store_address': (data_store_address),
    'market_addresses': [
        gmx_market_address,
        index_token_address,
        long_token_address,
        short_token_address
    ],
    'token_prices_tuple': [
        [
            int(max_price_of_index_token),
            int(min_price_of_index_token)
        ],
        [
            int(max_price_of_long_token),
            int(min_price_of_long_token)
        ],
        [
            int(max_price_of_short_token),
            int(min_price_of_short_token])
        ],
    ],
    'token_in': in_token_address,
    'token_amount_in': in_token_amount,
    'ui_fee_receiver': "0x0000000000000000000000000000000000000000"
}

get_execution_price_and_price_impact(
    chain,
    estimated_swap_output_parameters,
    decimals
)

```

### Estimate Swap output

Below shows an example of how to estimate swap output using the [EstimateSwapOutput](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/estimate_swap_output.py#L21) class in [estimate_swap_ouput.py](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/estimate_swap_output.py). One can provide either a token symbol or contract address for in and out tokens and the script will return a dictionary containing the estimate output number of tokens and price impact.

```python
from estimate_swap_output import EstimateSwapOutput

chain = "arbitrum"
in_token_symbol = "SOL"
out_token_symbol = "USDC"
token_amount = 2
in_token_address = None
out_token_address = None
token_amount_expanded = None

output = EstimateSwapOutput(chain=chain).get_swap_output(
    in_token_symbol=in_token_symbol,
    out_token_symbol=out_token_symbol,
    token_amount=token_amount,
    in_token_address=in_token_address,
    out_token_address=out_token_address,
    token_amount_expanded=token_amount_expanded
)

```

### Helper Scripts

To assist in argument formatting, there are a few helper functions:

#### [Order Argument Parser](https://github.com/snipermonke01/gmx_python_sdk/blob/main/scripts/v2/order_argument_parser.py)

Human readable numbers can be parsed in a dictionary with the following keys/values which are processed by a class, OrderArgumentParser. This class should initialised with a bool to indicate is_increase, is_decrease, or is_swap, calling the method: "process_parameters_dictionary". This will output a dictionary containing the user input parameters reformatted to allow for successful order creation.

For increase:


```python
from scripts.v2.order_argument_parser import OrderArgumentParser


parameters = {
    "chain": 'arbitrum',

    # the market you want to trade on
    "index_token_symbol": "ARB",

    # the token you want as collateral
    "collateral_token_symbol": "ARB",

    # the token to start with
    "start_token_symbol": "USDC",

    # True for long, False for short
    "is_long": False,

    # in USD
    "size_delta": 6.69,

    # if leverage is passed, will calculate number of tokens in start_token_symbol amount
    "leverage": 1,

    # as a percentage
    "slippage_percent": 0.03
}


order_parameters = OrderArgumentParser(is_increase=True).process_parameters_dictionary(parameters)
```

For decrease:

```python
from scripts.v2.order_argument_parser import OrderArgumentParser

parameters = {
    "chain": 'arbitrum',
    "index_token_symbol": "ARB",

    "collateral_token_symbol": "USDC",

    # set start token the same as your collateral
    "start_token_symbol": "USDC",

    "is_long": False,

    # amount of your position you want to close in USD
    "size_delta": 12,

    # amount of collateral you want to remove in collateral tokens
    "initial_collateral_delta": 6,

    # as a percentage
    "slippage_percent": 0.03
}


order_parameters = OrderArgumentParser(is_decrease=True).process_parameters_dictionary(parameters)
```
For Swap:

```python
from scripts.v2.order_argument_parser import OrderArgumentParser

parameters = {
    "chain": 'arbitrum',

    # token to use as collateral. Start token swaps into collateral token if different
    "out_token_symbol": "ETH",

    # the token to start with - WETH not supported yet
    "start_token_symbol": "USDC",

    # True for long, False for short
    "is_long": False,

    # Position size in in USD
    "size_delta_usd": 0,

    # Amount of start tokens to swap out
    "initial_collateral_delta": 10,

    # as a percentage
    "slippage_percent": 0.03
}


order_parameters = OrderArgumentParser(is_swap=True).process_parameters_dictionary(parameters)
```
#### [Liquidity Argument Parser](https://github.com/snipermonke01/gmx_python_sdk/blob/main/scripts/v2/order_argument_parser.py)

Human readable numbers can be parsed in a dictionary with the following keys/values which are processed by a class, LiquidityArgumentParser. This class should initialised with a bool to indicate is_deposit or is_withdraw calling the method: "process_parameters_dictionary". This will output a dictionary containing the user input parameters reformatted to allow for successful deposit/withdrawal order creation.

For Deposit:

```python
from scripts.v2.liquidity_argument_parser import LiquidityArgumentParser

parameters = {
    "chain": "arbitrum",
    "market_token_symbol": "ETH",
    "long_token_symbol": "ETH",
    "short_token_symbol": USDC,
    "long_token_usd": 10,
    "short_token_usd": 10
}

output = LiquidityArgumentParser(is_deposit=True).process_parameters_dictionary(parameters)
```


For Withdraw:

```python
from scripts.v2.liquidity_argument_parser import LiquidityArgumentParser

parameters = {
    "chain": "arbitrum",
    "market_token_symbol": "ETH",
    "out_token_symbol": "ETH",
    "gm_amount": 1
}

output = LiquidityArgumentParser(is_withdrawal=True).process_parameters_dictionary(parameters)
```

#### Closing positions

Instead of passing the parameters to close a position, if you are aware of the market symbol and the direction of the trade you want to close you can pass these to [transform_open_position_to_order_parameters](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/get_positions.py#L46) after collecting all open positions using [get_positions](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/get_positions.py#L13). You can specify the amount of collateral or position size to remove/close as a decimal, eg 0.5 would close/remove 50% of size/collateral:

```python
from get_positions import get_positions, transform_open_position_to_order_parameters

chain = "arbitrum"
market_symbol = "ETH"
out_token = "ETH"
is_long = False
slippage_percent = 0.003
amount_of_position_to_close = 1
amount_of_collateral_to_remove = 1

# gets all open positions as a dictionary, which the keys as each position
positions = get_positions(chain)

order_parameters = transform_open_position_to_order_parameters(
    chain,
    positions,
    market_symbol,
    is_long,
    slippage_percent,
    out_token,
    amount_of_position_to_close,
    amount_of_collateral_to_remove
)
```

### GMX Stats

A number of stats can be obtained using a wide range of scripts. The overview on how to call these can be found in [get_gmx_stats](https://github.com/snipermonke01/gmx_python_sdk/blob/main/example_scripts/get_gmx_stats.py). Each method returns a dictionary containing long/short information for a given chain. When initialising the class, pass to_json or to_csv as True to save the output to the [data store](https://github.com/snipermonke01/gmx_python_sdk/tree/main/data_store): 

```python
from get_gmx_stats import GetGMXv2Stats

to_json = False
to_csv = False
chain = "arbitrum"

stats_object = GetGMXv2Stats(
    to_json=to_json,
    to_csv=to_csv
)

liquidity = stats_object.get_available_liquidity(chain=chain)
borrow_apr = stats_object.get_borrow_apr(chain=chain)
claimable_fees = stats_object.get_claimable_fees(chain=chain)
contract_tvl = stats_object.get_contract_tvl(chain=chain)
funding_apr = stats_object.get_funding_apr(chain=chain)
gm_prices = stats_object.get_gm_price(chain=chain)
markets = stats_object.get_available_markets(chain=chain)
open_interest = stats_object.get_open_interest(chain=chain)
oracle_prices = stats_object.get_oracle_prices(chain=chain)
pool_tvl = stats_object.get_pool_tvl(chain=chain)
```

### Debug Mode

It is possible to call IncreaseOrder, DecreaseOrder, SwapOrder, DepositOrder, and WithdrawOrder in debug mode by passing debug_mode=True when initialising the class:

```python
from scripts.v2.create_increase_order import IncreaseOrder

order = IncreaseOrder(
    chain,
    market_key,
    collateral_address,
    index_token_address,
    is_long,
    size_delta_usd,
    initial_collateral_delta_amount,
    slippage_percent,
    swap_path
    debug_mode=True
)
```

This will allow you to submit parameters to the order class and build your txn without executing it.

### Known Limitations

- Avalanche chain not fully tested.
- A high rate limit RPC is required to read multiple sets of stats successively.
- Possible to specify out token not the long/short of the GM market when withdrawing,
  but it will fail and return GM tokens to users wallet.

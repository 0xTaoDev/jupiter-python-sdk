<div align="center">
    <h1>🐍 JUPITER PYTHON SDK 🪐</h1>
    <img src="https://github.com/0xTaoDev/jupiter-python-sdk/blob/main/images/jupiter-python-sdk-banner.png?raw=true" width="75%" height="75%">
</div>

---

<p align="center">
    <img src="https://img.shields.io/github/stars/0xtaodev/jupiter-python-sdk">
    <img src="https://img.shields.io/github/forks/0xtaodev/jupiter-python-sdk">
    <br>
    <img src="https://img.shields.io/github/issues/0xtaodev/jupiter-python-sdk">
    <img src="https://img.shields.io/github/issues-closed/0xtaodev/jupiter-python-sdk">
    <br>
    <img src="https://img.shields.io/github/languages/top/0xtaodev/jupiter-python-sdk">
    <img src="https://img.shields.io/github/last-commit/0xtaodev/jupiter-python-sdk">
    <br>
</p>

# 📖 Introduction
**Jupiter Python SDK** is a Python library that allows you to use most of **[Jupiter](https://jup.ag/) features**.<br>
It enables executing swaps, limit orders, DCA, swap pairs, tokens prices, fetching wallet infos, stats, data and more!<br>
This library is using packages like: [solana-py](https://github.com/michaelhly/solana-py), [solders](https://github.com/kevinheavey/solders), [anchorpy](https://github.com/kevinheavey/anchorpy).<br>
There is documentation inside each function, however, you can access to the [official Jupiter API](https://docs.jup.ag/docs) for more information.

# ⚠️ Disclaimer
**Please note that I'm not responsible for any loss of funds, damages, or other libailities resulting from the use of this software or any associated services.<br>
This tool is provided for educational purposes only and should not be used as financial advice, it is still in expiremental phase so use it at your own risk.**

# ✨ Quickstart

### 🛠️ Installation

```sh
pip install jupiter-python-sdk
```

### 📃 General Usage
**Providing the private key and RPC client is not mandatory if you only intend to execute functions for retrieving data.<br>
Otherwise, this is required, for instance, to open a DCA account or to close one.**

**You can set custom URLs for any self-hosted Jupiter APIs. Like the [V6 Swap API](https://station.jup.ag/docs/apis/self-hosted) or [QuickNode's Metis API](https://marketplace.quicknode.com/add-on/metis-jupiter-v6-swap-api).**

If you encounter ```ImportError: cannot import name 'sync_native' from 'spl.token.instructions``` error when trying to import Jupiter, Jupiter_DCA from jupiter_python_sdk.jupiter, follow these steps:
1. Go to https://github.com/michaelhly/solana-py/tree/master/src/spl/token and download ```instructions.py```
2. In your packages folder, replace ```spl/token/instructions.py``` with the one you just downloaded.

### Here is a code snippet on how to use the SDK
```py
import base58
import base64
import json

from solders import message
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed

from jupiter_python_sdk.jupiter import Jupiter, Jupiter_DCA


private_key = Keypair.from_bytes(base58.b58decode(os.getenv("PRIVATE-KEY"))) # Replace PRIVATE-KEY with your private key as string
async_client = AsyncClient("SOLANA-RPC-ENDPOINT-URL") # Replace SOLANA-RPC-ENDPOINT-URL with your Solana RPC Endpoint URL
jupiter = Jupiter(
    async_client=async_client,
    keypair=private_key,
    quote_api_url="https://quote-api.jup.ag/v6/quote?",
    swap_api_url="https://quote-api.jup.ag/v6/swap",
    open_order_api_url="https://jup.ag/api/limit/v1/createOrder",
    cancel_orders_api_url="https://jup.ag/api/limit/v1/cancelOrders",
    query_open_orders_api_url="https://jup.ag/api/limit/v1/openOrders?wallet=",
    query_order_history_api_url="https://jup.ag/api/limit/v1/orderHistory",
    query_trade_history_api_url="https://jup.ag/api/limit/v1/tradeHistory"
)


"""
EXECUTE A SWAP
"""
transaction_data = await jupiter.swap(
    input_mint="So11111111111111111111111111111111111111112",
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    amount=5_000_000,
    slippage_bps=1,
)
# Returns str: serialized transactions to execute the swap.

raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
signature = private_key.sign_message(message.to_bytes_versioned(raw_transaction.message))
signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])
opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
result = await async_client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
transaction_id = json.loads(result.to_json())['result']
print(f"Transaction sent: https://explorer.solana.com/tx/{transaction_id}")


"""
OPEN LIMIT ORDER
"""
transaction_data = await jupiter.open_order(
    input_mint=So11111111111111111111111111111111111111112",
    output_mint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    in_amount=5_000_000,
    out_amount=100_000,
)
# Returns dict: {'transaction_data': serialized transactions to create the limit order, 'signature2': signature of the account that will be opened}

raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data['transaction_data']))
signature = private_key.sign_message(message.to_bytes_versioned(raw_transaction.message))
signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature, transaction_data['signature2']])
opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
result = await async_client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
transaction_id = json.loads(result.to_json())['result']
print(f"Transaction sent: https://explorer.solana.com/tx/{transaction_id}")


"""
CREATE DCA ACCOUNT
"""
create_dca_account = await jupiter.dca.create_dca(
    input_mint=Pubkey.from_string("So11111111111111111111111111111111111111112"),
    output_mint=Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
    total_in_amount=5_000_000,
    in_amount_per_cycle=100_000,
    cycle_frequency=60,
    min_out_amount_per_cycle=0,
    max_out_amount_per_cycle=0,
    start=0
)
# Returns DCA Account Pubkey and transaction hash.


"""
CLOSE DCA ACCOUNT
"""
close_dca_account = await jupiter.dca.close_dca(
    dca_pubkey=Pubkey.from_string("45iYdjmFUHSJCQHnNpWNFF9AjvzRcsQUP9FDBvJCiNS1")
)
# Returns transaction hash.
```

### 📜 All available features
```py
- quote
- swap
- open_order
- cancel_orders
- create_dca
- close_dca
- fetch_user_dca_accounts
- fetch_dca_account_fills_history
- get_available_dca_tokens
- fetch_dca_data
- query_open_orders
- query_orders_history
- query_trades_history
- get_jupiter_stats
- get_token_price
- get_indexed_route_map
- get_tokens_list
- get_all_tickers
- get_all_swap_pairs
- get_swap_pairs
- get_token_stats_by_date
- program_id_to_label
```

# 📝 TO-DO
- [ ] Bridge 🌉
- [ ] Perpetual 💸
- [ ] Price API
- [ ] Wallet Transactions History

# 🤝 Contributions
If you are interesting in contributing, fork the repository and submit a pull request in order to merge your improvements into the main repository.<br>
Contact me for any inquiry, I will reach you as soon as possible.<br>
[![Discord](https://img.shields.io/badge/Discord-%237289DA.svg?logo=discord&logoColor=white)](https://discord.gg/QxwPGcXDp7)
[![Twitter](https://img.shields.io/badge/Twitter-%231DA1F2.svg?logo=Twitter&logoColor=white)](https://twitter.com/_TaoDev_)

# 👑 Donations
This project doesn't include platform fees. If you find value in it and would like to support its development, your donations are greatly appreciated.<br>
**SOLANA ADDRESS**
```sh
AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX
```

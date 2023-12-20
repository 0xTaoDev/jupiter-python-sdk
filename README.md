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
This library is using packages like: [solana-py](https://github.com/michaelhly/solana-py), [solders](https://github.com/kevinheavey/solders), [anchorpy](https://github.com/kevinheavey/anchorpy).

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
```py
import base58
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from jupiter import Jupiter, Jupiter_DCA

async def main():
    private_key = Keypair.from_bytes(base58.b58decode(os.getenv("PRIVATE_KEY"))) # Private key as string
    async_client = AsyncClient(os.getenv("RPC_API"))
    jupiter = Jupiter(async_client, private_key)
    
    # EXECUTE A SWAP
    swap = await jupiter.swap(
        input_mint=Pubkey.from_string("So11111111111111111111111111111111111111112"),
        output_mint=Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        amount=5_000_000,
        slippage_bps=1,
    )
    # Returns str: serialized transactions to execute the swap.

    # OPEN LIMIT ORDER
    open_limit_order = await jupiter.open_order(
        input_mint=Pubkey.from_string("So11111111111111111111111111111111111111112"),
        output_mint=Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        in_amount=5_000_000,
        out_amount=100_000,
    )
    # Returns dict: {'transaction_data': serialized transactions to create the limit order, 'signature2': signature of the account that will be opened}

    # CREATE DCA ACCOUNT
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

    # CLOSE DCA ACCOUNT
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
- get_toekn_stats_by_date
- program_id_to_label
```

# 🤝 Contributions
If you are interesting in contributing, fork the repository and submit a pull request in order to merge your improvements into the main repository.<br>
Contact me for any inquiry, I will reach you as soon as possible.<br>
[![Discord](https://img.shields.io/badge/Discord-%237289DA.svg?logo=discord&logoColor=white)](https://discord.gg/_taodev_)
[![Twitter](https://img.shields.io/badge/Twitter-%231DA1F2.svg?logo=Twitter&logoColor=white)](https://twitter.com/_TaoDev_)

# 👑 Donations
This project doesn't include platform fees. If you find value in it and would like to support its development, your donations are greatly appreciated.<br>
**SOLANA ADDRESS**
```sh
AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX
```

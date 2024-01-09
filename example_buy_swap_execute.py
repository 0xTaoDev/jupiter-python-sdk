import base58
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from jupiter_python_sdk.jupiter import Jupiter, Jupiter_DCA
import asyncio
from solana.transaction import Transaction
import base64
from solana.rpc.api import Client
from solders.system_program import TransferParams, transfer
import base64, json,time, os, sys
from solders.transaction import VersionedTransaction
from solders.message import to_bytes_versioned
from solders.signature import Signature
from solana.rpc.commitment import Commitment

from solana.rpc.api import RPCException


async def main():
    private_key = Keypair.from_bytes(base58.b58decode('PRIVATE-KEY')) # Private key as string
    #async_client = AsyncClient('RPC-URL')
    jupiter = Jupiter(async_client, private_key)

    # EXECUTE A SWAP
    swap = await jupiter.swap(
        input_mint="So11111111111111111111111111111111111111112",
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        amount=5_000_000,
        slippage_bps=1,
    )

    raw_tx = VersionedTransaction.from_bytes(base64.b64decode(swap))

    signature = private_key.sign_message(to_bytes_versioned(raw_tx.message))
    signed_tx = VersionedTransaction.populate(raw_tx.message, [signature])

    print(swap)
    txid=''

    ctx = AsyncClient('RPC-URL', commitment=Commitment("confirmed"), timeout=30,blockhash_cache=True)

    try:
        print("6. Execute Transaction...")
        start_time = time.time()
        txid = (await ctx.send_transaction(
            signed_tx
        ))
    except Exception as e:
        print(e)





if __name__ == "__main__":
    asyncio.run(main())

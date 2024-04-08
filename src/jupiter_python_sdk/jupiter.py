import base64
import json
import time
import struct

import httpx
from httpx._config import Timeout

from typing import Any

from solders import message
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.system_program import transfer, TransferParams

from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed

from spl.token.instructions import create_associated_token_account, get_associated_token_address, sync_native, SyncNativeParams, close_account, CloseAccountParams
from spl.token.constants import *

from construct import Container
from anchorpy.program.core import Program as AnchorProgram
from anchorpy.program.core import Idl, Provider
from anchorpy.provider import Wallet
from anchorpy import Context
from anchorpy import AccountsCoder


class Jupiter_DCA():
    
    DCA_PROGRAM_ID = Pubkey.from_string("DCA265Vj8a9CEuX1eb1LWRnDT7uK6q1xMipnNyatn23M")
    IDL = {"version":"0.1.0","name":"dca","instructions":[{"name":"openDca","accounts":[{"name":"dca","isMut":True,"isSigner":False},{"name":"user","isMut":True,"isSigner":True},{"name":"inputMint","isMut":False,"isSigner":False},{"name":"outputMint","isMut":False,"isSigner":False},{"name":"userAta","isMut":True,"isSigner":False},{"name":"inAta","isMut":True,"isSigner":False},{"name":"outAta","isMut":True,"isSigner":False},{"name":"systemProgram","isMut":False,"isSigner":False},{"name":"tokenProgram","isMut":False,"isSigner":False},{"name":"associatedTokenProgram","isMut":False,"isSigner":False},{"name":"eventAuthority","isMut":False,"isSigner":False},{"name":"program","isMut":False,"isSigner":False}],"args":[{"name":"applicationIdx","type":"u64"},{"name":"inAmount","type":"u64"},{"name":"inAmountPerCycle","type":"u64"},{"name":"cycleFrequency","type":"i64"},{"name":"minPrice","type":{"option":"u64"}},{"name":"maxPrice","type":{"option":"u64"}},{"name":"startAt","type":{"option":"i64"}},{"name":"closeWsolInAta","type":{"option":"bool"}}]},{"name":"openDcaV2","accounts":[{"name":"dca","isMut":True,"isSigner":False},{"name":"user","isMut":False,"isSigner":True},{"name":"payer","isMut":True,"isSigner":True},{"name":"inputMint","isMut":False,"isSigner":False},{"name":"outputMint","isMut":False,"isSigner":False},{"name":"userAta","isMut":True,"isSigner":False},{"name":"inAta","isMut":True,"isSigner":False},{"name":"outAta","isMut":True,"isSigner":False},{"name":"systemProgram","isMut":False,"isSigner":False},{"name":"tokenProgram","isMut":False,"isSigner":False},{"name":"associatedTokenProgram","isMut":False,"isSigner":False},{"name":"eventAuthority","isMut":False,"isSigner":False},{"name":"program","isMut":False,"isSigner":False}],"args":[{"name":"applicationIdx","type":"u64"},{"name":"inAmount","type":"u64"},{"name":"inAmountPerCycle","type":"u64"},{"name":"cycleFrequency","type":"i64"},{"name":"minPrice","type":{"option":"u64"}},{"name":"maxPrice","type":{"option":"u64"}},{"name":"startAt","type":{"option":"i64"}}]},{"name":"closeDca","accounts":[{"name":"user","isMut":True,"isSigner":True},{"name":"dca","isMut":True,"isSigner":False},{"name":"inputMint","isMut":False,"isSigner":False},{"name":"outputMint","isMut":False,"isSigner":False},{"name":"inAta","isMut":True,"isSigner":False},{"name":"outAta","isMut":True,"isSigner":False},{"name":"userInAta","isMut":True,"isSigner":False},{"name":"userOutAta","isMut":True,"isSigner":False},{"name":"systemProgram","isMut":False,"isSigner":False},{"name":"tokenProgram","isMut":False,"isSigner":False},{"name":"associatedTokenProgram","isMut":False,"isSigner":False},{"name":"eventAuthority","isMut":False,"isSigner":False},{"name":"program","isMut":False,"isSigner":False}],"args":[]},{"name":"withdraw","accounts":[{"name":"user","isMut":True,"isSigner":True},{"name":"dca","isMut":True,"isSigner":False},{"name":"inputMint","isMut":False,"isSigner":False},{"name":"outputMint","isMut":False,"isSigner":False},{"name":"dcaAta","isMut":True,"isSigner":False},{"name":"userInAta","isMut":True,"isSigner":False,"isOptional":True},{"name":"userOutAta","isMut":True,"isSigner":False,"isOptional":True},{"name":"systemProgram","isMut":False,"isSigner":False},{"name":"tokenProgram","isMut":False,"isSigner":False},{"name":"associatedTokenProgram","isMut":False,"isSigner":False},{"name":"eventAuthority","isMut":False,"isSigner":False},{"name":"program","isMut":False,"isSigner":False}],"args":[{"name":"withdrawParams","type":{"defined":"WithdrawParams"}}]},{"name":"deposit","accounts":[{"name":"user","isMut":True,"isSigner":True},{"name":"dca","isMut":True,"isSigner":False},{"name":"inAta","isMut":True,"isSigner":False},{"name":"userInAta","isMut":True,"isSigner":False},{"name":"tokenProgram","isMut":False,"isSigner":False},{"name":"eventAuthority","isMut":False,"isSigner":False},{"name":"program","isMut":False,"isSigner":False}],"args":[{"name":"depositIn","type":"u64"}]},{"name":"withdrawFees","accounts":[{"name":"admin","isMut":True,"isSigner":True},{"name":"mint","isMut":False,"isSigner":False},{"name":"feeAuthority","isMut":False,"isSigner":False,"docs":["CHECK"]},{"name":"programFeeAta","isMut":True,"isSigner":False},{"name":"adminFeeAta","isMut":True,"isSigner":False},{"name":"systemProgram","isMut":False,"isSigner":False},{"name":"tokenProgram","isMut":False,"isSigner":False},{"name":"associatedTokenProgram","isMut":False,"isSigner":False}],"args":[{"name":"amount","type":"u64"}]},{"name":"initiateFlashFill","accounts":[{"name":"keeper","isMut":True,"isSigner":True},{"name":"dca","isMut":True,"isSigner":False},{"name":"inputMint","isMut":False,"isSigner":False,"docs":["The token to borrow"]},{"name":"keeperInAta","isMut":True,"isSigner":False,"docs":["The account to send borrowed tokens to"]},{"name":"inAta","isMut":True,"isSigner":False,"docs":["The account to borrow from"]},{"name":"outAta","isMut":False,"isSigner":False,"docs":["The account to repay to"]},{"name":"instructionsSysvar","isMut":False,"isSigner":False,"docs":["Solana Instructions Sysvar"]},{"name":"systemProgram","isMut":False,"isSigner":False},{"name":"tokenProgram","isMut":False,"isSigner":False},{"name":"associatedTokenProgram","isMut":False,"isSigner":False}],"args":[]},{"name":"fulfillFlashFill","accounts":[{"name":"keeper","isMut":True,"isSigner":True},{"name":"dca","isMut":True,"isSigner":False},{"name":"inputMint","isMut":False,"isSigner":False},{"name":"outputMint","isMut":False,"isSigner":False},{"name":"keeperInAta","isMut":False,"isSigner":False},{"name":"inAta","isMut":False,"isSigner":False},{"name":"outAta","isMut":False,"isSigner":False},{"name":"feeAuthority","isMut":False,"isSigner":False,"docs":["CHECK"]},{"name":"feeAta","isMut":True,"isSigner":False},{"name":"instructionsSysvar","isMut":False,"isSigner":False,"docs":["Solana Instructions Sysvar"]},{"name":"systemProgram","isMut":False,"isSigner":False},{"name":"tokenProgram","isMut":False,"isSigner":False},{"name":"associatedTokenProgram","isMut":False,"isSigner":False},{"name":"eventAuthority","isMut":False,"isSigner":False},{"name":"program","isMut":False,"isSigner":False}],"args":[{"name":"repayAmount","type":"u64"}]},{"name":"transfer","accounts":[{"name":"keeper","isMut":True,"isSigner":True},{"name":"dca","isMut":True,"isSigner":False},{"name":"user","isMut":True,"isSigner":False},{"name":"outputMint","isMut":False,"isSigner":False},{"name":"dcaOutAta","isMut":True,"isSigner":False},{"name":"userOutAta","isMut":True,"isSigner":False,"isOptional":True},{"name":"intermediateAccount","isMut":True,"isSigner":False,"isOptional":True},{"name":"systemProgram","isMut":False,"isSigner":False},{"name":"tokenProgram","isMut":False,"isSigner":False},{"name":"associatedTokenProgram","isMut":False,"isSigner":False},{"name":"eventAuthority","isMut":False,"isSigner":False},{"name":"program","isMut":False,"isSigner":False}],"args":[]},{"name":"endAndClose","accounts":[{"name":"keeper","isMut":True,"isSigner":True},{"name":"dca","isMut":True,"isSigner":False},{"name":"inputMint","isMut":False,"isSigner":False},{"name":"outputMint","isMut":False,"isSigner":False},{"name":"inAta","isMut":True,"isSigner":False},{"name":"outAta","isMut":True,"isSigner":False},{"name":"user","isMut":True,"isSigner":False},{"name":"userOutAta","isMut":True,"isSigner":False,"isOptional":True},{"name":"initUserOutAta","isMut":True,"isSigner":False,"isOptional":True},{"name":"intermediateAccount","isMut":True,"isSigner":False,"isOptional":True},{"name":"systemProgram","isMut":False,"isSigner":False},{"name":"tokenProgram","isMut":False,"isSigner":False},{"name":"associatedTokenProgram","isMut":False,"isSigner":False},{"name":"eventAuthority","isMut":False,"isSigner":False},{"name":"program","isMut":False,"isSigner":False}],"args":[]}],"accounts":[{"name":"Dca","type":{"kind":"struct","fields":[{"name":"user","type":"publicKey"},{"name":"inputMint","type":"publicKey"},{"name":"outputMint","type":"publicKey"},{"name":"idx","type":"u64"},{"name":"nextCycleAt","type":"i64"},{"name":"inDeposited","type":"u64"},{"name":"inWithdrawn","type":"u64"},{"name":"outWithdrawn","type":"u64"},{"name":"inUsed","type":"u64"},{"name":"outReceived","type":"u64"},{"name":"inAmountPerCycle","type":"u64"},{"name":"cycleFrequency","type":"i64"},{"name":"nextCycleAmountLeft","type":"u64"},{"name":"inAccount","type":"publicKey"},{"name":"outAccount","type":"publicKey"},{"name":"minOutAmount","type":"u64"},{"name":"maxOutAmount","type":"u64"},{"name":"keeperInBalanceBeforeBorrow","type":"u64"},{"name":"dcaOutBalanceBeforeSwap","type":"u64"},{"name":"createdAt","type":"i64"},{"name":"bump","type":"u8"}]}}],"types":[{"name":"WithdrawParams","type":{"kind":"struct","fields":[{"name":"withdrawAmount","type":"u64"},{"name":"withdrawal","type":{"defined":"Withdrawal"}}]}},{"name":"Withdrawal","type":{"kind":"enum","variants":[{"name":"In"},{"name":"Out"}]}}],"events":[{"name":"CollectedFee","fields":[{"name":"userKey","type":"publicKey","index":False},{"name":"dcaKey","type":"publicKey","index":False},{"name":"mint","type":"publicKey","index":False},{"name":"amount","type":"u64","index":False}]},{"name":"Filled","fields":[{"name":"userKey","type":"publicKey","index":False},{"name":"dcaKey","type":"publicKey","index":False},{"name":"inputMint","type":"publicKey","index":False},{"name":"outputMint","type":"publicKey","index":False},{"name":"inAmount","type":"u64","index":False},{"name":"outAmount","type":"u64","index":False},{"name":"feeMint","type":"publicKey","index":False},{"name":"fee","type":"u64","index":False}]},{"name":"Opened","fields":[{"name":"userKey","type":"publicKey","index":False},{"name":"dcaKey","type":"publicKey","index":False},{"name":"inDeposited","type":"u64","index":False},{"name":"inputMint","type":"publicKey","index":False},{"name":"outputMint","type":"publicKey","index":False},{"name":"cycleFrequency","type":"i64","index":False},{"name":"inAmountPerCycle","type":"u64","index":False},{"name":"createdAt","type":"i64","index":False}]},{"name":"Closed","fields":[{"name":"userKey","type":"publicKey","index":False},{"name":"dcaKey","type":"publicKey","index":False},{"name":"inDeposited","type":"u64","index":False},{"name":"inputMint","type":"publicKey","index":False},{"name":"outputMint","type":"publicKey","index":False},{"name":"cycleFrequency","type":"i64","index":False},{"name":"inAmountPerCycle","type":"u64","index":False},{"name":"createdAt","type":"i64","index":False},{"name":"totalInWithdrawn","type":"u64","index":False},{"name":"totalOutWithdrawn","type":"u64","index":False},{"name":"unfilledAmount","type":"u64","index":False},{"name":"userClosed","type":"bool","index":False}]},{"name":"Withdraw","fields":[{"name":"dcaKey","type":"publicKey","index":False},{"name":"inAmount","type":"u64","index":False},{"name":"outAmount","type":"u64","index":False},{"name":"userWithdraw","type":"bool","index":False}]},{"name":"Deposit","fields":[{"name":"dcaKey","type":"publicKey","index":False},{"name":"amount","type":"u64","index":False}]}],"errors":[{"code":6000,"name":"InvalidAmount","msg":"Invalid deposit amount"},{"code":6001,"name":"InvalidCycleAmount","msg":"Invalid deposit amount"},{"code":6002,"name":"InvalidPair","msg":"Invalid pair"},{"code":6003,"name":"TooFrequent","msg":"Too frequent DCA cycle"},{"code":6004,"name":"InvalidMinPrice","msg":"Minimum price constraint must be greater than 0"},{"code":6005,"name":"InvalidMaxPrice","msg":"Maximum price constraint must be greater than 0"},{"code":6006,"name":"InAmountInsufficient","msg":"In amount needs to be more than in amount per cycle"},{"code":6007,"name":"Unauthorized","msg":"Wrong user"},{"code":6008,"name":"NoInATA","msg":"inAta not passed in"},{"code":6009,"name":"NoUserInATA","msg":"userInAta not passed in"},{"code":6010,"name":"NoOutATA","msg":"outAta not passed in"},{"code":6011,"name":"NoUserOutATA","msg":"userOutAta not passed in"},{"code":6012,"name":"InsufficientBalanceInProgram","msg":"Trying to withdraw more than available"},{"code":6013,"name":"InvalidDepositAmount","msg":"Deposit should be more than 0"},{"code":6014,"name":"UserInsufficientBalance","msg":"User has insufficient balance"},{"code":6015,"name":"UnauthorizedKeeper","msg":"Unauthorized Keeper"},{"code":6016,"name":"UnrecognizedProgram","msg":"Unrecognized Program"},{"code":6017,"name":"MathErrors","msg":"Calculation errors"},{"code":6018,"name":"KeeperNotTimeToFill","msg":"Not time to fill"},{"code":6019,"name":"OrderFillAmountWrong","msg":"Order amount wrong"},{"code":6020,"name":"SwapOutAmountBelowMinimum","msg":"Out amount below expectations"},{"code":6021,"name":"WrongAdmin","msg":"Wrong admin"},{"code":6022,"name":"MathOverflow","msg":"Overflow in arithmetic operation"},{"code":6023,"name":"AddressMismatch","msg":"Address Mismatch"},{"code":6024,"name":"ProgramMismatch","msg":"Program Mismatch"},{"code":6025,"name":"IncorrectRepaymentAmount","msg":"Incorrect Repayment Amount"},{"code":6026,"name":"CannotBorrowBeforeRepay","msg":"Cannot Borrow Before Repay"},{"code":6027,"name":"NoRepaymentInstructionFound","msg":"No Repayment Found"},{"code":6028,"name":"MissingSwapInstructions","msg":"Missing Swap Instruction"},{"code":6029,"name":"UnexpectedSwapProgram","msg":"Expected Instruction to use Jupiter Swap Program"},{"code":6030,"name":"UnknownInstruction","msg":"Unknown Instruction"},{"code":6031,"name":"MissingRepayInstructions","msg":"Missing Repay Instruction"},{"code":6032,"name":"KeeperShortchanged","msg":"Keeper Shortchanged"},{"code":6033,"name":"WrongSwapOutAccount","msg":"Jup Swap to Wrong Out Account"},{"code":6034,"name":"WrongTransferAmount","msg":"Transfer amount should be exactly account balance"},{"code":6035,"name":"InsufficientBalanceForRent","msg":"Insufficient balance for rent"},{"code":6036,"name":"UnexpectedSolBalance","msg":"Unexpected SOL amount in intermediate account"},{"code":6037,"name":"InsufficientWsolForTransfer","msg":"Too little WSOL to perform transfer"},{"code":6038,"name":"MissedInstruction","msg":"Did not call initiate_flash_fill"},{"code":6039,"name":"WrongProgram","msg":"Did not call this program's initiate_flash_fill"},{"code":6040,"name":"BalanceNotZero","msg":"Can't close account with balance"},{"code":6041,"name":"UnexpectedWSOLLeftover","msg":"Should not have WSOL leftover in DCA out-token account"},{"code":6042,"name":"IntermediateAccountNotSet","msg":"Should pass in a WSOL intermediate account when transferring SOL"},{"code":6043,"name":"UnexpectedSwapInstruction","msg":"Did not call jup swap"}]}
    
    def __init__(
        self,
        async_client: AsyncClient,
        keypair: Keypair
    ):
        self.rpc = async_client
        self.keypair = keypair  
        self.dca_program = AnchorProgram(
            idl=Idl.from_json(json.dumps(self.IDL)),
            program_id=self.DCA_PROGRAM_ID,
            provider=Provider(
                connection=self.rpc,
                wallet=Wallet(payer=self.keypair),
                opts=TxOpts(skip_preflight=True, preflight_commitment=Processed)
            )
        )
    
    async def get_mint_token_program(
        self,
        token_mint: Pubkey,
    ) -> Pubkey:
        """Returns token mint token program from token mint Pubkey.
        
        Args:
            ``token_mint (Pubkey)``: Pubkey of the token mint.
            
        Returns:
            ``Pubkey (Pubkey)``: Mint token program Pubkey.
        
        Example:
            >>> rpc_url = "https://neat-hidden-sanctuary.solana-mainnet.discover.quiknode.pro/2af5315d336f9ae920028bbb90a73b724dc1bbed/"
            >>> async_client = AsyncClient(rpc_url)
            >>> private_key_string = "tSg8j3pWQyx3TC2fpN9Ud1bS0NoAK0Pa3TC2fpNd1bS0NoASg83TC2fpN9Ud1bS0NoAK0P"
            >>> private_key = Keypair.from_bytes(base58.b58decode(private_key_string))
            >>> jupiter = Jupiter(async_client, private_key)
            >>> token_mint = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
            >>> token_mint_program = await jupiter.dca.get_mint_token_program(token_mint)
            
            Pubkey(
                TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA,
            )
        """
        
        mint_token_program_info = await self.rpc.get_account_info(token_mint)
        mint_token_program = mint_token_program_info.value.owner
        return mint_token_program
        
    async def get_or_create_associated_token_address(
        self,
        token_mint: Pubkey,
    ) -> dict:
        """Returns assosciated token address Pubkey with instruction to create it if it doesn't exists.
        
        Args:
            ``token_mint (Pubkey)``: Pubkey of the token mint.
            
        Returns:
            ``Dict``: Associated token address Pubkey and instruction.
        
        Example:
            >>> rpc_url = "https://neat-hidden-sanctuary.solana-mainnet.discover.quiknode.pro/2af5315d336f9ae920028bbb90a73b724dc1bbed/"
            >>> async_client = AsyncClient(rpc_url)
            >>> private_key_string = "tSg8j3pWQyx3TC2fpN9Ud1bS0NoAK0Pa3TC2fpNd1bS0NoASg83TC2fpN9Ud1bS0NoAK0P"
            >>> private_key = Keypair.from_bytes(base58.b58decode(private_key_string))
            >>> jupiter = Jupiter(async_client, private_key)
            >>> token_mint = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
            >>> associated_token_address = await jupiter.dca.get_or_create_associated_token_address(token_mint)
            
            {'pubkey': Pubkey(
                2GWpKNsfBq7y2LS9FNpAUWsr6atnywB7JTwRrifMHzwU,
            ), 'instruction': Instruction(
                Instruction {
                    program_id: ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL,
                    accounts: [
                        AccountMeta {
                            pubkey: AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX,
                            is_signer: True,
                            is_writable: True,
                        },
                        AccountMeta {
                            pubkey: 2GWpKNsfBq7y2LS9FNpAUWsr6atnywB7JTwRrifMHzwU,
                            is_signer: False,
                            is_writable: True,
                        },
                        AccountMeta {
                            pubkey: AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX,
                            is_signer: False,
                            is_writable: False,
                        },
                        AccountMeta {
                            pubkey: EPjFWdd1ufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v,
                            is_signer: False,
                            is_writable: False,
                        },
                        AccountMeta {
                            pubkey: 11111111111111111111111111111111,
                            is_signer: False,
                            is_writable: False,
                        },
                        AccountMeta {
                            pubkey: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA,
                            is_signer: False,
                            is_writable: False,
                        },
                        AccountMeta {
                            pubkey: SysvarRent111111111111111111111111111111111,
                            is_signer: False,
                            is_writable: False,
                        },
                    ],
                    data: [],
                },
            )}
        """
        
        toAccount = get_associated_token_address(self.keypair.pubkey(), token_mint)
        accountInfo = await self.rpc.get_account_info(toAccount)
        account = accountInfo.value
        
        if account:
            instruction = None
            return {'pubkey': toAccount, 'instruction': instruction}
        else:
            instruction = create_associated_token_account(self.keypair.pubkey(), self.keypair.pubkey(), token_mint)
            return {'pubkey': toAccount, 'instruction': instruction}
    
    async def get_dca_pubkey(
        self,
        input_mint: Pubkey,
        output_mint: Pubkey,
        uid: int,
    ) -> Pubkey:
        """Returns DCA Pubkey to be created.
        
        Args:
            ``input_mint (Pubkey)``: Pubkey of the token to sell.
            ``output_mint (Pubkey)``: Pubkey of the token to buy.
            ``uid (int)``: A unix timestamp in seconds.
            
        Returns:
            ``Pubkey``: DCA Pubkey to be created.
        
        Example:
            >>> rpc_url = "https://neat-hidden-sanctuary.solana-mainnet.discover.quiknode.pro/2af5315d336f9ae920028bbb90a73b724dc1bbed/"
            >>> async_client = AsyncClient(rpc_url)
            >>> private_key_string = "tSg8j3pWQyx3TC2fpN9Ud1bS0NoAK0Pa3TC2fpNd1bS0NoASg83TC2fpN9Ud1bS0NoAK0P"
            >>> private_key = Keypair.from_bytes(base58.b58decode(private_key_string))
            >>> jupiter = Jupiter(async_client, private_key)
            >>> input_mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
            >>> output_mint = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
            >>> uid = int(time.time())
            >>> dca_pubkey = await jupiter.dca.get_dca_pubkey(input_mint, output_mint, uid)
            
            Pubkey(
                ArotVdXCEw4Zy5ywUVP7ZJBPFvXR8v8Md6jSQK9pLaCb,
            )
        """ 
            
        dcaPubKey = Pubkey.find_program_address(
            seeds=[
            b'dca',
            self.keypair.pubkey().__bytes__(),
            input_mint.__bytes__(),
            output_mint.__bytes__(),
            struct.pack("<Q", uid)
            ],
            program_id=self.DCA_PROGRAM_ID
        )
        return dcaPubKey[0]

    async def fetch_dca_data(
        self,
        dca_pubkey: Pubkey,
    ) -> Container[Any]:
        """Fetch DCA Account Anchor Data
        
        Args:
            ``dca_pubkey (Pubkey)``: Pubkey of the DCA account.
        
        Returns:
            ``Dca``: DCA Account Anchor Data
        
        Example:
            >>> rpc_url = "https://neat-hidden-sanctuary.solana-mainnet.discover.quiknode.pro/2af5315d336f9ae920028bbb90a73b724dc1bbed/"
            >>> async_client = AsyncClient(rpc_url)
            >>> private_key_string = "tSg8j3pWQyx3TC2fpN9Ud1bS0NoAK0Pa3TC2fpNd1bS0NoASg83TC2fpN9Ud1bS0NoAK0P"
            >>> private_key = Keypair.from_bytes(base58.b58decode(private_key_string))
            >>> jupiter = Jupiter(async_client, private_key)
            >>> dca_pubkey = Pubkey.from_string("45iYdjmFUHSJCQHnNpWNFF9AjvzRcsQUP9FDBvJCiNS1")
            >>> fetch_dca_data = await jupiter.dca.fetch_dca_data(dca_pubkey)
            Dca(user=Pubkey(
                AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX,
            ), input_mint=Pubkey(
                So11111111111111111111111111111111111111112,
            ), output_mint=Pubkey(
                EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v,
            ), idx=1703051020, next_cycle_at=1703052580, in_deposited=5000000, in_withdrawn=0, out_withdrawn=194361, in_used=2600000, out_received=194361, in_amount_per_cycle=100000, cycle_frequency=60, next_cycle_amount_left=100000, in_account=Pubkey(
                3NFmVtdyxQvmhXa1a82j62dd9kCmKFa3uv3vv7WRQsRY,
            ), out_account=Pubkey(
                ErFYjASdQ5HVtJoQ3dqrjp8MgFKjSjFVQiRSqBbKT9kJ,
            ), min_out_amount=0, max_out_amount=0, keeper_in_balance_before_borrow=0, dca_out_balance_before_swap=0, created_at=1703050997, bump=253)
        """ 
        dca_account_coder = AccountsCoder(idl=Idl.from_json(json.dumps(self.IDL)))
        get_dca_account_details  = await self.rpc.get_account_info(dca_pubkey)
        dca_account_details = get_dca_account_details.value.data
        dca_account_decoded_details = dca_account_coder.decode(dca_account_details)
        return dca_account_decoded_details

    async def create_dca(
        self,
        input_mint: Pubkey,
        output_mint: Pubkey,
        total_in_amount: int,
        in_amount_per_cycle: int,
        cycle_frequency: int,
        min_out_amount_per_cycle: int=None,
        max_out_amount_per_cycle: int=None,
        start_at: int=0,
        ) -> dict:
        """Setting up a DCA account with signing and sending the transaction.
        
        Args:
            ``input_mint (Pubkey)``: Pubkey of the token to sell.
            ``output_mint (Pubkey)``: Pubkey of the token to buy.
            ``total_in_amount (int)``: Total input mint amount to sell.
            ``in_amount_per_cycle (int)``: Input mint amount to sell each time. For e.g. if you are trying to buy SOL using 100 USDC every day over 10 days, in_amount_per_cycle should be 100*10**6.
            ``cycle_frequency (int)``: The number of seconds between each periodic buys. For e.g. if you are trying to DCA on a daily basis, cycle_frequency should be 60*60*24 = 86,400.
            ``min_out_amount_per_cycle (int)``: Optional field. Following the examples above, let's say you only want to buy SOL if SOL is below SOL-USDC $20, that means for each cycle, with every 100 USDC, you want to receive a minimum of 100 / 20 = 5 SOL. You can then pass 5 * LAMPORTS_PER_SOL as argument here. This ensures that you receive > 5 SOL for each order.
            ``max_out_amount_per_cycle (int)``: This is just the inverse scenario of min_out_amount_per_cycle. While max_out_amount_per_cycle is a little counter intuitive, it can be used by advanced traders / investors who believe an asset is at risk of further decline in prices if it goes beyond a certain threshold. Say in the case of output mint being a stablecoin, if the stablecoin drops to $0.5, you will get more buying into it, but that may not necessary be a good thing since the risk of a stablecoin going to $0 is very real if it could depeg to $0.5. This is where max_out_amount_per_cycle could be useful.
            ``start_at (int)``: Optional field. Unix timestamp in seconds of when you would like DCA to start. Pass 0 if you want to start immediately or pass a future time as a unix timestamp in seconds.
            
        Returns:
            ``Dict``: Transaction hash and DCA Account Pubkey.
        
        Example:
            >>> rpc_url = "https://neat-hidden-sanctuary.solana-mainnet.discover.quiknode.pro/2af5315d336f9ae920028bbb90a73b724dc1bbed/"
            >>> async_client = AsyncClient(rpc_url)
            >>> private_key_string = "tSg8j3pWQyx3TC2fpN9Ud1bS0NoAK0Pa3TC2fpNd1bS0NoASg83TC2fpN9Ud1bS0NoAK0P"
            >>> private_key = Keypair.from_bytes(base58.b58decode(private_key_string))
            >>> jupiter = Jupiter(async_client, private_key)
            >>> input_mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
            >>> output_mint = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
            >>> total_in_amount = 5_000_000
            >>> in_amount_per_cycle = 100
            >>> cycle_frequency = 60
            >>> min_out_amount_per_cycle = 0
            >>> max_out_amount_per_cycle = 0
            >>> start = 0
            >>> create_dca = await jupiter.dca.create_dca(input_mint, output_mint, total_in_amount, in_amount_per_cycle, cycle_frequency, min_out_amount_per_cycle, max_out_amount_per_cycle, start)

            {
                'dca_pubkey': Pubkey(Duop8ynu7WozpmLUsc1pAq6gobS3vdxe8GJMFzF8rY56,),
                'transaction_hash': '5zFwgyHExYcWLTgqh6GMDPML2mPHzmJUFfsVD882tYd4oGhekiDufcBZSbcoNFKxvhRLQt8WwYU4SsW8fCefYmHf'
            }
        """
        
        pre_instructions = []
        post_instructions = []
    
        input_token_program, output_token_program = await self.get_mint_token_program(input_mint), await self.get_mint_token_program(output_mint)
        user_input_account = get_associated_token_address(self.keypair.pubkey(), input_mint)
        
        if input_mint == WRAPPED_SOL_MINT:
            input_mint_ata = await self.get_or_create_associated_token_address(input_mint)
            transfer_IX = transfer(TransferParams(
                from_pubkey=self.keypair.pubkey(),
                to_pubkey=user_input_account,
                lamports=total_in_amount
            ))
            sync_native_IX = sync_native(SyncNativeParams(
                program_id=input_token_program,
                account=user_input_account
            ))
            
            if input_mint_ata['instruction']:
                pre_instructions.append(input_mint_ata['instruction'])
                post_instructions.append(close_account(
                    CloseAccountParams(
                        program_id=input_mint_ata['pubkey'],
                        account=self.keypair.pubkey(),
                        dest=self.keypair.pubkey(),
                        owner=self.keypair.pubkey()
                    )
                ))
                
            pre_instructions.append(transfer_IX)
            pre_instructions.append(sync_native_IX)
        
        if output_mint != WRAPPED_SOL_MINT:
            output_mint_ata = await self.get_or_create_associated_token_address(output_mint)
            
            if output_mint_ata['instruction']:
                pre_instructions.append(output_mint_ata['instruction'])
        
        uid = int(time.time())
        dca_pubkey = await self.get_dca_pubkey(input_mint, output_mint, uid)

        accounts = {
            'dca': dca_pubkey,
            'user': self.keypair.pubkey(),
            'payer': self.keypair.pubkey(),
            'input_mint': input_mint,
            'output_mint': output_mint,
            'user_ata': user_input_account,
            'in_ata': get_associated_token_address(dca_pubkey, input_mint),
            'out_ata': get_associated_token_address(dca_pubkey, output_mint),
            'system_program': Pubkey.from_string("11111111111111111111111111111111"),
            'token_program': Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
            'associated_token_program': Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"),
            'event_authority': Pubkey.from_string("Cspp27eGUDMXxPEdhmEXFVRn6Lt1L7xJyALF3nmnWoBj"),
            'program': self.DCA_PROGRAM_ID 
        }

        transaction = await self.dca_program.rpc['open_dca'](
            uid,
            total_in_amount,
            in_amount_per_cycle,
            cycle_frequency,
            min_out_amount_per_cycle,
            max_out_amount_per_cycle,
            start_at,
            False,
            ctx=Context(
                accounts=accounts,
                signers=[self.keypair],
                pre_instructions=pre_instructions,
                # post_instructions=post_instructions,
                options=TxOpts(skip_preflight=False, preflight_commitment=Processed)
            )
        )

        return {'dca_pubkey': dca_pubkey, 'transaction_hash': str(transaction)}

    async def close_dca(
        self,
        dca_pubkey: Pubkey,
    ) -> str:
        """Close DCA Account with signing and sending the transaction.
        
        Args:
            ``dca_pubkey (Pubkey)``: Pubkey of the DCA account to be closed.
        
        Returns:
            ``str``: transaction hash of the DCA account closed.
        
        Example:
            >>> rpc_url = "https://neat-hidden-sanctuary.solana-mainnet.discover.quiknode.pro/2af5315d336f9ae920028bbb90a73b724dc1bbed/"
            >>> async_client = AsyncClient(rpc_url)
            >>> private_key_string = "tSg8j3pWQyx3TC2fpN9Ud1bS0NoAK0Pa3TC2fpNd1bS0NoASg83TC2fpN9Ud1bS0NoAK0P"
            >>> private_key = Keypair.from_bytes(base58.b58decode(private_key_string))
            >>> jupiter = Jupiter(async_client, private_key)
            >>> dca_pubkey = Pubkey.from_string("45iYdjmFUHSJCQHnNpWNFF9AjvzRcsQUP9FDBvJCiNS1")
            >>> close_dca = await jupiter.dca.close_dca(dca_pubkey)
            HXiWtTPLjgtiuNoAN7CEfyDyftdsAnMfuQ93Yp1vukgBbdU1Lb2Bo59p48PVr7CMhxPDwGQbsfjvKT5HXXQfvE2
        """
        dca_account = await self.fetch_dca_data(dca_pubkey)
        input_mint = dca_account.input_mint
        output_mint = dca_account.output_mint
        input_token_program, output_token_program = await self.get_mint_token_program(input_mint), await self.get_mint_token_program(output_mint)
        user_input_account = get_associated_token_address(self.keypair.pubkey(), input_mint)
        user_output_account = get_associated_token_address(self.keypair.pubkey(), output_mint)
        reserve_input_account = get_associated_token_address(dca_pubkey, input_mint)
        reserve_output_account = get_associated_token_address(dca_pubkey, output_mint)
        
        accounts = {
            'user': self.keypair.pubkey(),
            'dca': dca_pubkey,
            'input_mint': input_mint,
            'output_mint': output_mint,
            'in_ata': reserve_input_account,
            'out_ata': reserve_output_account,
            'user_in_ata': user_input_account,
            'user_out_ata': user_output_account,
            'system_program': Pubkey.from_string("11111111111111111111111111111111"),
            'token_program': Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
            'associated_token_program': Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"),
            'event_authority': Pubkey.from_string("Cspp27eGUDMXxPEdhmEXFVRn6Lt1L7xJyALF3nmnWoBj"),
            'program': self.DCA_PROGRAM_ID 
        }
        transaction = await self.dca_program.rpc['close_dca'](
            ctx=Context(
                accounts=accounts,
                signers=[self.keypair],
                # pre_instructions=pre_instructions,
                # post_instructions=post_instructions,
                options=TxOpts(skip_preflight=False, preflight_commitment=Processed)
            )
        )
        return str(transaction)

    @staticmethod
    async def fetch_user_dca_accounts(
        wallet_address: str,
        status: int
    ) -> dict:
        """Returns all DCA Accounts from a wallet address

        Args:
            ``wallet_address (str)``: Wallet address.
            ``status (int)``: 0 = DCA Running | 1 = DCA Done
                
        Returns:
            ``dict``: all DCA Accounts from the wallet address.

        Example:
            >>> wallet_address = "AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX"
            >>> status = 0
            >>> user_dca_accounts = await Jupiter_DCA.fetch_user_dca_accounts(wallet_address, status)
        {
            'ok': True,
            'data': {
                'dcaAccounts': [
                    {
                        'id': 202513,
                        'createdAt': '2023-12-18T12:39:40.000Z',
                        'updatedAt': '2023-12-18T12:39:42.265Z',
                        'userKey': 'AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX',
                        'dcaKey': 'FTG9eN99uJJBqBtcz1bR6pGfj2Pb3yNAZmGYXggcAgio',
                        'inputMint': 'So11111111111111111111111111111111111111112',
                        'outputMint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
                        'inDeposited': '1000000',
                        'inAmountPerCycle': '100',
                        'cycleFrequency': '60',
                        'closeTxHash': '',
                        'openTxHash': '2bwo4ds3Xpiwr9gLptXVFTcxnz2rP9pu3fAppNn3E61g33tprBCy6X8PT3SaXMn7fpG2c5CRw1LWGMEz3ik5SgnP',
                        'status': 0,
                        'inWithdrawn': '0',
                        'outWithdrawn': '0',
                        'unfilledAmount': '1000000',
                        'userClosed': False, 
                        'fills': []
                    }
                ]
            }
        }
        """
        user_dca_accounts = httpx.get(f"https://dca-api.jup.ag/user/{wallet_address}/dca?status={status}", timeout=Timeout(timeout=30.0)).json()
        return user_dca_accounts
    
    @staticmethod
    async def fetch_dca_account_fills_history(
        dca_account_address: str,
    ) -> dict:
        """Returns all DCA Account fills history

        Args:
            ``dca_account_address (str)``: DCA Account address.
                
        Returns:
            ``dict``: all DCA Account fills history.

        Example:
            >>> dca_account_address = "C91FGJAvQgeaXka1exMihC5qChwdcJzFemFVQutv4dev"
            >>> dca_account_fills_history = await Jupiter_DCA.fetch_dca_fills_history(dca_account_address)
        {
            'ok': True,
            'data': {
                'fills': [
                    {
                        'userKey': 'AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX',
                        'dcaKey': 'C91FGJAvQgeaXka1exMihC5qChwdcJzFemFVQutv4dev',
                        'inputMint': 'So11111111111111111111111111111111111111112', 
                        'outputMint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
                        'inAmount': '100000',
                        'outAmount': '7540',
                        'feeMint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
                        'fee': '7',
                        'txId': '48kC4ZnkPpiRc6T3eVKYghmUERa2geC2e9FvGbVjDMaNkbrDJ3tj36GMkNdi1AkXkqrAHoDZcLW5SFjQEZcKB2NB',
                        'confirmedAt': 1703055843
                    }
                ]
            }
        }    
        """
        dca_account_fills_history = httpx.get(f"https://dca-api.jup.ag/dca/{dca_account_address}/fills", timeout=Timeout(timeout=30.0)).json()
        return dca_account_fills_history
          
    @staticmethod
    async def get_available_dca_tokens(
    ) -> list:
        """Get available tokens for DCA.
        
        Returns:
            ``list``: all available tokens from https://cache.jup.ag/top-tokens
        
        Example:
            >>> available_dca_tokens = await Jupiter_DCA.get_available_dca_tokens()
        """
        available_dca_tokens = httpx.get(f"https://cache.jup.ag/top-tokens", timeout=Timeout(timeout=30.0)).json()
        return available_dca_tokens
    
class Jupiter():
    
    ENDPOINT_APIS_URL = {
        "QUOTE": "https://quote-api.jup.ag/v6/quote?",
        "SWAP": "https://quote-api.jup.ag/v6/swap",
        "OPEN_ORDER": "https://jup.ag/api/limit/v1/createOrder",
        "CANCEL_ORDERS": "https://jup.ag/api/limit/v1/cancelOrders",
        "QUERY_OPEN_ORDERS": "https://jup.ag/api/limit/v1/openOrders?wallet=",
        "QUERY_ORDER_HISTORY": "https://jup.ag/api/limit/v1/orderHistory",
        "QUERY_TRADE_HISTORY": "https://jup.ag/api/limit/v1/tradeHistory"
    }
    
    def __init__(
        self,
        async_client: AsyncClient,
        keypair: Keypair,
        quote_api_url: str="https://quote-api.jup.ag/v6/quote?",
        swap_api_url: str="https://quote-api.jup.ag/v6/swap",
        open_order_api_url: str="https://jup.ag/api/limit/v1/createOrder",
        cancel_orders_api_url: str="https://jup.ag/api/limit/v1/cancelOrders",
        query_open_orders_api_url: str="https://jup.ag/api/limit/v1/openOrders?wallet=",
        query_order_history_api_url: str="https://jup.ag/api/limit/v1/orderHistory",
        query_trade_history_api_url: str="https://jup.ag/api/limit/v1/tradeHistory",
    ):
        self.dca = Jupiter_DCA(async_client, keypair)
        self.rpc = async_client
        self.keypair = keypair
        
        self.ENDPOINT_APIS_URL["QUOTE"] = quote_api_url
        self.ENDPOINT_APIS_URL["SWAP"] = swap_api_url
        self.ENDPOINT_APIS_URL["OPEN_ORDER"] = open_order_api_url
        self.ENDPOINT_APIS_URL["CANCEL_ORDERS"] = cancel_orders_api_url
        self.ENDPOINT_APIS_URL["QUERY_OPEN_ORDERS"] = query_open_orders_api_url
        self.ENDPOINT_APIS_URL["QUERY_ORDER_HISTORY"] = query_order_history_api_url
        self.ENDPOINT_APIS_URL["QUERY_TRADE_HISTORY"] = query_trade_history_api_url
    
    async def quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int=None,
        swap_mode: str="ExactIn",
        only_direct_routes: bool=False,
        as_legacy_transaction: bool=False,
        exclude_dexes: list=None,
        max_accounts: int=None,
        platform_fee_bps: int=None
    ) -> dict:
        """Get the best swap route for a token trade pair sorted by largest output token amount from https://quote-api.jup.ag/v6/quote
        
        Args:
            Required:
                ``input_mint (str)``: Input token mint address\n
                ``output_mint (str)``: Output token mint address\n
                ``amount (int)``: The API takes in amount in integer and you have to factor in the decimals for each token by looking up the decimals for that token. For example, USDC has 6 decimals and 1 USDC is 1000000 in integer when passing it in into the API.\n
            Optionals:
                ``slippage_bps (int)``: The slippage % in BPS. If the output token amount exceeds the slippage then the swap transaction will fail.\n
                ``swap_mode (str)``: (ExactIn or ExactOut) Defaults to ExactIn. ExactOut is for supporting use cases where you need an exact token amount, like payments. In this case the slippage is on the input token.\n
                ``only_direct_routes (bool)``: Default is False. Direct Routes limits Jupiter routing to single hop routes only.\n
                ``as_legacy_transaction (bool)``: Default is False. Instead of using versioned transaction, this will use the legacy transaction.\n
                ``exclude_dexes (list)``: Default is that all DEXes are included. You can pass in the DEXes that you want to exclude in a list. For example, ['Aldrin','Saber'].\n
                ``max_accounts (int)``: Find a route given a maximum number of accounts involved, this might dangerously limit routing ending up giving a bad price. The max is an estimation and not the exact count.\n
                ``platform_fee_bps (int)``: If you want to charge the user a fee, you can specify the fee in BPS. Fee % is taken out of the output token.
        
        Returns:
            ``dict``: returns best swap route
            
        Example:
            >>> rpc_url = "https://neat-hidden-sanctuary.solana-mainnet.discover.quiknode.pro/2af5315d336f9ae920028bbb90a73b724dc1bbed/"
            >>> async_client = AsyncClient(rpc_url)
            >>> private_key_string = "tSg8j3pWQyx3TC2fpN9Ud1bS0NoAK0Pa3TC2fpNd1bS0NoASg83TC2fpN9Ud1bS0NoAK0P"
            >>> private_key = Keypair.from_bytes(base58.b58decode(private_key_string))
            >>> jupiter = Jupiter(async_client, private_key)
            >>> input_mint = "So11111111111111111111111111111111111111112"
            >>> output_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            >>> amount = 5_000_000
            >>> quote = await jupiter.quote(input_mint, output_mint, amount)
            {
                'inputMint': 'So11111111111111111111111111111111111111112',
                'inAmount': '5000000',
                'outputMint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
                'outAmount': '353237',
                'otherAmountThreshold':'351471',
                'swapMode': 'ExactIn',
                'slippageBps': 50,
                'platformFee': None,
                'priceImpactPct': '0',
                'routePlan': [{'swapInfo': {'ammKey': 'Cx8eWxJAaCQAFVmv1mP7B2cVie2BnkR7opP8vUh23Wcr', 'label': 'Lifinity V2', 'inputMint': 'So11111111111111111111111111111111111111112', 'outputMint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'inAmount': '5000000', 'outAmount': '353237', 'feeAmount': '1000', 'feeMint': 'So11111111111111111111111111111111111111112'}, 'percent': 100}],
                'contextSlot': 236625263,
                'timeTaken': 0.069434356}
        """
        
        quote_url = self.ENDPOINT_APIS_URL['QUOTE'] + "inputMint=" + input_mint + "&outputMint=" + output_mint + "&amount=" + str(amount) + "&swapMode=" + swap_mode + "&onlyDirectRoutes=" + str(only_direct_routes).lower() + "&asLegacyTransaction=" + str(as_legacy_transaction).lower()
        if slippage_bps:
            quote_url += "&slippageBps=" + str(slippage_bps)
        if exclude_dexes:
            quote_url += "&excludeDexes=" + ','.join(exclude_dexes)
        if max_accounts:
            quote_url += "&maxAccounts=" + str(max_accounts)
        if platform_fee_bps:
            quote_url += "&plateformFeeBps=" + platform_fee_bps
        
        quote_response = httpx.get(url=quote_url).json()
        try:
            quote_response['routePlan']
            return quote_response
        except:
            raise Exception(quote_response['error'])

    async def swap(
        self,
        input_mint: str,
        output_mint: str,
        amount: int=0,
        quoteResponse: str=None,
        wrap_unwrap_sol: bool=True,
        slippage_bps: int=1,
        swap_mode: str="ExactIn",
        prioritization_fee_lamports: int=None,
        only_direct_routes: bool=False,
        as_legacy_transaction: bool=False,
        exclude_dexes: list=None,
        max_accounts: int=None,
        platform_fee_bps: int=None
    ) -> str:
        """Perform a swap.
        
        Args:
            Required:
                ``input_mint (str)``: Input token mint str\n
                ``output_mint (str)``: Output token mint str\n
                ``amount (int)``: The API takes in amount in integer and you have to factor in the decimals for each token by looking up the decimals for that token. For example, USDC has 6 decimals and 1 USDC is 1000000 in integer when passing it in into the API.\n
            Optionals:
                ``prioritizationFeeLamports (int)``: If transactions are expiring without confirmation on-chain, this might mean that you have to pay additional fees to prioritize your transaction. To do so, you can set the prioritizationFeeLamports parameter.\n
                ``wrap_unwrap_sol (bool)``: Auto wrap and unwrap SOL. Default is True.\n
                ``slippage_bps (int)``: The slippage % in BPS. If the output token amount exceeds the slippage then the swap transaction will fail.\n
                ``swap_mode (str)``: (ExactIn or ExactOut) Defaults to ExactIn. ExactOut is for supporting use cases where you need an exact token amount, like payments. In this case the slippage is on the input token.\n
                ``only_direct_routes (bool)``: Default is False. Direct Routes limits Jupiter routing to single hop routes only.\n
                ``as_legacy_transaction (bool)``: Default is False. Instead of using versioned transaction, this will use the legacy transaction.\n
                ``exclude_dexes (list)``: Default is that all DEXes are included. You can pass in the DEXes that you want to exclude in a list. For example, ['Aldrin','Saber'].\n
                ``max_accounts (int)``: Find a route given a maximum number of accounts involved, this might dangerously limit routing ending up giving a bad price. The max is an estimation and not the exact count.\n
                ``platform_fee_bps (int)``: If you want to charge the user a fee, you can specify the fee in BPS. Fee % is taken out of the output token.
        
        Returns:
            ``str``: returns serialized transactions to perform the swap from https://quote-api.jup.ag/v6/swap
            
        Example:
            >>> rpc_url = "https://neat-hidden-sanctuary.solana-mainnet.discover.quiknode.pro/2af5315d336f9ae920028bbb90a73b724dc1bbed/"
            >>> async_client = AsyncClient(rpc_url)
            >>> private_key_string = "tSg8j3pWQyx3TC2fpN9Ud1bS0NoAK0Pa3TC2fpNd1bS0NoASg83TC2fpN9Ud1bS0NoAK0P"
            >>> private_key = Keypair.from_bytes(base58.b58decode(private_key_string))
            >>> jupiter = Jupiter(async_client, private_key)
            >>> input_mint = "So11111111111111111111111111111111111111112"
            >>> output_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            >>> amount = 5_000_000
            >>> transaction_data = await jupiter.swap(user_public_key, input_mint, output_mint, amount)
            AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAQAJDpQzg6Gwmq0Gtgp4+LWUVz0yQOAuHGNJAGTs0dcqEMVCoh2aSWdVMvcatcojrWtwXATiOw7/o5hE7NFuy3p8vgLfsLhf7Ff9NofcPgIyAbMytm5ggTyKwmR+JqgXUXARVfefILshj4ZhFSjUfRpiSI47mVNFUq9v5NOOCWSEZJZM/GHGfBesEb9blQsf7DnKodziY279S/OPkZf0/OalnPEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMGRm/lIRcy/+ytunLDm+e8jOW7xfcSayxDmzpAAAAABHnVW/IxwG7udMVuzmgVB/2xst6j9I5RArHNola8E48Gm4hX/quBhPtof2NGGMA12sQ53BrrO1WYoPAAAAAAAQbd9uHXZaGT2cvhRs7reawctIXtX1s3kTqM9YV+/wCpT0tsDkEI/SpqJHjq4KzFnbIbtO31EcFiz2AtHgwJAfuMlyWPTiSJ8bs9ECkUjg2DC1oTmdr/EIQEjnvY2+n4WbQ/+if11/ZKdMCbHylYed5LCas238ndUUsyGqezjOXoxvp6877brTo9ZfNqq8l0MbG75MLS9uDkfKYCA0UvXWHmraeknnR8/memFAZWZHeDMQG7C5ZFLxolWUniPl6SYgcGAAUCwFwVAAYACQNIDQAAAAAAAAsGAAMACAUJAQEFAgADDAIAAAAgTgAAAAAAAAkBAwERBx8JCgADAQIECA0HBwwHGREBAhUOFxMWDxIQFAoYCQcHJMEgmzNB1pyBBwEAAAATZAABIE4AAAAAAACHBQAAAAAAADIAAAkDAwAAAQkB1rO1s+JVEuIRoGsE8f2MlAkFWssCkimIonlHpLV2w4gKBwKRTE0SjIeLSwIICg==
        """
        
        if quoteResponse is None:
            quoteResponse = await self.quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=amount,
            slippage_bps=slippage_bps,
            swap_mode=swap_mode,
            only_direct_routes=only_direct_routes,
            as_legacy_transaction=as_legacy_transaction,
            exclude_dexes=exclude_dexes,
            max_accounts=max_accounts,
            platform_fee_bps=platform_fee_bps
            )
        transaction_parameters = {
            "quoteResponse": quoteResponse,
            "userPublicKey": self.keypair.pubkey().__str__(),
            "wrapAndUnwrapSol": wrap_unwrap_sol
        }
        if prioritization_fee_lamports:
            transaction_parameters.update({"prioritizationFeeLamports": prioritization_fee_lamports})
        transaction_data = httpx.post(url=self.ENDPOINT_APIS_URL['SWAP'], json=transaction_parameters).json()
        return transaction_data['swapTransaction']

    async def open_order(
        self,
        input_mint: str,
        output_mint: str,
        in_amount: int=0,
        out_amount: int=0,
        expired_at: int=None
    ) -> dict:
        """Open an order.
        
        Args:
            Required:
                ``input_mint (str)``: Input token mint address\n
                ``output_mint (str)``: Output token mint address\n
                ``in_amount (int)``: The API takes in amount in integer and you have to factor in the decimals for each token by looking up the decimals for that token. For example, USDC has 6 decimals and 1 USDC is 1000000 in integer when passing it in into the API.\n
                ``out_amount (int)``: The API takes in amount in integer and you have to factor in the decimals for each token by looking up the decimals for that token. For example, USDC has 6 decimals and 1 USDC is 1000000 in integer when passing it in into the API.\n
            Optionals:
                ``expired_at (int)``: Deadline for when the limit order expires. It can be either None or Unix timestamp in seconds.
        Returns:
            ``dict``: transaction_data and signature2 in order to create the limit order.
            
        Example:
            >>> rpc_url = "https://neat-hidden-sanctuary.solana-mainnet.discover.quiknode.pro/2af5315d336f9ae920028bbb90a73b724dc1bbed/"
            >>> async_client = AsyncClient(rpc_url)
            >>> private_key_string = "tSg8j3pWQyx3TC2fpN9Ud1bS0NoAK0Pa3TC2fpNd1bS0NoASg83TC2fpN9Ud1bS0NoAK0P"
            >>> private_key = Keypair.from_bytes(base58.b58decode(private_key_string))
            >>> jupiter = Jupiter(async_client, private_key)
            >>> input_mint = "So11111111111111111111111111111111111111112"
            >>> output_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            >>> in_amount = 5_000_000
            >>> out_amount = 100_000
            >>> transaction_data = await jupiter.open_order(user_public_key, input_mint, output_mint, in_amount, out_amount)
            {
                'transaction_data': 'AgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgEGC5Qzg6Gwmq0Gtgp4+LWUVz0yQOAuHGNJAGTs0dcqEMVCBvqBKhFi2uRFEKYI4zPatxbdm7DylvnQUby9MexSmeAdsqhWUMQ86Ddz4+7pQFooE6wLglATS/YvzOVUNMOqnyAmC8Ioh9cSvEZniys4XY0OyEvxe39gSdHqlHWJQUPMn4prs0EwIc9JznmgzyMliG5PJTvaFYw75ssASGlB2gMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAImg/TLoYktlelMGKAi4mA0icnTD92092qSZhd3wNABMCv4fVqQvV1OYZ3a3bH43JpI5pIln+UAHnO1fyDJwCfIGm4hX/quBhPtof2NGGMA12sQ53BrrO1WYoPAAAAAAAQan1RcZLFxRIYzJTD1K8X9Y2u4Im6H9ROPb2YoAAAAABt324ddloZPZy+FGzut5rBy0he1fWzeROoz1hX7/AKmr+pT0gdwb1ZeE73qr11921UvCtCB3MMpBcLaiY8+u7QEHDAEABAMCCAIHBgUKCRmFbkqvcJ/1nxAnAAAAAAAAECcAAAAAAAAA',
                'signature2': Signature(
                    2Pip6gx9FLGVqmRqfAgwJ8HEuCY8ZbUbVERR18vHyxFngSi3Jxq8Vkpm74hS5zq7RAM6tqGUAkf3ufCBsxGXZrUC,)
            }
        """
        
        keypair = Keypair()
        transaction_parameters = {
            "owner": self.keypair.pubkey().__str__(),
            "inputMint": input_mint,
            "outputMint": output_mint,
            "outAmount": out_amount,
            "inAmount": in_amount,
            "base": keypair.pubkey().__str__()
        }
        if expired_at:
            transaction_parameters['expiredAt'] = expired_at
        transaction_data = httpx.post(url=self.ENDPOINT_APIS_URL['OPEN_ORDER'], json=transaction_parameters).json()['tx']
        raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
        signature2 = keypair.sign_message(message.to_bytes_versioned(raw_transaction.message))
        return {"transaction_data": transaction_data, "signature2": signature2}

    async def cancel_orders(
        self,
        orders: list=[]
    ) -> str:
        """Cancel open orders from a list (max. 10).
        
        Args:
            Required:!:
                ``orders (list)``: List of orders to be cancelled.
        Returns:
            ``str``: returns serialized transactions to cancel orders from https://jup.ag/api/limit/v1/cancelOrders
        
        Example:
            >>> rpc_url = "https://neat-hidden-sanctuary.solana-mainnet.discover.quiknode.pro/2af5315d336f9ae920028bbb90a73b724dc1bbed/"
            >>> async_client = AsyncClient(rpc_url)
            >>> private_key_string = "tSg8j3pWQyx3TC2fpN9Ud1bS0NoAK0Pa3TC2fpNd1bS0NoASg83TC2fpN9Ud1bS0NoAK0P"
            >>> private_key = Keypair.from_bytes(base58.b58decode(private_key_string))
            >>> jupiter = Jupiter(async_client, private_key)
            >>> list_orders = [item['publicKey'] for item in await jupiter.query_open_orders()] # Cancel all open orders
            >>> transaction_data = await jupiter.cancel_orders(orders=openOrders)
            AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAQIlDODobCarQa2Cnj4tZRXPTJA4C4cY0kAZOzR1yoQxUIklPdDonxNd5JDfdYoHE56dvNBQ1SLN90fFZxvVlzZr9DPwpfbd+ANTB35SSvHYVViD27UZR578oC2faxJea7y958guyGPhmEVKNR9GmJIjjuZU0VSr2/k044JZIRklkwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAr+H1akL1dTmGd2t2x+NyaSOaSJZ/lAB5ztX8gycAnyBpuIV/6rgYT7aH9jRhjANdrEOdwa6ztVmKDwAAAAAAEG3fbh12Whk9nL4UbO63msHLSF7V9bN5E6jPWFfv8AqW9ZjNTy3JS6YYFodCWqtWH80+eLPmN4igHrkYHIsdQfAQUHAQIAAwQHBghfge3wCDHfhA==
        """
        
        transaction_parameters = {
            "owner": self.keypair.pubkey().__str__(),
            "feePayer": self.keypair.pubkey().__str__(), 
            "orders": orders
        }
        transaction_data = httpx.post(url=self.ENDPOINT_APIS_URL['CANCEL_ORDERS'], json=transaction_parameters).json()['tx']
        return transaction_data

    @staticmethod
    async def query_open_orders(
        wallet_address: str,
        input_mint: str=None,
        output_mint: str=None
    ) -> list:
        """     
        Query open orders from self.keypair public address.
        
        Args:
            Required:
                ``wallet_address (str)``: Wallet address.
            Optionals:
                ``input_mint (str)``: Input token mint address.
                ``output_mint (str)``: Output token mint address.
        Returns:
            ``list``: returns open orders list from https://jup.ag/api/limit/v1/openOrders
            
        Example:
            >>> list_open_orders = await Jupiter.query_open_orders("AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX")
            [
                {   
                    'publicKey': '3ToRYxxMHN3CHkbqWHcbXBCBLNqmDeLoubGGfNKGSCDL',
                    'account': {
                        'maker': 'AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX',
                        'inputMint': 'So11111111111111111111111111111111111111112',
                        'outputMint': 'AGFEad2et2ZJif9jaGpdMixQqvW5i81aBdvKe7PHNfz3',
                        'oriInAmount': '10000',
                        'oriOutAmount': '10000',
                        'inAmount': '10000',
                        'outAmount': '10000',
                        'expiredAt': None,
                        'base': 'FghAhphJkhT74PXFQAz3QKqGVGA72Y2gUeVHU7QRw31c'
                    }
                }
            ]      
        """
        
        query_openorders_url = "https://jup.ag/api/limit/v1/openOrders?wallet=" + wallet_address
        if input_mint:
            query_openorders_url += "inputMint=" + input_mint
        if output_mint:
            query_openorders_url += "outputMint" + output_mint
            
        list_open_orders = httpx.get(query_openorders_url, timeout=Timeout(timeout=30.0)).json()
        return list_open_orders

    @staticmethod
    async def query_orders_history(
        wallet_address: str,
        cursor: int=None,
        skip: int=None,
        take: int=None
    ) -> list:
        """
        Query orders history from self.keypair public address.
        
        Args:
            Required:
                ``wallet_address (str)``: Wallet address.
            Optionals:
                ``cursor (int)``: Pointer to a specific result in the data set.
                ``skip (int)``: Number of records to skip from the beginning.
                ``take (int)``: Number of records to retrieve from the current position.
        Returns:
            ``list``: returns open orders list from https://jup.ag/api/limit/v1/orderHistory
            
        Example:
            >>> list_orders_history = await Jupiter.query_orders_history("AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX")
            [
                {
                    'id': 1639144,
                    'orderKey': '3ToRYxxMHN3CHkbqWHcbXBCBLNqmDeLoubGGfNKGSCDL',
                    'maker': 'AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX',
                    'inputMint': 'So11111111111111111111111111111111111111112',
                    'outputMint': 'AGFEad2et2ZJif9jaGpdMixQqvW5i81aBdvKe7PHNfz3',
                    'inAmount': '10000',
                    'oriInAmount': '10000',
                    'outAmount': '10000',
                    'oriOutAmount': '10000',
                    'expiredAt': None,
                    'state': 'Cancelled',
                    'createTxid': '4CYy8wZG2aRPctL9do7UBzaK9w4EDLJxGkkU1EEAx4LYNYW7j7Kyet2vL4q6cKK7HbJNHp6QXzLQftpTiDdhtyfL',
                    'cancelTxid': '83eN6Lm41t2VWUchm1T6hWX2qK3sf39XzPGbxV9s2WjBZfdUADQdRGg2Y1xAKn4igMJU1xRPCTgUhnm6qFUPWRc',
                    'updatedAt': '2023-12-18T15:55:30.617Z',
                    'createdAt': '2023-12-18T15:29:34.000Z'
                }
            ]
        """
        
        query_orders_history_url = "https://jup.ag/api/limit/v1/orderHistory" + "?wallet=" + wallet_address
        if cursor:
            query_orders_history_url += "?cursor=" + str(cursor)
        if skip:
            query_orders_history_url += "?skip=" + str(skip)
        if take:
            query_orders_history_url += "?take=" + str(take)
            
        list_orders_history = httpx.get(query_orders_history_url, timeout=Timeout(timeout=30.0)).json()
        return list_orders_history

    @staticmethod
    async def query_trades_history(
        wallet_address: str,
        input_mint: str=None,
        output_mint: str=None,
        cursor: int=None,
        skip: int=None,
        take: int=None
    ) -> list:
        """
        Query trades history from a public address.
        
        Args:
            Required:
                ``wallet_address (str)``: Wallet address.
            Optionals:
                ``input_mint (str)``: Input token mint address.
                ``output_mint (str)``: Output token mint address.
                ``cursor (int)``: Pointer to a specific result in the data set.
                ``skip (int)``: Number of records to skip from the beginning.
                ``take (int)``: Number of records to retrieve from the current position.
        Returns:
            ``list``: returns trades history list from https://jup.ag/api/limit/v1/tradeHistory
        
        Example:
            >>> list_trades_history = await Jupiter.query_trades_history("AyWu89SjZBW1MzkxiREmgtyMKxSkS1zVy8Uo23RyLphX")
            [
                {
                    'id': 10665592,
                    'inAmount':
                    '10000000',
                    'outAmount': '675870652',
                    'txid': '5rmA1S5MDAVdRYWeVgUWYFp6pYuy5vwrYpRJUJdhjoWnuuheeg1YwqK6P5H6u4tv99cUwQttSBYm6kjSNHJGENgb',
                    'updatedAt': '2023-12-13T15:39:04.800Z',
                    'createdAt': '2023-12-13T15:37:08.000Z',
                    'order': {
                        'id': 1278268,
                        'orderKey': '3bGykFCMWPNQDTRVBdKBbZuVHqNB5z5XaphkRHLWYmE5',
                        'inputMint': 'So11111111111111111111111111111111111111112',
                        'outputMint': '8XSsNvaKU9FDhYWAv7Yc7qSNwuJSzVrXBNEk7AFiWF69'
                    }
                }
            ]
        """
        
        query_tradeHistoryUrl = "https://jup.ag/api/limit/v1/tradeHistory" + "?wallet=" + wallet_address
        if input_mint:
            query_tradeHistoryUrl += "inputMint=" + input_mint
        if output_mint:
            query_tradeHistoryUrl += "outputMint" + output_mint
        if cursor:
            query_tradeHistoryUrl += "?cursor=" + cursor
        if skip:
            query_tradeHistoryUrl += "?skip=" + skip
        if take:
            query_tradeHistoryUrl += "?take=" + take
            
        tradeHistory = httpx.get(query_tradeHistoryUrl, timeout=Timeout(timeout=30.0)).json()
        return tradeHistory
    
    @staticmethod
    async def get_indexed_route_map(
    ) -> dict:
        """
        Retrieve an indexed route map for all the possible token pairs you can swap between.

        Returns:
            ``dict``: indexed route map for all the possible token pairs you can swap betwee from https://quote-api.jup.ag/v6/indexed-route-map
        
        Example:
            >>> indexed_route_map = await Jupiter.get_indexed_route_map()
        """
        
        indexed_route_map = httpx.get("https://quote-api.jup.ag/v6/indexed-route-map", timeout=Timeout(timeout=30.0)).json()
        return indexed_route_map

    @staticmethod
    async def get_tokens_list(
        list_type: str="strict",
        banned_tokens: bool=False
    ) -> dict:
        """
        The Jupiter Token List API is an open, collaborative, and dynamic token list to make trading on Solana more transparent and safer for users and developers.\n
        There are two types of list:\n
        ``strict``\n
            - Only tokens that are tagged "old-registry", "community", or "wormhole" verified.\n
            - No unknown and banned tokens.\n
        ``all``\n
            - Everything including unknown/untagged tokens that are picked up automatically.\n
            - It does not include banned tokens by default.\n
            - Often, projects notice that the token got banned and withdraw liquidity. As our lists are designed for trading, banned tokens that used to, but no longer meet our minimum liquidity requirements will not appear in this response.
        
        Args:
            Optionals:
                ``list_type (str)``: Default is "strict" (strict/all).
                ``banned_tokens (bool)``: Only if list_type is "all"
        Returns:
            ``dict``: indexed route map for all the possible token pairs you can swap betwee from https://token.jup.ag/{list_type}
        
        Example:
        >>> tokens_list = await Jupiter.get_tokens_list()
        """
        
        tokens_list_url = "https://token.jup.ag/"  + list_type
        if banned_tokens is True:
            tokens_list_url +=  "?includeBanned=true"
        tokens_list = httpx.get(tokens_list_url, timeout=Timeout(timeout=30.0)).json()
        return tokens_list

    @staticmethod
    async def get_all_tickers(
    ) -> dict:
        """Returns all tickers (cached for every 2-5 mins) from https://stats.jup.ag/coingecko/tickers

        Returns:
            ``dict``: all tickers(cached for every 2-5 mins)

        Example:
            >>> all_tickers_list = await Jupiter.get_all_tickers()
        """
        all_tickers_list = httpx.get("https://stats.jup.ag/coingecko/tickers", timeout=Timeout(timeout=30.0)).json()
        return all_tickers_list

    @staticmethod
    async def get_all_swap_pairs(
    ) -> dict:
        """Returns all swap pairs (cached for every 2-5 mins) from https://stats.jup.ag/coingecko/pairs

        Returns:
            ``dict``: all swap pairs

        Example:
            >>> all_swap_pairs_list = await Jupiter.get_all_swap_pairs()
        """
        all_swap_pairs_list = httpx.get("https://stats.jup.ag/coingecko/pairs", timeout=Timeout(timeout=30.0)).json()
        return all_swap_pairs_list

    @staticmethod
    async def get_swap_pairs(
        input_mint: str,
        output_mint: str,
    ) -> dict:
        """Returns swap pairs for input token and output token
        
        Args:
            Required:
                ``input_mint (str)``: Input token mint address.\n
                ``output_mint (str)``: Output token mint address.\n

        Returns:
            ``dict``: all swap pairs for input token and output token

        Example:
            >>> swap_pairs_list = await Jupiter.get_swap_pairs("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        """
        swap_pairs_url = "https://stats.jup.ag/coingecko/tickers?ticker_id=" + input_mint + "_" + output_mint
        swap_pairs_list = httpx.get(swap_pairs_url, timeout=Timeout(timeout=30.0)).json()
        return swap_pairs_list
    
    @staticmethod
    async def get_token_stats_by_date(
        token: str,
        date: str,
    ) -> list:
        """Returns swap pairs for input token and output token
        
        Args:
            Required:
                ``token (str)``: Input token mint address.\n
                ``date (str)``: YYYY-MM-DD format date.\n
                
        Returns:
            ``list``: all swap pairs for input token and output token

        Example:
            >>> token_stats_by_date = await Jupiter.get_swap_pairs("B5mW68TkDewnKvWNc2trkmmdSRxcCjZz3Yd9BWxQTSRU", "2022-04-1")
        """
        token_stats_by_date_url = "https://stats.jup.ag/token-ledger/" + token + "/" + date
        token_stats_by_date = httpx.get(token_stats_by_date_url, timeout=Timeout(timeout=30.0)).json()
        return token_stats_by_date

    @staticmethod
    async def get_jupiter_stats(
        unit_of_time: str,
    ) -> dict:
        """Stats for the unit of time specified.
        
        Args:
            Required:
                ``unit_of_time (str)``: Unit of time: day/week/month
                
        Returns:
            ``dict``: stats for the unit of time specified.

        Example:
            >>> jupiter_stats = await Jupiter.get_jupiter_stats("day")
        """
        jupiter_stats_url = "https://stats.jup.ag/info/" + unit_of_time
        jupiter_stats = httpx.get(jupiter_stats_url, timeout=Timeout(timeout=30.0)).json()
        return jupiter_stats

    @staticmethod
    async def get_token_price(
        input_mint: str,
        output_mint: str=None,
    ) -> dict:
        """The Jupiter Price API aims to make getting precise and real-time pricing for all SPL tokens as powerful and simple as possible.
        
        Args:
            Required:
                ``input_mint (str)``: Input token mint name or address.
            Optionals:
                ``output_mint (str)``: Output token mint name or address.
                
        Returns:
            ``dict``: id, mintSymbol, vsToken, vsTokenSymbol, price, timeTaken

        Example:
            >>> token_price = await Jupiter.get_jupiter_stats("So11111111111111111111111111111111111111112", "USDC")
        {
            'So11111111111111111111111111111111111111112': {
                'id': 'So11111111111111111111111111111111111111112',
                'mintSymbol': 'SOL',
                'vsToken': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
                'vsTokenSymbol': 'USDC',
                'price': 71.893496709
            }
        }
        """
        token_prices_url = "https://price.jup.ag/v4/price?ids=" + input_mint
        if output_mint:
            token_prices_url += "&vsToken=" + output_mint
        token_prices = httpx.get(token_prices_url, timeout=Timeout(timeout=30.0)).json()['data']
        return token_prices

    @staticmethod
    async def program_id_to_label(
    ) -> dict:
        """Returns a dict, which key is the program id and value is the label.\n
        This is used to help map error from transaction by identifying the fault program id.\n
        With that, we can use the exclude_dexes or dexes parameter for swap.

        Returns:
            ``dict``: program_id and label

        Example:
            >>> program_id_to_label_list = await Jupiter.program_id_to_label()
        """
        program_id_to_label_list = httpx.get("https://quote-api.jup.ag/v6/program-id-to-label", timeout=Timeout(timeout=30.0)).json()
        return program_id_to_label_list

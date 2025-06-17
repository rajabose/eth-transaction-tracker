from typing import List, Dict, Any
from datetime import datetime
from web3 import Web3
from config.config import TRANSACTION_TYPES

class TransactionProcessor:
    def __init__(self):
        self.w3 = Web3()

    def process_normal_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """Process a normal ETH transaction."""
        return {
            'Transaction Hash': tx['hash'],
            'Date & Time': datetime.fromtimestamp(int(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S'),
            'From Address': tx['from'],
            'To Address': tx['to'],
            'Transaction Type': TRANSACTION_TYPES['EXTERNAL'],
            'Asset Contract Address': '',
            'Asset Symbol/Name': 'ETH',
            'Token ID': '',
            'Value/Amount': self.w3.from_wei(int(tx['value']), 'ether'),
            'Gas Fee (ETH)': self.w3.from_wei(int(tx['gasPrice']) * int(tx['gasUsed']), 'ether')
        }

    def process_internal_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """Process an internal transaction."""
        return {
            'Transaction Hash': tx['hash'],
            'Date & Time': datetime.fromtimestamp(int(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S'),
            'From Address': tx['from'],
            'To Address': tx['to'],
            'Transaction Type': TRANSACTION_TYPES['INTERNAL'],
            'Asset Contract Address': '',
            'Asset Symbol/Name': 'ETH',
            'Token ID': '',
            'Value/Amount': self.w3.from_wei(int(tx['value']), 'ether'),
            'Gas Fee (ETH)': '0'  # Internal transactions don't have gas fees
        }

    def process_erc20_transfer(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """Process an ERC-20 token transfer."""
        return {
            'Transaction Hash': tx['hash'],
            'Date & Time': datetime.fromtimestamp(int(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S'),
            'From Address': tx['from'],
            'To Address': tx['to'],
            'Transaction Type': TRANSACTION_TYPES['ERC20'],
            'Asset Contract Address': tx['contractAddress'],
            'Asset Symbol/Name': tx['tokenSymbol'],
            'Token ID': '',
            'Value/Amount': int(tx['value']) / (10 ** int(tx['tokenDecimal'])),
            'Gas Fee (ETH)': self.w3.from_wei(int(tx['gasPrice']) * int(tx['gasUsed']), 'ether')
        }

    def process_erc721_transfer(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """Process an ERC-721 NFT transfer."""
        return {
            'Transaction Hash': tx['hash'],
            'Date & Time': datetime.fromtimestamp(int(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S'),
            'From Address': tx['from'],
            'To Address': tx['to'],
            'Transaction Type': TRANSACTION_TYPES['ERC721'],
            'Asset Contract Address': tx['contractAddress'],
            'Asset Symbol/Name': tx['tokenName'],
            'Token ID': tx['tokenID'],
            'Value/Amount': '1',  # NFTs are always 1 unit
            'Gas Fee (ETH)': self.w3.from_wei(int(tx['gasPrice']) * int(tx['gasUsed']), 'ether')
        }

    def process_erc1155_transfer(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """Process an ERC-1155 token transfer."""
        return {
            'Transaction Hash': tx['hash'],
            'Date & Time': datetime.fromtimestamp(int(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S'),
            'From Address': tx['from'],
            'To Address': tx['to'],
            'Transaction Type': TRANSACTION_TYPES['ERC1155'],
            'Asset Contract Address': tx['contractAddress'],
            'Asset Symbol/Name': tx['tokenName'],
            'Token ID': tx['tokenID'],
            'Value/Amount': tx['tokenValue'],
            'Gas Fee (ETH)': self.w3.from_wei(int(tx['gasPrice']) * int(tx['gasUsed']), 'ether')
        }

    def process_contract_interaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """Process a contract interaction transaction."""
        return {
            'Transaction Hash': tx['hash'],
            'Date & Time': datetime.fromtimestamp(int(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S'),
            'From Address': tx['from'],
            'To Address': tx['to'],
            'Transaction Type': TRANSACTION_TYPES['CONTRACT'],
            'Asset Contract Address': tx['to'],
            'Asset Symbol/Name': 'Contract Interaction',
            'Token ID': '',
            'Value/Amount': self.w3.from_wei(int(tx['value']), 'ether'),
            'Gas Fee (ETH)': self.w3.from_wei(int(tx['gasPrice']) * int(tx['gasUsed']), 'ether')
        }

import requests
import time
from typing import List, Dict, Any
from config.config import ETHERSCAN_API_KEY, ETHERSCAN_API_URL

class EtherscanAPI:
    def __init__(self):
        self.api_key = ETHERSCAN_API_KEY
        self.base_url = ETHERSCAN_API_URL
        self.rate_limit_delay = 0.2  # 200ms delay between requests

    def _make_request(self, module: str, action: str, **params) -> Dict[str, Any]:
        """Make a request to the Etherscan API with rate limiting."""
        params.update({
            'module': module,
            'action': action,
            'apikey': self.api_key
        })
        
        time.sleep(self.rate_limit_delay)  # Rate limiting
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data['status'] == '0' and data['message'] != 'No transactions found':
            raise Exception(f"Etherscan API error: {data['message']}")
        
        return data

    def get_normal_transactions(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict[str, Any]]:
        """Get normal transactions for an address."""
        data = self._make_request(
            'account',
            'txlist',
            address=address,
            startblock=start_block,
            endblock=end_block,
            sort='asc'
        )
        return data.get('result', [])

    def get_internal_transactions(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict[str, Any]]:
        """Get internal transactions for an address."""
        data = self._make_request(
            'account',
            'txlistinternal',
            address=address,
            startblock=start_block,
            endblock=end_block,
            sort='asc'
        )
        return data.get('result', [])

    def get_erc20_transfers(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict[str, Any]]:
        """Get ERC-20 token transfers for an address."""
        data = self._make_request(
            'account',
            'tokentx',
            address=address,
            startblock=start_block,
            endblock=end_block,
            sort='asc'
        )
        return data.get('result', [])

    def get_erc721_transfers(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict[str, Any]]:
        """Get ERC-721 token transfers for an address."""
        data = self._make_request(
            'account',
            'tokennfttx',
            address=address,
            startblock=start_block,
            endblock=end_block,
            sort='asc'
        )
        return data.get('result', [])

    def get_erc1155_transfers(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict[str, Any]]:
        """Get ERC-1155 token transfers for an address."""
        data = self._make_request(
            'account',
            'token1155tx',
            address=address,
            startblock=start_block,
            endblock=end_block,
            sort='asc'
        )
        return data.get('result', [])

    def get_contract_abi(self, contract_address: str) -> str:
        """Get the ABI for a contract address."""
        data = self._make_request(
            'contract',
            'getabi',
            address=contract_address
        )
        return data.get('result', '')

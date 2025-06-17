import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')

# API Endpoints
ETHERSCAN_API_URL = 'https://api.etherscan.io/api'
ALCHEMY_API_URL = f'https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}'

# Pagination and Rate Limiting
PAGE_SIZE = 5000  # Maximum transactions per page for Etherscan
MAX_RETRIES = 3    # Maximum number of retries for failed requests
RATE_LIMIT_DELAY = 0.2  # Delay between API calls in seconds
BATCH_SIZE = 1000  # Number of transactions to process in memory at once

# Transaction Types
TRANSACTION_TYPES = {
    'EXTERNAL': 'External Transfer',
    'INTERNAL': 'Internal Transfer',
    'ERC20': 'ERC-20 Token Transfer',
    'ERC721': 'ERC-721 NFT Transfer',
    'ERC1155': 'ERC-1155 Token Transfer',
    'CONTRACT': 'Contract Interaction',
    'FAILED': 'Failed Transaction'
}

# CSV Output Configuration
CSV_COLUMNS = [
    'Transaction Hash',
    'Date & Time',
    'From Address',
    'To Address',
    'Transaction Type',
    'Asset Contract Address',
    'Asset Symbol/Name',
    'Token ID',
    'Value/Amount',
    'Gas Fee (ETH)'
]

# File Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
TEMP_DIR = os.path.join(DATA_DIR, 'temp')

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

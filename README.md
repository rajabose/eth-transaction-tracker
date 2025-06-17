# Ethereum Transaction Tracker

A Python script that retrieves and exports Ethereum wallet transaction history to a structured CSV file.

## Features

- Fetches all types of Ethereum transactions:
  - External (Normal) Transfers
  - Internal Transfers
  - ERC-20 Token Transfers
  - ERC-721 NFT Transfers
- Exports transaction data to CSV with detailed information
- Supports both Etherscan and Alchemy APIs
- Handles large transaction volumes

## Prerequisites

- Python 3.9 or higher
- Etherscan API key
- Alchemy API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd eth-transaction-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with:
```
ETHERSCAN_API_KEY=your_etherscan_api_key
ALCHEMY_API_KEY=your_alchemy_api_key
```

## Usage

Run the script using the provided shell script:
```bash
./start.sh <ethereum_address>
```

Example:
```bash
./start.sh 0x742d35Cc6634C0532925a3b844Bc454e4438f44e
```

The script will:
1. Fetch all transactions for the provided address
2. Process and categorize the transactions
3. Save the results to a CSV file in the `data/output` directory

## Output Format

The generated CSV file includes the following fields:
- Transaction Hash
- Date & Time
- From Address
- To Address
- Transaction Type
- Asset Contract Address
- Asset Symbol/Name
- Token ID
- Value/Amount
- Gas Fee (ETH)

## Docker Support

You can also run the application using Docker:

1. Build the Docker image:
```bash
docker build -t eth-transaction-tracker .
```

2. Run the container:
```bash
docker run --rm -v $(pwd)/data:/app/data eth-transaction-tracker <ethereum_address>
```

## Notes

- The script handles pagination automatically for large transaction histories
- Transaction data is fetched from Etherscan API
- Gas fees are calculated in ETH
- Token amounts are automatically converted using the correct decimal places

## License

MIT License

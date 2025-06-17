import os
import sys
import json
import time
import requests
from datetime import datetime
import pandas as pd
from web3 import Web3
from eth_utils import to_checksum_address
from config.config import (
    ETHERSCAN_API_KEY,
    ALCHEMY_API_KEY,
    ETHERSCAN_API_URL,
    ALCHEMY_API_URL,
    TRANSACTION_TYPES,
    CSV_COLUMNS,
    OUTPUT_DIR,
    TEMP_DIR,
    PAGE_SIZE,
    MAX_RETRIES,
    RATE_LIMIT_DELAY,
    BATCH_SIZE
)

class TransactionTracker:
    def __init__(self, address):
        self.address = to_checksum_address(address)
        self.transactions = []
        self.is_large_address = False
        self.transaction_count = 0

    def make_api_request(self, url, params, retry_count=0):
        """Make API request with retry logic and rate limiting."""
        try:
            time.sleep(RATE_LIMIT_DELAY)
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == '1':
                return data['result']
            elif data['message'] == 'NOTOK' and retry_count < MAX_RETRIES:
                print(f"API error, retrying... (attempt {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(RATE_LIMIT_DELAY * 2)
                return self.make_api_request(url, params, retry_count + 1)
            else:
                print(f"Error: {data['message']}")
                return []
        except Exception as e:
            if retry_count < MAX_RETRIES:
                print(f"Request failed, retrying... (attempt {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(RATE_LIMIT_DELAY * 2)
                return self.make_api_request(url, params, retry_count + 1)
            print(f"Error fetching data: {str(e)}")
            return []

    def fetch_transactions(self, action, tx_type):
        """Fetch transactions with pagination."""
        transactions = []
        page = 1
        offset = 1000  # Reduced from 5000 to handle pagination better
        
        while True:
            params = {
                'module': 'account',
                'action': action,
                'address': self.address,
                'startblock': 0,
                'endblock': 99999999,
                'page': page,
                'offset': offset,
                'sort': 'desc',
                'apikey': ETHERSCAN_API_KEY
            }
            
            batch = self.make_api_request(ETHERSCAN_API_URL, params)
            if not batch:
                break
                
            for tx in batch:
                tx['tx_type'] = tx_type
            transactions.extend(batch)
            
            print(f"Fetched {len(transactions)} {tx_type} transactions...")
            
            # Check if this is a large address
            if len(transactions) > 10000 and not self.is_large_address:
                self.is_large_address = True
                print("Large address detected. Switching to batch processing mode...")
            
            # If we got less than the offset, we've reached the end
            if len(batch) < offset:
                break
            
            # Check if we've hit the Etherscan limit
            if page * offset >= 10000:
                print(f"Reached Etherscan's pagination limit for {tx_type} transactions.")
                print("Switching to block-based pagination...")
                
                # Get the last block number from the current batch
                last_block = int(batch[-1]['blockNumber'])
                
                # Continue fetching with block-based pagination
                while True:
                    params['startblock'] = last_block + 1
                    params['page'] = 1  # Reset page number
                    
                    batch = self.make_api_request(ETHERSCAN_API_URL, params)
                    if not batch:
                        break
                        
                    for tx in batch:
                        tx['tx_type'] = tx_type
                    transactions.extend(batch)
                    
                    print(f"Fetched {len(transactions)} {tx_type} transactions...")
                    
                    if len(batch) < offset:
                        break
                    
                    last_block = int(batch[-1]['blockNumber'])
                
                break
            
            page += 1
        
        return transactions

    def get_all_transactions(self):
        """Fetch all types of transactions."""
        print(f"Fetching transactions for address: {self.address}")
        
        # Fetch different types of transactions
        self.transactions.extend(self.fetch_transactions('txlist', 'EXTERNAL'))
        self.transactions.extend(self.fetch_transactions('txlistinternal', 'INTERNAL'))
        self.transactions.extend(self.fetch_transactions('tokentx', 'ERC20'))
        self.transactions.extend(self.fetch_transactions('tokennfttx', 'ERC721'))
        
        self.transaction_count = len(self.transactions)
        print(f"Found {self.transaction_count} total transactions")
        
        return self.transactions

    def process_transaction(self, tx):
        """Process a single transaction."""
        try:
            timestamp = datetime.fromtimestamp(int(tx['timeStamp']))
            tx_type = tx.get('tx_type', 'EXTERNAL')
            
            processed_tx = {
                'Transaction Hash': tx['hash'],
                'Date & Time': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'From Address': tx['from'],
                'To Address': tx['to'],
                'Transaction Type': TRANSACTION_TYPES.get(tx_type, tx_type),
                'Asset Contract Address': '',
                'Asset Symbol/Name': 'ETH',
                'Token ID': '',
                'Value/Amount': float(tx['value']) / 1e18,
                'Gas Fee (ETH)': float(tx.get('gasPrice', 0)) * float(tx.get('gasUsed', 0)) / 1e18
            }
            
            if tx_type == 'ERC20':
                processed_tx.update({
                    'Asset Contract Address': tx['contractAddress'],
                    'Asset Symbol/Name': tx.get('tokenSymbol', ''),
                    'Value/Amount': float(tx['value']) / (10 ** int(tx.get('tokenDecimal', 18)))
                })
            elif tx_type == 'ERC721':
                processed_tx.update({
                    'Asset Contract Address': tx['contractAddress'],
                    'Asset Symbol/Name': tx.get('tokenName', ''),
                    'Token ID': tx.get('tokenID', '')
                })
            
            return processed_tx
        except Exception as e:
            print(f"Error processing transaction {tx.get('hash', 'unknown')}: {str(e)}")
            return None

    def process_transactions(self):
        """Process all transactions based on volume."""
        if not self.transactions:
            print("No transactions to process.")
            return None

        if self.is_large_address:
            return self.process_large_transactions()
        else:
            return self.process_small_transactions()

    def process_small_transactions(self):
        """Process transactions for small addresses (in memory)."""
        processed_data = []
        for tx in self.transactions:
            processed_tx = self.process_transaction(tx)
            if processed_tx:
                processed_data.append(processed_tx)
        return processed_data

    def process_large_transactions(self):
        """Process transactions for large addresses (in batches)."""
        processed_data = []
        total_batches = (self.transaction_count + BATCH_SIZE - 1) // BATCH_SIZE
        
        for i in range(0, self.transaction_count, BATCH_SIZE):
            batch = self.transactions[i:i + BATCH_SIZE]
            print(f"Processing batch {i//BATCH_SIZE + 1}/{total_batches}")
            
            for tx in batch:
                processed_tx = self.process_transaction(tx)
                if processed_tx:
                    processed_data.append(processed_tx)
            
            # Save batch to temporary file
            if processed_data:
                batch_file = os.path.join(TEMP_DIR, f'batch_{i//BATCH_SIZE}.csv')
                df = pd.DataFrame(processed_data, columns=CSV_COLUMNS)
                df.to_csv(batch_file, index=False)
                processed_data = []  # Clear memory
        
        return TEMP_DIR

    def save_transactions(self, data):
        """Save processed transactions to CSV."""
        if not data:
            print("No transactions to save.")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(OUTPUT_DIR, f"transactions_{self.address}_{timestamp}.csv")
        
        if self.is_large_address:
            self.merge_csv_files(data, output_file)
        else:
            df = pd.DataFrame(data, columns=CSV_COLUMNS)
            df['Date & Time'] = pd.to_datetime(df['Date & Time'])
            df = df.sort_values('Date & Time', ascending=False)
            df.to_csv(output_file, index=False)
        
        print(f"Transactions saved to: {output_file}")

    def merge_csv_files(self, temp_dir, output_file):
        """Merge all temporary CSV files into a single output file."""
        all_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith('.csv')]
        
        if not all_files:
            print("No data to merge.")
            return
        
        dfs = [pd.read_csv(f) for f in all_files]
        final_df = pd.concat(dfs, ignore_index=True)
        
        final_df['Date & Time'] = pd.to_datetime(final_df['Date & Time'])
        final_df = final_df.sort_values('Date & Time', ascending=False)
        final_df.to_csv(output_file, index=False)
        
        # Clean up temporary files
        for f in all_files:
            os.remove(f)

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <ethereum_address>")
        sys.exit(1)
    
    address = sys.argv[1]
    tracker = TransactionTracker(address)
    
    # Get and process transactions
    tracker.get_all_transactions()
    processed_data = tracker.process_transactions()
    tracker.save_transactions(processed_data)

if __name__ == "__main__":
    main()

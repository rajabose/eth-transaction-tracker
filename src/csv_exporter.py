import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from config.config import CSV_COLUMNS, OUTPUT_DIR

class CSVExporter:
    def __init__(self):
        self.columns = CSV_COLUMNS

    def export_transactions(self, transactions: List[Dict[str, Any]], address: str) -> str:
        """Export transactions to a CSV file."""
        # Create DataFrame
        df = pd.DataFrame(transactions, columns=self.columns)
        
        # Sort by date
        df['Date & Time'] = pd.to_datetime(df['Date & Time'])
        df = df.sort_values('Date & Time')
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"transactions_{address}_{timestamp}.csv"
        filepath = f"{OUTPUT_DIR}/{filename}"
        
        # Export to CSV
        df.to_csv(filepath, index=False)
        
        return filepath

    def merge_transaction_lists(self, *transaction_lists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge multiple transaction lists into one."""
        all_transactions = []
        for tx_list in transaction_lists:
            all_transactions.extend(tx_list)
        return all_transactions

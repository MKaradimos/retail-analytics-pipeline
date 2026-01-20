"""
CSV data ingestion module - loads sales transaction data from CSV files.
"""
import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from config import DATA_DIR
from models import SalesTransactionModel

logger = logging.getLogger(__name__)


class CSVIngestion:
    """Handles data ingestion from CSV files."""
    
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
    
    def load_sales_transactions(self, filename: str = 'sales_transactions.csv') -> List[Dict[str, Any]]:
        """
        Load and validate sales transactions from CSV file.
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            List of validated transaction dictionaries
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        try:
            logger.info(f"Loading transactions from {filepath}")
            
            # Read CSV with appropriate dtypes
            df = pd.read_csv(
                filepath,
                parse_dates=['transaction_date'],
                dtype={
                    'transaction_id': str,
                    'product_id': int,
                    'customer_id': str,
                    'quantity': int,
                    'store_location': str,
                    'payment_method': str
                }
            )
            
            logger.info(f"Loaded {len(df)} transactions from CSV")
            
            # Validate data
            validated_transactions = self._validate_transactions(df)
            logger.info(f"Validated {len(validated_transactions)} transactions")
            
            return validated_transactions
            
        except Exception as e:
            logger.error(f"Failed to load CSV file: {e}")
            raise
    
    def _validate_transactions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Validate transaction data using Pydantic models.
        
        Args:
            df: DataFrame with transaction data
            
        Returns:
            List of validated transaction dictionaries
        """
        validated = []
        errors = []
        
        for idx, row in df.iterrows():
            try:
                transaction = SalesTransactionModel(**row.to_dict())
                validated.append(transaction.model_dump())
            except Exception as e:
                errors.append({
                    'row': idx,
                    'transaction_id': row.get('transaction_id', 'unknown'),
                    'error': str(e)
                })
                logger.warning(f"Validation failed for row {idx}: {e}")
        
        if errors:
            logger.warning(f"Failed to validate {len(errors)} transactions")
            # Log first few errors for debugging
            for error in errors[:5]:
                logger.warning(f"  Row {error['row']}: {error['error']}")
        
        return validated
    
    def load_customer_data(self, filename: str = 'customers.csv') -> List[Dict[str, Any]]:
        """
        Load customer dimension data from CSV file.
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            List of customer dictionaries
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            logger.warning(f"Customer file not found: {filepath}")
            return []
        
        try:
            df = pd.read_csv(filepath, parse_dates=['registration_date'])
            logger.info(f"Loaded {len(df)} customers from CSV")
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Failed to load customer data: {e}")
            return []


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    ingestion = CSVIngestion()
    
    # This will fail if no CSV exists - that's ok for testing
    try:
        transactions = ingestion.load_sales_transactions()
        print(f"Successfully loaded {len(transactions)} transactions")
    except FileNotFoundError:
        print("No CSV file found - this is expected for initial setup")

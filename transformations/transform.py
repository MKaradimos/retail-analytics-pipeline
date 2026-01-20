"""
Data transformation module - transforms raw data into warehouse-ready format.
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class DataTransformer:
    """Handles data transformations for warehouse loading."""
    
    @staticmethod
    def transform_products_to_dimension(products: List[Dict]) -> List[tuple]:
        """
        Transform API product data to dimension table format.
        
        Args:
            products: List of validated product dictionaries
            
        Returns:
            List of tuples ready for database insertion
        """
        transformed = []
        
        for product in products:
            try:
                row = (
                    product['product_id'],
                    product['title'],
                    product['category'],
                    product.get('description', 'No description'),
                    product['price'],
                    product.get('image_url'),
                    datetime.now()  # loaded_at
                )
                transformed.append(row)
            except KeyError as e:
                logger.warning(f"Missing key in product transformation: {e}")
        
        logger.info(f"Transformed {len(transformed)} products for dimension table")
        return transformed
    
    @staticmethod
    def transform_transactions_to_fact(transactions: List[Dict]) -> List[tuple]:
        """
        Transform transaction data to fact table format.
        
        Args:
            transactions: List of validated transaction dictionaries
            
        Returns:
            List of tuples ready for database insertion
        """
        transformed = []
        
        for txn in transactions:
            try:
                # Extract date components for time dimension
                txn_date = txn['transaction_date']
                
                row = (
                    txn['transaction_id'],
                    txn['product_id'],
                    txn['customer_id'],
                    txn_date,
                    txn_date.date(),  # date_key
                    txn['quantity'],
                    txn['unit_price'],
                    txn['total_amount'],
                    txn['store_location'],
                    txn['payment_method'],
                    datetime.now()  # loaded_at
                )
                transformed.append(row)
            except KeyError as e:
                logger.warning(f"Missing key in transaction transformation: {e}")
        
        logger.info(f"Transformed {len(transformed)} transactions for fact table")
        return transformed
    
    @staticmethod
    def extract_customer_dimension(transactions: List[Dict]) -> List[tuple]:
        """
        Extract unique customers from transaction data.
        
        Args:
            transactions: List of validated transaction dictionaries
            
        Returns:
            List of unique customer tuples
        """
        customers = {}
        
        for txn in transactions:
            customer_id = txn['customer_id']
            if customer_id not in customers:
                # In real scenario, would enrich with additional customer data
                customers[customer_id] = (
                    customer_id,
                    f"Customer {customer_id}",  # placeholder name
                    None,  # email
                    txn['store_location'],  # use store location as proxy
                    'Unknown',  # country
                    txn['transaction_date'],  # first_transaction_date
                    datetime.now()  # loaded_at
                )
        
        logger.info(f"Extracted {len(customers)} unique customers")
        return list(customers.values())
    
    @staticmethod
    def calculate_aggregations(transactions: List[Dict]) -> Dict[str, Any]:
        """
        Calculate summary statistics for logging and validation.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Dictionary with aggregated metrics
        """
        if not transactions:
            return {}
        
        total_revenue = sum(Decimal(str(t['total_amount'])) for t in transactions)
        total_quantity = sum(t['quantity'] for t in transactions)
        unique_customers = len(set(t['customer_id'] for t in transactions))
        unique_products = len(set(t['product_id'] for t in transactions))
        
        aggregations = {
            'total_transactions': len(transactions),
            'total_revenue': float(total_revenue),
            'total_quantity': total_quantity,
            'unique_customers': unique_customers,
            'unique_products': unique_products,
            'avg_transaction_value': float(total_revenue / len(transactions))
        }
        
        logger.info(f"Aggregations: {aggregations}")
        return aggregations


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    
    # Sample data
    sample_products = [
        {
            'product_id': 1,
            'title': 'Test Product',
            'category': 'electronics',
            'price': Decimal('29.99')
        }
    ]
    
    transformer = DataTransformer()
    result = transformer.transform_products_to_dimension(sample_products)
    print(f"Transformed {len(result)} products")

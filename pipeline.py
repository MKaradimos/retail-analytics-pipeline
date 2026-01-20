"""
Main pipeline orchestrator - runs the complete ETL process.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import LOGS_DIR, PIPELINE_CONFIG
from database import db
from ingestion import APIIngestion, CSVIngestion
from transformations import DataTransformer

# Configure logging
logging.basicConfig(
    level=getattr(logging, PIPELINE_CONFIG['log_level']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / f'pipeline_{datetime.now():%Y%m%d_%H%M%S}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class RetailAnalyticsPipeline:
    """Main pipeline orchestrator."""
    
    def __init__(self):
        self.api_ingestion = APIIngestion()
        self.csv_ingestion = CSVIngestion()
        self.transformer = DataTransformer()
        self.stats = {
            'products_loaded': 0,
            'customers_loaded': 0,
            'transactions_loaded': 0,
            'errors': []
        }
    
    def initialize_database(self):
        """Initialize database schema."""
        logger.info("=" * 60)
        logger.info("STEP 1: Initializing database schema")
        logger.info("=" * 60)
        
        try:
            schema_file = Path(__file__).parent / 'sql' / 'schema.sql'
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            db.execute_script(schema_sql)
            logger.info("✓ Database schema initialized successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to initialize database: {e}")
            self.stats['errors'].append(f"Database initialization: {e}")
            return False
    
    def load_products(self):
        """Load product dimension from API."""
        logger.info("=" * 60)
        logger.info("STEP 2: Loading product dimension from API")
        logger.info("=" * 60)
        
        try:
            # Fetch from API
            products = self.api_ingestion.fetch_products()
            
            if not products:
                logger.warning("No products fetched from API")
                return False
            
            # Transform
            transformed = self.transformer.transform_products_to_dimension(products)
            
            # Load to database
            insert_query = """
                INSERT INTO dim_product 
                (product_id, product_name, category, description, unit_price, image_url, loaded_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) 
                DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    category = EXCLUDED.category,
                    description = EXCLUDED.description,
                    unit_price = EXCLUDED.unit_price,
                    image_url = EXCLUDED.image_url,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            rows_affected = db.execute_many(insert_query, transformed)
            self.stats['products_loaded'] = rows_affected
            
            logger.info(f"✓ Loaded {rows_affected} products to dimension table")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to load products: {e}")
            self.stats['errors'].append(f"Product loading: {e}")
            return False
    
    def load_transactions(self):
        """Load transactions from CSV and populate fact table."""
        logger.info("=" * 60)
        logger.info("STEP 3: Loading transactions from CSV")
        logger.info("=" * 60)
        
        try:
            # Load from CSV
            transactions = self.csv_ingestion.load_sales_transactions()
            
            if not transactions:
                logger.warning("No transactions loaded from CSV")
                return False
            
            # Calculate aggregations for logging
            aggregations = self.transformer.calculate_aggregations(transactions)
            logger.info(f"Transaction summary: {aggregations}")
            
            # Extract and load customers first
            customers = self.transformer.extract_customer_dimension(transactions)
            
            customer_query = """
                INSERT INTO dim_customer 
                (customer_id, customer_name, email, city, country, first_transaction_date, loaded_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (customer_id) DO NOTHING
            """
            
            customers_loaded = db.execute_many(customer_query, customers)
            self.stats['customers_loaded'] = customers_loaded
            logger.info(f"✓ Loaded {customers_loaded} customers to dimension table")
            
            # Transform and load transactions
            transformed = self.transformer.transform_transactions_to_fact(transactions)
            
            transaction_query = """
                INSERT INTO fact_sales 
                (transaction_id, product_id, customer_id, transaction_timestamp, 
                 date_key, quantity, unit_price, total_amount, store_location, 
                 payment_method, loaded_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (transaction_id) DO NOTHING
            """
            
            rows_affected = db.execute_many(transaction_query, transformed)
            self.stats['transactions_loaded'] = rows_affected
            
            logger.info(f"✓ Loaded {rows_affected} transactions to fact table")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to load transactions: {e}")
            self.stats['errors'].append(f"Transaction loading: {e}")
            return False
    
    def validate_data_quality(self):
        """Run data quality checks."""
        logger.info("=" * 60)
        logger.info("STEP 4: Validating data quality")
        logger.info("=" * 60)
        
        checks = []
        
        try:
            # Check 1: Verify all foreign keys
            orphan_check = """
                SELECT COUNT(*) as orphan_count
                FROM fact_sales f
                LEFT JOIN dim_product p ON f.product_id = p.product_id
                WHERE p.product_id IS NULL
            """
            result = db.execute_query(orphan_check)
            orphan_count = result[0]['orphan_count']
            checks.append(('Orphan product references', orphan_count == 0))
            
            # Check 2: Verify no negative amounts
            negative_check = """
                SELECT COUNT(*) as negative_count
                FROM fact_sales
                WHERE total_amount < 0
            """
            result = db.execute_query(negative_check)
            negative_count = result[0]['negative_count']
            checks.append(('No negative amounts', negative_count == 0))
            
            # Check 3: Verify date consistency
            date_check = """
                SELECT COUNT(*) as invalid_dates
                FROM fact_sales
                WHERE date_key != DATE(transaction_timestamp)
            """
            result = db.execute_query(date_check)
            invalid_dates = result[0]['invalid_dates']
            checks.append(('Date consistency', invalid_dates == 0))
            
            # Display results
            for check_name, passed in checks:
                status = "✓ PASS" if passed else "✗ FAIL"
                logger.info(f"{status}: {check_name}")
            
            all_passed = all(passed for _, passed in checks)
            return all_passed
            
        except Exception as e:
            logger.error(f"✗ Data quality validation failed: {e}")
            return False
    
    def generate_summary(self):
        """Generate pipeline execution summary."""
        logger.info("=" * 60)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("=" * 60)
        
        try:
            # Get summary statistics
            summary_query = """
                SELECT 
                    (SELECT COUNT(*) FROM dim_product) as product_count,
                    (SELECT COUNT(*) FROM dim_customer) as customer_count,
                    (SELECT COUNT(*) FROM fact_sales) as transaction_count,
                    (SELECT SUM(total_amount) FROM fact_sales) as total_revenue
            """
            
            result = db.execute_query(summary_query)[0]
            
            logger.info(f"Products in warehouse: {result['product_count']}")
            logger.info(f"Customers in warehouse: {result['customer_count']}")
            logger.info(f"Transactions in warehouse: {result['transaction_count']}")
            logger.info(f"Total revenue: ${result['total_revenue']:,.2f}")
            
            if self.stats['errors']:
                logger.warning(f"Errors encountered: {len(self.stats['errors'])}")
                for error in self.stats['errors']:
                    logger.warning(f"  - {error}")
            else:
                logger.info("✓ No errors encountered")
                
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
    
    def run(self):
        """Execute the complete pipeline."""
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("RETAIL ANALYTICS PIPELINE - STARTING")
        logger.info(f"Execution time: {start_time}")
        logger.info("=" * 60)
        
        # Execute pipeline steps
        steps = [
            ('Initialize Database', self.initialize_database),
            ('Load Products', self.load_products),
            ('Load Transactions', self.load_transactions),
            ('Validate Data Quality', self.validate_data_quality)
        ]
        
        for step_name, step_func in steps:
            success = step_func()
            if not success:
                logger.error(f"Pipeline failed at step: {step_name}")
                break
        
        # Generate summary
        self.generate_summary()
        
        # Calculate duration
        duration = datetime.now() - start_time
        logger.info("=" * 60)
        logger.info(f"PIPELINE COMPLETED - Duration: {duration}")
        logger.info("=" * 60)


def main():
    """Main entry point."""
    pipeline = RetailAnalyticsPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()

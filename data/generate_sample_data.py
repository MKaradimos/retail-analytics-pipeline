"""
Generate sample sales transaction data for testing.
"""
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
NUM_TRANSACTIONS = 500
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

# Sample data
STORES = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
PAYMENT_METHODS = ['cash', 'credit_card', 'debit_card', 'online']
PRODUCT_IDS = list(range(1, 21))  # Assuming 20 products from API

# Sample prices for products
PRODUCT_PRICES = {
    1: 109.95, 2: 22.30, 3: 55.99, 4: 15.99, 5: 695.00,
    6: 168.00, 7: 9.99, 8: 10.99, 9: 64.00, 10: 109.00,
    11: 29.95, 12: 12.99, 13: 599.00, 14: 39.99, 15: 56.00,
    16: 29.95, 17: 39.99, 18: 9.85, 19: 7.95, 20: 12.99
}


def random_date(start, end):
    """Generate a random datetime between start and end."""
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86400)
    return start + timedelta(days=random_days, seconds=random_seconds)


def generate_transaction_id():
    """Generate a unique transaction ID."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = random.randint(1000, 9999)
    return f"TXN-{timestamp}-{random_suffix}"


def generate_customer_id():
    """Generate a customer ID."""
    return f"CUST-{random.randint(1000, 9999)}"


def generate_transactions(num_transactions):
    """Generate sample transaction data."""
    transactions = []
    
    # Create some repeat customers (80% chance of using existing customer)
    customers = [generate_customer_id() for _ in range(num_transactions // 3)]
    
    for _ in range(num_transactions):
        # Use existing customer 80% of the time
        if random.random() < 0.8 and customers:
            customer_id = random.choice(customers)
        else:
            customer_id = generate_customer_id()
            customers.append(customer_id)
        
        product_id = random.choice(PRODUCT_IDS)
        unit_price = PRODUCT_PRICES.get(product_id, 29.99)
        quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
        total_amount = round(unit_price * quantity, 2)
        
        transaction = {
            'transaction_id': generate_transaction_id(),
            'product_id': product_id,
            'customer_id': customer_id,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': total_amount,
            'transaction_date': random_date(START_DATE, END_DATE),
            'store_location': random.choice(STORES),
            'payment_method': random.choice(PAYMENT_METHODS)
        }
        
        transactions.append(transaction)
    
    return pd.DataFrame(transactions)


def main():
    """Generate and save sample data."""
    print(f"Generating {NUM_TRANSACTIONS} sample transactions...")
    
    df = generate_transactions(NUM_TRANSACTIONS)
    
    # Sort by date
    df = df.sort_values('transaction_date')
    
    # Save to CSV
    output_dir = Path(__file__).parent.parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'sales_transactions.csv'
    df.to_csv(output_file, index=False)
    
    print(f"✓ Generated {len(df)} transactions")
    print(f"✓ Date range: {df['transaction_date'].min()} to {df['transaction_date'].max()}")
    print(f"✓ Unique customers: {df['customer_id'].nunique()}")
    print(f"✓ Total revenue: ${df['total_amount'].sum():,.2f}")
    print(f"✓ Saved to: {output_file}")
    
    # Display sample
    print("\nSample transactions:")
    print(df.head(10).to_string())


if __name__ == "__main__":
    main()

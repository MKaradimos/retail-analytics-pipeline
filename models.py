"""
Data validation models for ingestion pipeline.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductModel(BaseModel):
    """Validation model for product data from API."""
    
    product_id: int = Field(..., alias='id')
    title: str
    price: Decimal
    category: str
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, alias='image')
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    class Config:
        populate_by_name = True


class SalesTransactionModel(BaseModel):
    """Validation model for sales transaction data from CSV."""
    
    transaction_id: str
    product_id: int
    customer_id: str
    quantity: int
    unit_price: Decimal
    total_amount: Decimal
    transaction_date: datetime
    store_location: str
    payment_method: str
    
    @validator('quantity')
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v
    
    @validator('unit_price', 'total_amount')
    def amounts_positive(cls, v):
        if v < 0:
            raise ValueError('Amount cannot be negative')
        return v
    
    @validator('payment_method')
    def valid_payment_method(cls, v):
        valid_methods = ['cash', 'credit_card', 'debit_card', 'online']
        if v.lower() not in valid_methods:
            raise ValueError(f'Invalid payment method. Must be one of: {valid_methods}')
        return v.lower()


class CustomerModel(BaseModel):
    """Validation model for customer dimension data."""
    
    customer_id: str
    customer_name: str
    email: Optional[str] = None
    city: Optional[str] = None
    country: str = 'Unknown'
    registration_date: datetime
    
    @validator('email')
    def email_format(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

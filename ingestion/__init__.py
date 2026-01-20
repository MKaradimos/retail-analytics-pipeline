"""
Ingestion package - handles data loading from external sources.
"""
from .api_ingestion import APIIngestion
from .csv_ingestion import CSVIngestion

__all__ = ['APIIngestion', 'CSVIngestion']

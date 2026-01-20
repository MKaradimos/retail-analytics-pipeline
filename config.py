"""
Configuration management for the retail analytics pipeline.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'retail_analytics'),
    'user': os.getenv('DB_USER', 'analytics_user'),
    'password': os.getenv('DB_PASSWORD', 'change_me_in_production')
}

# API configuration
API_CONFIG = {
    'base_url': os.getenv('API_BASE_URL', 'https://fakestoreapi.com'),
    'timeout': 30,
    'retry_attempts': 3
}

# Pipeline configuration
PIPELINE_CONFIG = {
    'batch_size': int(os.getenv('BATCH_SIZE', 100)),
    'log_level': os.getenv('LOG_LEVEL', 'INFO')
}

"""
API data ingestion module - fetches product data from external API.
"""
import requests
import logging
from typing import List, Dict, Any
from time import sleep

from config import API_CONFIG
from models import ProductModel

logger = logging.getLogger(__name__)


class APIIngestion:
    """Handles data ingestion from external APIs."""
    
    def __init__(self):
        self.base_url = API_CONFIG['base_url']
        self.timeout = API_CONFIG['timeout']
        self.retry_attempts = API_CONFIG['retry_attempts']
        self.session = requests.Session()
    
    def fetch_products(self) -> List[Dict[str, Any]]:
        """
        Fetch all products from the API.
        
        Returns:
            List of validated product dictionaries
        """
        endpoint = f"{self.base_url}/products"
        
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Fetching products from API (attempt {attempt + 1})")
                response = self.session.get(endpoint, timeout=self.timeout)
                response.raise_for_status()
                
                raw_data = response.json()
                logger.info(f"Fetched {len(raw_data)} products from API")
                
                # Validate data
                validated_products = self._validate_products(raw_data)
                logger.info(f"Validated {len(validated_products)} products")
                
                return validated_products
                
            except requests.RequestException as e:
                logger.error(f"API request failed (attempt {attempt + 1}): {e}")
                if attempt < self.retry_attempts - 1:
                    sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
            except Exception as e:
                logger.error(f"Unexpected error during API fetch: {e}")
                raise
    
    def _validate_products(self, raw_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Validate product data using Pydantic models.
        
        Args:
            raw_data: Raw product data from API
            
        Returns:
            List of validated product dictionaries
        """
        validated = []
        errors = []
        
        for item in raw_data:
            try:
                product = ProductModel(**item)
                validated.append(product.model_dump())
            except Exception as e:
                errors.append({
                    'product_id': item.get('id', 'unknown'),
                    'error': str(e)
                })
                logger.warning(f"Validation failed for product {item.get('id')}: {e}")
        
        if errors:
            logger.warning(f"Failed to validate {len(errors)} products")
        
        return validated
    
    def fetch_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """
        Fetch a single product by ID.
        
        Args:
            product_id: Product identifier
            
        Returns:
            Validated product dictionary
        """
        endpoint = f"{self.base_url}/products/{product_id}"
        
        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            
            raw_data = response.json()
            product = ProductModel(**raw_data)
            
            return product.model_dump()
            
        except Exception as e:
            logger.error(f"Failed to fetch product {product_id}: {e}")
            raise


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    ingestion = APIIngestion()
    products = ingestion.fetch_products()
    print(f"Successfully fetched {len(products)} products")

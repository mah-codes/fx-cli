"""API module for fetching foreign exchange rates."""

import requests
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FXAPIError(Exception):
    """Custom exception for FX API errors."""
    pass


class FXAPI:
    """Foreign Exchange API client."""
    
    def __init__(self):
        self.api_key = os.getenv('FX_API_KEY')
        if not self.api_key:
            raise FXAPIError(
                "FX_API_KEY environment variable not set. "
                "Please set it in your .env file or environment."
            )
        self.base_url = "https://openexchangerates.org/api"
    
    def get_historical_rates(self, date: str) -> Dict[str, float]:
        """
        Get historical exchange rates for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary of currency codes to exchange rates
            
        Raises:
            FXAPIError: If API request fails
        """
        url = f"{self.base_url}/historical/{date}.json"
        params = {
            "app_id": self.api_key,
            "show_alternative": False,
            "prettyprint": False
        }
        headers = {"accept": "application/json"}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data:
                raise FXAPIError(f"API Error: {data.get('message', 'Unknown error')}")
            
            return data.get('rates', {})
            
        except requests.exceptions.RequestException as e:
            raise FXAPIError(f"Network error: {str(e)}")
        except KeyError as e:
            raise FXAPIError(f"Unexpected API response format: {str(e)}")
    
    def get_rate(self, date: str, currency: str) -> float:
        """
        Get exchange rate for a specific currency on a given date.
        
        Args:
            date: Date in YYYY-MM-DD format
            currency: 3-letter currency code (e.g., 'USD', 'BRL')
            
        Returns:
            Exchange rate relative to USD
            
        Raises:
            FXAPIError: If currency not found or API error
        """
        rates = self.get_historical_rates(date)
        
        if currency not in rates:
            raise FXAPIError(f"Currency '{currency}' not found in rates for {date}")
        
        return rates[currency]
    
    def convert_currency(self, date: str, from_currency: str, to_currency: str) -> float:
        """
        Convert between two currencies on a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate from source to target currency
            
        Raises:
            FXAPIError: If currencies not found or API error
        """
        rates = self.get_historical_rates(date)
        
        if from_currency not in rates:
            raise FXAPIError(f"Currency '{from_currency}' not found in rates for {date}")
        if to_currency not in rates:
            raise FXAPIError(f"Currency '{to_currency}' not found in rates for {date}")
        
        # Convert from source currency to USD, then to target currency
        from_rate = rates[from_currency]
        to_rate = rates[to_currency]
        
        return to_rate / from_rate
